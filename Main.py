import pygame, pymunk, math
from pymunk import Vec2d
from pymunk.vec2d import Vec2d

pygame.init()

screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
pygame.font.init()  # you have to call this at the start,
# if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)

count = 0
player_1 = 0
player_2 = 1

# load images

test_ball_image = pygame.image.load("ball_16.png")
ball_images = []
for i in range(1, 17):
    ball_image = pygame.image.load(f"ball_{i}.png").convert_alpha()
    ball_images.append(ball_image)


space = pymunk.Space() # initialized the space in which the physics sim occurs
space.damping = .5
ball_list = []

COLLISION_TYPE_BALL = 1
COLLISION_TYPE_POCKET = 2

def create_ball(space, position, radius):
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, radius))
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.95
    shape.damping = 0.5  # Increasing damping for more noticeable effect
    space.add(body, shape)
    shape.collision_type = COLLISION_TYPE_BALL
    return body

segment_body_bottom = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_bottom, (75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 100), 5)
segment_shape.elasticity = 0.85
space.add(segment_body_bottom, segment_shape)

segment_body_right = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_right, (screen.get_width() - 75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 600), 5)
segment_shape.elasticity = 0.85
space.add(segment_body_right, segment_shape)

segment_body_top = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_top, (screen.get_width() - 75, screen.get_height() - 600), (75, screen.get_height() - 600), 5)
segment_shape.elasticity = 0.85
space.add(segment_body_top, segment_shape)

segment_body_left = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body_left, (75, screen.get_height() - 600), (75, screen.get_height() - 100), 5)
segment_shape.elasticity = 0.85
space.add(segment_body_left, segment_shape)

test_ball = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 18))
test_ball.position = (200, (((2*screen.get_height()) - 700)/2))
test_shape = pymunk.Circle(test_ball, 18)
test_shape.elasticity = 0.95
test_shape.friction = 0.85  # Adding friction to the shape
test_shape.damping = 0.5  # Increasing damping for more noticeable effect
space.add(test_ball, test_shape)

# Cue stick properties
cue_length = 300
cue_angle = 0
pull_back_distance = 0
is_pulling_back = False

# Create pockets
pocket_radius = 30
pocket_positions = [
    (75, screen.get_height() - 100),  # Bottom left
    (screen.get_width() - 75, screen.get_height() - 100),  # Bottom right
    (75, screen.get_height() - 600),  # Top left
    (screen.get_width() - 75, screen.get_height() - 600),  # Top right
    (screen.get_width() / 2, screen.get_height() - 600),  # Center top
    (screen.get_width() / 2, screen.get_height() - 100)  # Bottom middle
]

pockets = []
for position in pocket_positions:
    pocket_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    pocket_shape = pymunk.Circle(pocket_body, pocket_radius)
    pocket_shape.elasticity = 0.0  # Pockets should not bounce
    pocket_shape.sensor = True  # Use as a sensor
    pocket_body.position = position
    pocket_shape.collision_type = COLLISION_TYPE_POCKET
    space.add(pocket_body, pocket_shape)
    pockets.append(pocket_shape)

rows = 5
radius = 18

# Create balls in a triangular formation
for row in range(rows):
    for col in range(row + 1):
        # Calculate the position of each ball
        x = row * (radius * 2) + 900  # Positioning vertically (now horizontal)
        y = (col - row / 2) * (radius * 2) + (((2*screen.get_height()) - 700)/2)  # Centering the triangle vertically
        ball_list.append(create_ball(space, (x, y), radius))


def convert_coordinates(point): # converting pygame coordinates to pymunk coordinates (pymunk coordinates put the origin in the bottom left corner
    return point[0], screen.get_height() - point[1]


class Ball(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y)

class Text():
    def __init__(self, words):
        text_surface = my_font.render(words, False, (0, 0, 0))
        screen.blit(text_surface, (20, 0))



# Define a collision handler
def collision_handler(arbiter, space, data):
    # Get the bodies involved in the collision
    body1, body2 = arbiter.shapes[0].body, arbiter.shapes[1].body

    # Remove the body from the space
    space.remove(body1, arbiter.shapes[0])  # Remove the first body and its shape

    return True  # Return True to keep the collision from being resolved


