import pygame
import asyncio
import ranking

# 引数に is_clear を追加
async def show_gameover(screen, score, is_clear=False):
    # 少しだけ入力を受け付けない時間を作る
    await asyncio.sleep(0.5)
    
    # 音楽の再生（クリア時と失敗時で分けるとおしゃれです）
    try:
        if is_clear:
            pygame.mixer.music.load("assets/clear_bgm.ogg") # クリア用BGM（あれば）
        else:
            pygame.mixer.music.load("assets/gameover_bgm.ogg")
        pygame.mixer.music.play(-1)
    except:
        pass

    best_five = ranking.update_ranking(score)
    clock = pygame.time.Clock()

    # フォント読み込み
    try:
        font_main = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 60)
        font_sub = pygame.font.Font("assets/NotoSansJP-Regular.ttf", 30)
    except:
        font_main = pygame.font.SysFont(None, 60)
        font_sub = pygame.font.SysFont(None, 30)    

    while True:
        screen.fill((0, 0, 0)) 

        # --- # 2. 文字を描画（ここを修正！） ---
        if is_clear:
            # クリア時の表示（金色）
            text_title = font_main.render("★ ゲームクリア！ ★", True, (255, 215, 0))
        else:
            # 失敗時の表示（赤色）
            text_title = font_main.render("ゲームオーバー", True, (255, 0, 0))
        
        # 中央寄せで表示
        rect_title = text_title.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(text_title, rect_title)

        # スコア表示
        score_txt = font_sub.render(f"今回のスコア: {score}秒", True, (255, 255, 255))
        screen.blit(score_txt, score_txt.get_rect(center=(screen.get_width() // 2, 280)))
        # ---------------------------------------

        # ランキング表示
        rank_title = font_sub.render("★ ベスト5 ★", True, (255, 215, 0))
        screen.blit(rank_title, (320, 380))
        
        for i, s in enumerate(best_five):
            txt = font_sub.render(f"{i+1}位: {s}秒", True, (255, 255, 255))
            screen.blit(txt, (320, 440 + i * 45))
        
        screen.blit(font_sub.render("クリックでタイトルへ", True, (200, 200, 200)), (260, 750))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                pygame.mixer.music.stop() 
                return "TITLE"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
