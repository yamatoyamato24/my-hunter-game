import pygame
import asyncio

# --- 画像読み込み関数（縦横比を維持） ---
def load_game_image(path, target_width):
    try:
        img = pygame.image.load(path).convert_alpha()
        org_width, org_height = img.get_size()
        aspect_ratio = org_height / org_width
        target_height = int(target_width * aspect_ratio)
        return pygame.transform.scale(img, (target_width, target_height))
    except:
        surf = pygame.Surface((target_width, target_width))
        surf.fill((200, 200, 200))
        return surf

class Player:
    def __init__(self):
        self.image = load_game_image("assets/run_away.png", 60)
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
        # 画面の下端(1000)まで動けるように修正
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 1500))
        if self.invincible_timer > 0: self.invincible_timer -= 1

    def draw(self, screen):
        if self.invincible_timer % 10 < 5: 
            screen.blit(self.image, self.rect)

class Enemy:
    def __init__(self):
        self.image = load_game_image("assets/enemy.png", 300)
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
        try:
            self.image = pygame.image.load("assets/background.png").convert()
            # 縦長画面(800x1500)に合わせて拡大
            self.image = pygame.transform.scale(self.image, (800, 1500))
        except:
            self.image = pygame.Surface((800, 1500))
            self.image.fill((34, 139, 34))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Controller:
    def __init__(self):
        # 画面の下の方（y=1200あたり）に配置
        self.cx, self.cy = 400, 1200
        self.size = 110 # さらに大きく（押しやすさ重視）
        self.pad_radius = 220  #土台も大きく
        
        # 十字ボタン（上下左右）
        self.up_rect    = pygame.Rect(self.cx - self.size//2, self.cy - self.size*1.7, self.size, self.size)
        self.down_rect  = pygame.Rect(self.cx - self.size//2, self.cy + self.size*0.7, self.size, self.size)
        self.left_rect  = pygame.Rect(self.cx - self.size*1.7, self.cy - self.size//2, self.size, self.size)
        self.right_rect = pygame.Rect(self.cx + self.size*0.7, self.cy - self.size//2, self.size, self.size)

        # 【追加】ナナメ判定用のRect（大きな円に合わせて位置を調整）
        s_n = self.size * 0.9 
        offset = 130 # 中心からの距離
        self.ur_rect = pygame.Rect(self.cx + 20, self.cy - offset, s_n, s_n) # 右上
        self.ul_rect = pygame.Rect(self.cx - 130, self.cy - offset, s_n, s_n) # 左上
        self.dr_rect = pygame.Rect(self.cx + 20, self.cy + 30,  s_n, s_n) # 右下
        self.dl_rect = pygame.Rect(self.cx - 130, self.cy + 30,  s_n, s_n) # 左下

        # ★フォントの準備はここ（最初の一回だけ）で行う！
        self.font = pygame.font.SysFont(None, 70)

    def draw(self, screen):
        pad_surf = pygame.Surface((800, 1500), pygame.SRCALPHA)
        m_pos = pygame.mouse.get_pos()
        m_pressed = pygame.mouse.get_pressed()[0]

        # 1. 土台と外側の白いリング
        pygame.draw.circle(pad_surf, (40, 40, 40, 150), (self.cx, self.cy), self.pad_radius)
        pygame.draw.circle(pad_surf, (255, 255, 255, 200), (self.cx, self.cy), self.pad_radius, 4)

        buttons = [
            (self.up_rect, "▲", "U"), (self.down_rect, "▼", "D"),
            (self.left_rect, "◀", "L"), (self.right_rect, "▶", "R"),
            (self.ur_rect, "", "UR"), (self.ul_rect, "", "UL"),
            (self.dr_rect, "", "DR"), (self.dl_rect, "", "DL")
        ]

        for rect, arrow, tag in buttons:
            if m_pressed and rect.collidepoint(m_pos):
                color = (255, 255, 0, 180)
            else:
                color = (80, 80, 80, 100)
            
            if len(tag) == 1:
                pygame.draw.rect(pad_surf, color, rect, border_radius=15)
                pygame.draw.rect(pad_surf, (255, 255, 255, 150), rect, 2, border_radius=15)
            else:
                pygame.draw.rect(pad_surf, color, rect, border_radius=30)

            if arrow != "":
                txt = self.font.render(arrow, True, (255, 255, 255))
                pad_surf.blit(txt, txt.get_rect(center=rect.center))

        screen.blit(pad_surf, (0, 0))

    def get_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        res = {"up": False, "down": False, "left": False, "right": False}
        
        if mouse_pressed:
            # 配列のインデックス指定で計算（エラー防止）
            dx = mouse_pos[0] - self.cx
            dy = mouse_pos[1] - self.cy
            
            if dx**2 + dy**2 < self.pad_radius**2:
                limit = 10 
                if dy < -limit: res["up"] = True
                if dy > limit:  res["down"] = True
                if dx < -limit: res["left"] = True
                if dx > limit:  res["right"] = True
        return res
async def play_game(screen):
    # ★開始直後に一瞬だけ休ませる（ブラウザの読み込み待ち）
    await asyncio.sleep(0.1) 

    # --- ゲーム用BGMの再生 ---
    try:
        pygame.mixer.music.load("assets/game_bgm.ogg")
        pygame.mixer.music.play(-1)
    except:
        print("BGM再生エラー")

    # クラスの初期化
    bg = Background()
    # 背景を画面サイズに合わせる
    bg.image = pygame.transform.scale(bg.image, (800, 1500))
    bg.rect = bg.image.get_rect()
    
    player = Player()
    enemy = Enemy()
    controller = Controller()
    
    clock = pygame.time.Clock()
    score = 0
    font_ui = pygame.font.SysFont(None, 40)
    font_count = pygame.font.SysFont(None, 150)
    
    start_ticks = pygame.time.get_ticks()

    while True:
        # カウントダウン秒数の計算
        countdown = 3 - (pygame.time.get_ticks() - start_ticks) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", 0
        
        # 入力を受け取る
        ctrl = controller.get_input()

        # カウントダウン終了後のみ更新
        if countdown <= 0:
            if ctrl["up"]:    player.rect.y -= player.speed
            if ctrl["down"]:  player.rect.y += player.speed
            if ctrl["left"]:  player.rect.x -= player.speed
            if ctrl["right"]: player.rect.x += player.speed
            
            player.update()
            enemy.update(player.rect)
            score += 1 / 60 

        # 当たり判定（正確なマスク衝突）
        offset_x = enemy.rect.x - player.rect.x
        offset_y = enemy.rect.y - player.rect.y
        if player.mask.overlap(enemy.mask, (offset_x, offset_y)) and player.invincible_timer <= 0:
            player.hp -= 1
            player.invincible_timer = 60

            if player.hp <= 0:
                pygame.mixer.music.stop() # 音楽を止める
                await asyncio.sleep(0.5)  # 余韻
                return "GAMEOVER", int(score)

        # --- 描画処理 ---
        bg.draw(screen)
        player.draw(screen)
        enemy.draw(screen)

        # 十字キーを一番上に描画
        controller.draw(screen)
        
        # UI表示
        txt_ui = font_ui.render(f"LIFE:{player.hp} SCORE:{int(score)}", True, (255,255,255))
        screen.blit(txt_ui, (20,20))

        # カウントダウン演出（画面を暗く＋大きな数字）
        if countdown > 0:
            # 1500pxの画面全体を覆うように修正
            overlay = pygame.Surface((800, 1500), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            count_surf = font_count.render(str(countdown), True, (255, 215, 0))
            count_rect = count_surf.get_rect(center=(400, 500)) # 1000の真ん中(500)に
            screen.blit(count_surf, count_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
