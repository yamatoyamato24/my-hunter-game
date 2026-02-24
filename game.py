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
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 600))
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
        # 十字キーの基準位置（画面下部の中央など、縦長画面に合わせて調整してください）
        # x, y は十字キーの中心付近
        cx, cy = 400, 750  # 画面を縦長にしたとのことなので yを大きめに設定
        size = 60         # ボタン1つのサイズ

        # ケムコ風の十字配置 (Rectの作成)
        self.up_rect    = pygame.Rect(cx - size//2, cy - size*1.5, size, size)
        self.down_rect  = pygame.Rect(cx - size//2, cy + size//2,  size, size)
        self.left_rect  = pygame.Rect(cx - size*1.5, cy - size//2, size, size)
        self.right_rect = pygame.Rect(cx + size//2, cy - size//2,  size, size)
        
        # 中央部分（飾り、または決定ボタン用）
        self.center_rect = pygame.Rect(cx - size//2, cy - size//2, size, size)

    def draw(self, screen):
        # 十字キーの描画（レトロゲーム風に少し濃いめのグレー）
        color = (100, 100, 100, 150) # 半透明のグレー
        border = 3
        
        for r in [self.up_rect, self.down_rect, self.left_rect, self.right_rect, self.center_rect]:
            # ボタンの背景
            pygame.draw.rect(screen, color, r)
            # ボタンの枠線（白）
            pygame.draw.rect(screen, (255, 255, 255), r, border)

        # 矢印の記号を描画（簡易版）
        font = pygame.font.SysFont(None, 40)
        screen.blit(font.render("U", True, (255,255,255)), (self.up_rect.x+15, self.up_rect.y+10))
        screen.blit(font.render("D", True, (255,255,255)), (self.down_rect.x+15, self.down_rect.y+10))
        screen.blit(font.render("L", True, (255,255,255)), (self.left_rect.x+15, self.left_rect.y+10))
        screen.blit(font.render("R", True, (255,255,255)), (self.right_rect.x+15, self.right_rect.y+10))

    def get_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0] # 左クリック（タッチ）
        
        res = {"up": False, "down": False, "left": False, "right": False}
        
        if mouse_pressed:
            # 座標の差（中心からどれくらい離れているか）で判定する
            dx = mouse_pos[0] - 400 # cx 
            dy = mouse_pos[1] - 750 # cy

            # 中心からある程度の距離内を触っていたら
            if dx**2 + dy**2 < 150**2: # 半径150px以内
                if dy < -30: res["up"] = True    # 中心より30px以上上
                if dy > 30:  res["down"] = True  # 中心より30px以上下
                if dx < -30: res["left"] = True  # 中心より30px以上左
                if dx > 30:  res["right"] = True # 中心より30px以上右
        return res

async def play_game(screen):
    # --- 【追加】ゲーム用BGMの再生 ---
    try:
        pygame.mixer.music.load("assets/game_bgm.ogg")
        pygame.mixer.music.play(-1)  # 無限ループ
    except Exception as e:
        print(f"BGM再生エラー: {e}")

    bg, player, enemy, controller = Background(), Player(), Enemy(), Controller()
    
    # ① プレイヤーを小さく調整（クラス側の初期化でサイズ指定）
    player.image = load_game_image("assets/run_away.png", 60) # 幅60に
    player.rect = player.image.get_rect(center=(400, 300))
    player.mask = pygame.mask.from_surface(player.image)
    
    clock, score = pygame.time.Clock(), 0

    # ② カウントダウン用の大きなフォントを用意
    font_ui = pygame.font.SysFont(None, 36)
    font_count = pygame.font.SysFont(None, 150) # サイズ150！

    start_ticks = pygame.time.get_ticks()

    while True:
        # カウントダウン数秒の計算
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        countdown = 3 - seconds_passed

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
