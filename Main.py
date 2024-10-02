import pygame, pymunk, math
from pymunk.vec2d import Vec2d

pygame.init()

screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()

space = pymunk.Space() # initialized the space in which the physics sim occurs
space.damping = .8

def create_ball(space, position, radius):
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, radius))
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.95
    shape.friction = 0.85  # Adding friction to the shape
    shape.damping = 0.5  # Increasing damping for more noticeable effect
    space.add(body, shape)
    return body

segment_body_bottom = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_bottom, (75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 100), 5)
segment_shape.elasticity = 0.85
segment_shape.friction = 0.9
space.add(segment_body_bottom, segment_shape)

segment_body_right = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_right, (screen.get_width() - 75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 600), 5)
segment_shape.elasticity = 0.85
segment_shape.friction = 0.9
space.add(segment_body_right, segment_shape)

segment_body_top = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_top, (screen.get_width() - 75, screen.get_height() - 600), (75, screen.get_height() - 600), 5)
segment_shape.elasticity = 0.85
segment_shape.friction = 0.9
space.add(segment_body_top, segment_shape)

segment_body_left = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_left, (75, screen.get_height() - 600), (75, screen.get_height() - 100), 5)
segment_shape.elasticity = 0.85
segment_shape.friction = 0.9
space.add(segment_body_left, segment_shape)

test_ball = create_ball(space, (200, (((2*screen.get_height()) - 700)/2)), 10)
test_ball.velocity = (600, 0)

# Cue stick properties
cue_length = 100
cue_angle = 0

rows = 5
radius = 10

# Create balls in a triangular formation
for row in range(rows):
    for col in range(row + 1):
        # Calculate the position of each ball
        x = row * (radius * 2) + 900  # Positioning vertically (now horizontal)
        y = (col - row / 2) * (radius * 2) + (((2*screen.get_height()) - 700)/2)  # Centering the triangle vertically
        create_ball(space, (x, y), radius)


def convert_coordinates(point): # converting pygame coordinates to pymunk coordinates (pymunk coordinates put the origin in the bottom left corner
    return point[0], screen.get_height() - point[1]


class Ball(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y)


while True:
    # Process player inputs.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    # Do logical updates here.
    # ...

        # Update cue stick angle based on mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    ball_pos = test_ball.position
    angle = math.atan2(mouse_y - (screen.get_height() - ball_pos.y), mouse_x - ball_pos.x)
    cue_angle = angle

    screen.fill("white")  # Fill the display with a solid color

    # Render the graphics here.
    # ...


    pygame.draw.line(screen, 'black', (75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 100), 5 )
    pygame.draw.line(screen, 'black', (screen.get_width() - 75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 600), 5 )
    pygame.draw.line(screen, 'black', (screen.get_width() - 75, screen.get_height() - 600), (75, screen.get_height() - 600), 5 )
    pygame.draw.line(screen, 'black', (75, screen.get_height() - 600), (75, screen.get_height() - 100), 5 )

    for shape in space.shapes:
        position = shape.body.position
        pygame.draw.circle(screen, (0, 0, 255), (int(position.x), int(position.y)), radius)

        # Check if the test ball is not moving
    if test_ball.velocity.length < 1:  # Check if the speed is less than 1
        # Draw the cue stick
        cue_start = (ball_pos.x, ball_pos.y)
        cue_end = (ball_pos.x + cue_length * math.cos(cue_angle),
                       ball_pos.y + cue_length * math.sin(cue_angle))
        pygame.draw.line(screen, 'black', cue_start, cue_end, 5)

        pygame.draw.line(screen, 'black', cue_start, cue_end, 5)
    # In your main loop, apply friction to each ball
    # for shape in space.shapes:
    #     if isinstance(shape, pymunk.Circle):  # Assuming your balls are Circles
    #         apply_friction(shape.body)


    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60) # wait until next frame (at 60 FPS)
    space.step(1/60) # running the simulation