import pygame
import asyncio
import math

async def show_title(screen):
    # 音楽の準備（ループの直前に入れる）
    try:
        pygame.mixer.music.load("assets/title_bgm.ogg")
        pygame.mixer.music.play(-1) # -1は無限ループ
    except:
        print("Music load error")

    try:
        font_main = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 40)
        font_sub = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 25)
    except:
        # もし読み込みに失敗した時のためのバックアップ
        font_main = pygame.font.SysFont(None, 40)
        font_sub = pygame.font.SysFont(None, 25)

    clock = pygame.time.Clock()
    while True:
        screen.fill((136, 136, 136))
        alpha = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
        
        text_sub = font_sub.render("かいぶつから逃げ切れ！", True, (220, 220, 220))
        screen.blit(text_sub, text_sub.get_rect(center=(400, 360)))
        
        # ここから下は if の中（右側にスペースを入れる）にする
        if alpha > 0.3:
            txt_main = font_main.render("スペースキーでスタート", True, (255, 255, 255))
            screen.blit(txt_main, txt_main.get_rect(center=(400, 300)))
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: return "PLAY"
            if event.type == pygame.MOUSEBUTTONDOWN: return "PLAY"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
