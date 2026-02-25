import pygame
import asyncio
import game
import title
import gameover

async def main():
    pygame.init()
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
            state = await gameover.show_gameover(screen, last_score)
        
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
