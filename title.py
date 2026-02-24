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

    # ループ開始
    while True:
        screen.fill((136, 136, 136))
        alpha = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2 #点滅の計算
        
        #サブタイトル表示
        text_sub = font_sub.render("かいぶつから逃げ切れ！", True, (220, 220, 220))
        screen.blit(text_sub, text_sub.get_rect(center=(400, 360)))
        
        # メインタイトル点滅表示
        if alpha > 0.3:
            txt_main = font_main.render("スペースキーでスタート", True, (255, 255, 255))
            screen.blit(txt_main, txt_main.get_rect(center=(400, 500)))
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            # スペースキーかクリックで""PLAY"を返して終了
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
                (event.type == pygame.MOUSEBUTTONDOWN):
            
                pygame.mixer.music.stop() # 音楽を止める処理
                await asyncio.sleep(0.01) # ★ここ！一瞬だけ(0.01秒)待つ
                return "PLAY"
            
        # --- ここから下は while ループを維持するための必須処理 ---
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0) 