# Set up the collision handler in the space
handler = space.add_collision_handler(COLLISION_TYPE_BALL, COLLISION_TYPE_POCKET)
handler.begin = collision_handler

while True:

    # Process player inputs.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if test_ball.velocity.x < 1 and test_ball.velocity.y < 1:
                    is_pulling_back = True
                    pull_back_distance = 0  # Reset the pullback distance
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if test_ball.velocity.x < 1 and test_ball.velocity.y < 1:
                    # Calculate the force to apply based on the pullback distance
                    direction = test_ball.position - (pygame.mouse.get_pos())
                    direction = direction.normalized()
                    force_magnitude = pull_back_distance * 100  # Adjust the multiplier as needed
                    force_vector = direction*force_magnitude #-Vec2d(math.cos(cue_angle), math.sin(cue_angle)) * force_magnitude
                    # test_ball.apply_impulse_at_local_point(force_vector, (0, 0))
                    test_ball.apply_impulse_at_world_point(force_vector, (0, 0))
                    is_pulling_back = False
                    force_vector = 0
                    count += 1



    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pos = Vec2d(mouse_x, mouse_y)
    ball_pos = test_ball.position
    cue_angle = math.atan2(mouse_y - (screen.get_height() - ball_pos.y), mouse_x - ball_pos.x)

    if is_pulling_back and pull_back_distance <= 15:
        pull_back_distance += 1  # Increment pull back distance while the key is held down


    # Do logical updates here.
    # ...

    player_up = count % 2


    screen.fill("white")  # Fill the display with a solid color
    if player_up == player_1:
        text1 = Text("Player 1's turn!")
    elif player_up == player_2:
        text2 = Text("Player 2's turn!")

    # Render the graphics here.
    # ...

    pygame.draw.rect(screen, 'forest Green', (75, screen.get_height() - 600, 1130, 500))

    pygame.draw.line(screen, 'black', (75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 100), 5 )
    pygame.draw.line(screen, 'black', (screen.get_width() - 75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 600), 5 )
    pygame.draw.line(screen, 'black', (screen.get_width() - 75, screen.get_height() - 600), (75, screen.get_height() - 600), 5 )
    pygame.draw.line(screen, 'black', (75, screen.get_height() - 600), (75, screen.get_height() - 100), 5 )

    count_one = 0

    # for shape in space.shapes:
    #     position = shape.body.position
    #     pygame.draw.circle(screen, (0, 0, 0), (int(position.x), int(position.y)), radius)
    #     if count_one == 17:
    #         screen.blit(ball_images[count_one], (int(position.x), int(position.y)))
    #         count_one += 1

    # Draw balls with images
    for i, shape in enumerate(space.shapes):
        position = shape.body.position
        # Draw the circle for visual reference (optional)
        pygame.draw.circle(screen, (0, 0, 0), (int(position.x), int(position.y)), radius)

        # Blit the corresponding ball image if available
        if i < len(ball_images):  # Ensure the image exists for this ball
            screen.blit(ball_images[i], (int(position.x) - radius, int(position.y) - radius))


    # Draw pockets
    for pocket in pockets:
        position = pocket.body.position
        pygame.draw.circle(screen, (100, 100, 100), (int(position.x), int(position.y)), pocket_radius)


    pygame.draw.circle(screen, (0, 0, 255), (int(test_ball.position.x), int(test_ball.position.y)), 18)
    screen.blit(test_ball_image, (test_ball.position.x - 18, test_ball.position.y - 18))

        # Check if the test ball is not moving
    if test_ball.velocity.length < 1:  # Check if the speed is less than 1
        # Draw the cue stick
        cue_start = (ball_pos.x, ball_pos.y)
        cue_vector = ball_pos - pygame.mouse.get_pos()
        cue_vector = cue_vector.normalized()
        cue_end = cue_start + -cue_vector * cue_length#(ball_pos.x + cue_length * math.cos(cue_angle),
                   #    ball_pos.y + cue_length * math.sin(cue_angle))
        pygame.draw.line(screen, 'black', cue_start, cue_end, 10)

        pygame.draw.line(screen, 'black', cue_start, cue_end, 10)




    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60) # wait until next frame (at 60 FPS)
    space.step(1/60) # running the simulation