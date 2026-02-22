import pygame
import asyncio
import ranking

async def show_gameover(screen, score):
    best_five = ranking.update_ranking(score)
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()
    while True:
        screen.fill((50, 0, 0))
        screen.blit(font.render("GAME OVER", True, (255,0,0)), (300, 100))
        screen.blit(font.render(f"SCORE: {score}s", True, (255,255,255)), (300, 160))
        
        for i, s in enumerate(best_five):
            txt = font.render(f"{i+1}: {s}s", True, (255, 255, 255))
            screen.blit(txt, (320, 220 + i * 40))
        
        screen.blit(font.render("CLICK TO TITLE", True, (200,200,200)), (300, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return "TITLE"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
