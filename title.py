import pygame
import asyncio
import math

async def show_title(screen):
    font = pygame.font.SysFont(None, 50)
    clock = pygame.time.Clock()
    while True:
        screen.fill((136, 136, 136))
        alpha = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
        if alpha > 0.3:
            txt = font.render("CLICK OR SPACE TO START", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=(400, 300)))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: return "PLAY"
            if event.type == pygame.MOUSEBUTTONDOWN: return "PLAY"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
