import pygame
import asyncio

def load_game_image(path, target_width): # 幅だけ指定するように変更
    try:
        img = pygame.image.load(path).convert_alpha()
        # 元の画像のサイズを取得
        org_width, org_height = img.get_size()
        # 指定した「幅」に合わせて「高さ」を計算（比率を維持）
        aspect_ratio = org_height / org_width
        target_height = int(target_width * aspect_ratio)

        return pygame.transform.scale(img, (target_width, target_height))
    except:
        surf = pygame.Surface((target_width, target_width)) # 失敗時は正方形
        surf.fill((200, 200, 200))
        return surf

class Player:
    def __init__(self):
        self.image = load_game_image("assets/run_away.png", (100, 100))
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
        self.image = load_game_image("assets/enemy.png", (300, 300))
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
        self.image = load_game_image("assets/background.png", (800, 600))
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
    clock, score = pygame.time.Clock(), 0
    font = pygame.font.SysFont(None, 36)
    start_ticks = pygame.time.get_ticks()

    while True:
        countdown = 3 - (pygame.time.get_ticks() - start_ticks) // 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", 0
        
        ctrl = controller.get_input()
        if countdown <= 0:
            if ctrl["up"]: player.rect.y -= player.speed
            if ctrl["down"]: player.rect.y += player.speed
            if ctrl["left"]: player.rect.x -= player.speed
            if ctrl["right"]: player.rect.x += player.speed
            player.update(); enemy.update(player.rect)
            score += 1 / 60 

        if player.mask.overlap(enemy.mask, (enemy.rect.x - player.rect.x, enemy.rect.y - player.rect.y)) and player.invincible_timer <= 0:
            player.hp -= 1
            player.invincible_timer = 60
            if player.hp <= 0: return "GAMEOVER", int(score)

        bg.draw(screen); player.draw(screen); enemy.draw(screen); controller.draw(screen)
        screen.blit(font.render(f"LIFE:{player.hp} SCORE:{int(score)}", True, (255,255,255)), (20,20))
        if countdown > 0:
            screen.blit(font.render(str(countdown), True, (255,215,0)), (400,300))
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
