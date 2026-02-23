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
        self.up_rect = pygame.Rect(700, 450, 50, 50)
        self.down_rect = pygame.Rect(700, 530, 50, 50)
        self.left_rect = pygame.Rect(640, 490, 50, 50)
        self.right_rect = pygame.Rect(760, 490, 50, 50)

    def draw(self, screen):
        for r in [self.up_rect, self.down_rect, self.left_rect, self.right_rect]:
            pygame.draw.rect(screen, (255, 255, 255, 100), r, 2)

    def get_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        res = {"up": False, "down": False, "left": False, "right": False}
        if mouse_pressed:
            if self.up_rect.collidepoint(mouse_pos): res["up"] = True
            if self.down_rect.collidepoint(mouse_pos): res["down"] = True
            if self.left_rect.collidepoint(mouse_pos): res["left"] = True
            if self.right_rect.collidepoint(mouse_pos): res["right"] = True
        return res

async def play_game(screen):
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
                #ゲームオーバー画面へ切り替え
                await asyncio.sleep(0.3) #少し余韻を残す
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
