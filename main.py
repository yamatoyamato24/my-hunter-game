import pygame
import asyncio
import game
import title
import gameover

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("My HUNTER Game")

    state = "TITLE"
    last_score = 0

    while state != "QUIT":
        if state == "TITLE":
            state = await title.show_title(screen)
        elif state == "PLAY":
            state, last_score = await game.play_game(screen)
        elif state == "GAMEOVER":
            state = await gameover.show_gameover(screen, last_score)
        
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
