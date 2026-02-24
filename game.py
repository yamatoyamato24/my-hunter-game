import pygame
import asyncio

# --- 画像読み込み関数（縦横比を維持） ---
def load_game_image(path, target_width):
    try:
        img = pygame.image.load(path).convert_alpha()
        org_width, org_height = img.get_size()
        # 比率を計算して高さを自動調整
        aspect_ratio = org_height / org_width
        target_height = int(target_width * aspect_ratio)
        return pygame.transform.scale(img, (target_width, target_height))
    except:
        # 読み込めない時の代わり
        surf = pygame.Surface((target_width, target_width))
        surf.fill((200, 200, 200))
        return surf

class Player:
    def __init__(self):
        self.image = load_game_image("assets/run_away.png", 60) # 幅60で固定
        self.rect = self.image.get_rect(center=(400, 300))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 5
        self.hp = 3
        self.invincible_timer = 0 

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:    self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:  self.rect.y += self.speed
        if keys[pygame.K_LEFT]:  self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 1000))
        if self.invincible_timer > 0: self.invincible_timer -= 1

    def draw(self, screen):
        if self.invincible_timer % 10 < 5: 
            screen.blit(self.image, self.rect)

class Enemy:
    def __init__(self):
        self.image = load_game_image("assets/enemy.png", 300) # 幅300で固定
        self.rect = self.image.get_rect(topleft=(20, 20))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 2

    def update(self, player_rect):
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        if self.rect.y < player_rect.y: self.rect.y += self.speed
        if self.rect.y > player_rect.y: self.rect.y -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Background:
    def __init__(self):
        # 背景は画面いっぱいに広げる
        try:
            self.image = pygame.image.load("assets/background.png").convert()
            self.image = pygame.transform.scale(self.image, (800, 600))
        except:
            self.image = pygame.Surface((800, 600))
            self.image.fill((34, 139, 34))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Controller:
    def __init__(self):
        self.cx, self.cy = 400, 800 
        self.size = 90
        self.pad_radius = 180 
        
        # 十字ボタン（上下左右）
        self.up_rect    = pygame.Rect(self.cx - self.size//2, self.cy - self.size*1.6, self.size, self.size)
        self.down_rect  = pygame.Rect(self.cx - self.size//2, self.cy + self.size*0.6, self.size, self.size)
        self.left_rect  = pygame.Rect(self.cx - self.size*1.6, self.cy - self.size//2, self.size, self.size)
        self.right_rect = pygame.Rect(self.cx + self.size*0.6, self.cy - self.size//2, self.size, self.size)

        # 【追加】ナナメ判定用のRect（ボタンの隙間を埋める）
        s_n = self.size * 0.9 # ナナメボタンのサイズ
        # 中心からの距離を微調整して、大きな円にフィットさせます
        offset = self.size * 0.6
        self.ur_rect = pygame.Rect(self.cx + 20, self.cy - 110, s_n, s_n) # 右上
        self.ul_rect = pygame.Rect(self.cx - 90, self.cy - 110, s_n, s_n) # 左上
        self.dr_rect = pygame.Rect(self.cx + 20, self.cy + 40,  s_n, s_n) # 右下
        self.dl_rect = pygame.Rect(self.cx - 90, self.cy + 40,  s_n, s_n) # 左下

    def draw(self, screen):
        pad_surf = pygame.Surface((800, 1000), pygame.SRCALPHA)
        m_pos = pygame.mouse.get_pos()
        m_pressed = pygame.mouse.get_pressed()[0] # 左クリック/タッチ

        # 1. 土台と外側の白いリング
        pygame.draw.circle(pad_surf, (40, 40, 40, 150), (self.cx, self.cy), self.pad_radius)
        pygame.draw.circle(pad_surf, (255, 255, 255, 200), (self.cx, self.cy), self.pad_radius, 3)

        # 2. 全ての判定エリア（8方向）をリスト化
        # (判定エリア, 表示する文字, 役割)
        buttons = [
            (self.up_rect, "▲", "U"), (self.down_rect, "▼", "D"),
            (self.left_rect, "◀", "L"), (self.right_rect, "R"),
            (self.ur_rect, "", "UR"), (self.ul_rect, "", "UL"),
            (self.dr_rect, "", "DR"), (self.dl_rect, "", "DL")
        ]

        for rect, arrow, tag in buttons:
            # マウスが重なっていて、かつ押されているなら光らせる
            if m_pressed and rect.collidepoint(m_pos):
                color = (255, 255, 0, 180) # 押したときは黄色
            else:
                color = (80, 80, 80, 100) # 通常時は控えめなグレー
            
            # ナナメのボタンは「枠線なし」にすると、十字キーが浮き立って綺麗に見えます
            if len(tag) == 1: # 上下左右
                pygame.draw.rect(pad_surf, color, rect, border_radius=10)
                pygame.draw.rect(pad_surf, (255, 255, 255, 150), rect, 2, border_radius=10)
            else: # ナナメ
                # ナナメ部分は「角丸の塗りつぶし」だけで表現
                pygame.draw.rect(pad_surf, color, rect, border_radius=20)

            # 矢印テキスト（上下左右のみ）
            if arrow != "":
                font = pygame.font.SysFont(None, 50)
                txt = font.render(arrow, True, (255, 255, 255))
                pad_surf.blit(txt, txt.get_rect(center=rect.center))

        screen.blit(pad_surf, (0, 0))

    def get_input(self):
        # ナナメ移動の判定ロジック
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        res = {"up": False, "down": False, "left": False, "right": False}
        
        if mouse_pressed:
            dx = mouse_pos[0] - self.cx
            dy = mouse_pos[1] - self.cy
            
            if dx**2 + dy**2 < self.pad_radius**2:
                # 判定をしきい値（30）で分けることで、ナナメ入力をスムーズに
                # 判定の感度を調整（中心付近の「遊び」を少し広げる）
                limit = 40 
                if dy < -limit: res["up"] = True
                if dy > limit:  res["down"] = True
                if dx < -limit: res["left"] = True
                if dx > limit:  res["right"] = True
        return res

async def play_game(screen):
    font_count = pygame.font.SysFont(None, 150)
    # --- 【追加】ゲーム用BGMの再生 ---
    try:
        pygame.mixer.music.load("assets/game_bgm.ogg")
        pygame.mixer.music.play(-1)  # 無限ループ
    except Exception as e:
        print(f"BGM再生エラー: {e}")

    # 背景を 800x1000 に拡大して準備
    bg = Background()
    bg.image = pygame.transform.scale(bg.image, (800, 1000))
    bg.rect = bg.image.get_rect()
    player, enemy, controller = Player(), Enemy(), Controller()
    clock, score = pygame.time.Clock(), 0
    font_ui = pygame.font.SysFont(None, 40)
    font_count = pygame.font.SysFont(None, 150) # ← この1行があるか確認してください！
    start_ticks = pygame.time.get_ticks()

    while True:
        # カウントダウン数秒の計算
        countdown = 3 - (pygame.time.get_ticks() - start_ticks) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", 0
        
        ctrl = controller.get_input()

        # カウントダウン終了後のみ動かす
        if countdown <= 0:
            if ctrl["up"]: player.rect.y -= player.speed
            if ctrl["down"]: player.rect.y += player.speed
            if ctrl["left"]: player.rect.x -= player.speed
            if ctrl["right"]: player.rect.x += player.speed
            player.update()
            enemy.update(player.rect)
            score += 1 / 60 

        # マスク判定（ズレの計算を修正して正確に）
        if player.mask.overlap(enemy.mask, (enemy.rect.x - player.rect.x, enemy.rect.y - player.rect.y)) and player.invincible_timer <= 0:
            player.hp -= 1
            player.invincible_timer = 60

            # HPがなくなったら GAMEOVER という言葉を main.py に返す
            if player.hp <= 0:
                pygame.mixer.music.stop() # ★ゲームのBGMをここで一度止める！
                #ゲームオーバー画面へ切り替え
                await asyncio.sleep(0.5) #少し余韻を残す
                return "GAMEOVER", int(score)

        # --- 描画処理 ---
        bg.draw(screen)
        player.draw(screen)
        enemy.draw(screen)

        # 十字キーを「ゲーム画面の上」に重ねて描画
        controller.draw(screen)
        
        # UI表示
        txt_ui = font_ui.render(f"LIFE:{player.hp} SCORE:{int(score)}", True, (255,255,255))
        screen.blit(txt_ui, (20,20))

        # カウントダウン中は画面を暗くし、大きな数字を出す
        if countdown > 0:
            # 画面全体を覆う半透明の黒いシート
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # (赤, 緑, 青, 透明度0-255)
            screen.blit(overlay, (0, 0))

            # 大きな数字を描画
            count_surf = font_count.render(str(countdown), True, (255, 215, 0)) # 金色
            count_rect = count_surf.get_rect(center=(400, 300))
            screen.blit(count_surf, count_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
