import pygame, pymunk

pygame.init()

screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()

space = pymunk.Space() # initialized the space in which the physics sim occurs

while True:
    # Process player inputs.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    # Do logical updates here.
    # ...

    screen.fill("purple")  # Fill the display with a solid color

    # Render the graphics here.
    # ...

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60) # wait until next frame (at 60 FPS)
    space.step(1/60) # running the simulation