import pygame
import asyncio
import ranking

async def show_gameover(screen, score):
    # 悲しい音楽の再生
    try:
        pygame.mixer.music.load("assets/gameover_bgm.ogg")
        pygame.mixer.music.play(-1)
    except:
        pass

    best_five = ranking.update_ranking(score)
    clock = pygame.time.Clock()

    # フォント読み込み
    try:
        font_main = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 60) # 少し大きく
        font_sub = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 30)
    except:
        font_main = pygame.font.SysFont(None, 60)
        font_sub = pygame.font.SysFont(None, 30)    

    while True:
        # 1. 画面を真っ黒に塗りつぶす（これで前のゲーム画面が消えます）
        screen.fill((0, 0, 0)) 

        # 2. 文字を描画（y座標を少し下げて、1000ピクセルの画面で見やすく調整）
        screen.blit(font_main.render("ゲームオーバー", True, (255, 0, 0)), (230, 200))
        screen.blit(font_sub.render(f"今回のスコア: {score}秒", True, (255, 255, 255)), (280, 280))
        
        # ランキング表示
        rank_title = font_sub.render("★ ベスト5 ★", True, (255, 215, 0))
        screen.blit(rank_title, (320, 380))
        
        for i, s in enumerate(best_five):
            txt = font_sub.render(f"{i+1}位: {s}秒", True, (255, 255, 255))
            screen.blit(txt, (320, 440 + i * 45))
        
        # 戻るボタンの案内
        screen.blit(font_sub.render("クリックでタイトルへ", True, (200, 200, 200)), (260, 750))

        # 3. イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                pygame.mixer.music.stop() # タイトルに戻る前に音楽を止める
                return "TITLE"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

