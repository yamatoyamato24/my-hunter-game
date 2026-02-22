import pygame
import asyncio
import ranking

async def show_gameover(screen, score):

    # 悲しい音楽の再生（ループ直前）
    try:
        pygame.mixer.music.load("assets/gameover_bgm.ogg")
        pygame.mixer.music.play(-1)
    except:
        pass

    best_five = ranking.update_ranking(score)
    clock = pygame.time.Clock()

    try:
        font_main = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 40)
        font_sub = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 25)
    except:
        # もし読み込みに失敗した時のためのバックアップ
        font_main = pygame.font.SysFont(None, 40)
        font_sub = pygame.font.SysFont(None, 25)    

    while True:
        screen.blit(font_main.render("ゲームオーバー", True, (255,0,0)), (300, 100))
        screen.blit(font_sub.render(f"スコア: {score}秒", True, (255,255,255)), (300, 160))
        
        for i, s in enumerate(best_five):
            txt = font_sub.render(f"{i+1}位: {s}秒", True, (255, 255, 255))
            screen.blit(txt, (320, 220 + i * 40))
        
        screen.blit(font_sub.render("クリックでタイトルへ", True, (200,200,200)), (300, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return "TITLE"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
