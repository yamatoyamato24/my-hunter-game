import pygame
import asyncio
import game
import title
import gameover

async def main():
    pygame.init()
    # スマホのブラウザで見やすいサイズに調整
    screen = pygame.display.set_mode((800, 1500))
    pygame.display.set_caption("My HUNTER Game")

    state = "TITLE"
    last_score = 0

    while state != "QUIT":
        if state == "TITLE":
            # ここで受け取った state が "PLAY" になる必要がある
            state = await title.show_title(screen)
            print(f"タイトルから戻ってきた値は: {state}") # ★これを追加
        elif state == "PLAY":  # ← ここが "PLAY" と一致しているか！
            state, last_score = await game.play_game(screen)
        elif state == "GAMEOVER":
        # 失敗なので is_clear=False
            state = await gameover.show_gameover(screen, last_score, is_clear=False)
        # ★【追加】クリアした時の処理
        elif state == "CLEAR":
            # クリアなので is_clear=True
            state = await gameover.show_gameover(screen, last_score, is_clear=True)

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
