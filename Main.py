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

# Adding collision shapes for the table
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

# Collision shapes for the pockets
pocket_positions = [
    (75, screen.get_height() - 100),  # Bottom left corner
    (screen.get_width() - 75, screen.get_height() - 100),  # Bottom right corner
    (75, screen.get_height() - 600),  # Top left corner
    (screen.get_width() - 75, screen.get_height() - 600),  # Top right corner
    (screen.get_width() // 2, screen.get_height() - 100),  # Bottom middle
    (screen.get_width() // 2, screen.get_height() - 600)   # Top middle
]

test_ball = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 18))
test_ball.position = (200, (((2*screen.get_height()) - 700)/2))
test_shape = pymunk.Circle(test_ball, 20)
test_shape.elasticity = 0.95
test_shape.friction = 0.85  # Adding friction to the shape
test_shape.damping = 0.5  # Increasing damping for more noticeable effect
space.add(test_ball, test_shape)

def create_pocket(space, position, radius):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)  # Pockets are static
    shape = pymunk.Circle(body, radius)
    shape.position = position
    shape.elasticity = 0.0  # Pockets don't bounce
    shape.friction = 0.0
    space.add(body, shape)
    return shape

# # Create pockets in the physics space
# pocket_radius = 0  # Adjust as necessary
# pockets = [create_pocket(space, pos, pocket_radius) for pos in pocket_positions]

# Cue stick properties
cue_length = 300
cue_angle = 0
pull_back_distance = 0
is_pulling_back = False

rows = 5
radius = 20

# Create balls in a triangular formation
for row in range(rows):
    for col in range(row + 1):
        # Calculate the position of each ball
        x = row * (radius * 2) + 900  # Positioning vertically (now horizontal)
        y = (col - row / 2) * (radius * 2) + (((2*screen.get_height()) - 700)/2)  # Centering the triangle vertically
        create_ball(space, (x, y), radius)


def convert_coordinates(point): # converting pygame coordinates to pymunk coordinates (pymunk coordinates put the origin in the bottom left corner
    return point[0], screen.get_height() - point[1]

def check_pocket_collisions(ball, pockets, pocket_radius):
    for pocket in pockets:
        # Calculate the distance between the ball's position and the pocket's position
        distance = (ball.body.position - pocket.body.position).length
        # Check if the distance is less than the sum of the radii
        if distance < (ball.radius + pocket_radius):
            return True  # Ball is in the pocket
    return False  # No collision detected



class Ball(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y)

class Cue(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y)

    # def update(self):
    #     super().update()
    #
    # def draw(self):
    #     super().draw()

    # def get_angle(self):




while True:
    # Process player inputs.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_pulling_back = True
                pull_back_distance = 0  # Reset the pull back distance
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # if test_ball.velocity.x == 0 and test_ball.velocity.y == 0:
                    # Calculate the force to apply based on the pull back distance
                    force_magnitude = pull_back_distance * 100  # Adjust the multiplier as needed
                    force_vector = -Vec2d(math.cos(cue_angle), math.sin(cue_angle)) * force_magnitude
                    test_ball.apply_impulse_at_local_point(force_vector, (0, 0))
                    is_pulling_back = False

        if is_pulling_back:
            pull_back_distance += 1  # Increment pull back distance while the key is held down


    # Do logical updates here.
    # ...
    # for shape in space.shapes:
    #     # Check for pocket collisions
    #     if check_pocket_collisions(shape, pockets, pocket_radius):
    #         print("Ball in pocket!")
    #         space.remove(shape)  # Remove the ball from the simulation

    # Update cue stick angle based on mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    ball_pos = test_ball.position
    angle = (math.atan2(mouse_y - (screen.get_height() - ball_pos.y), mouse_x - ball_pos.x))
    cue_angle = angle
    mouse_pos = pygame.mouse.get_pos()
    # cue.rect.center = space.shapes[-1].body.position
    # x_dist = space.shapes[-1].body.position[0] - mouse_pos[0]
    # y_dist = -(space.shapes[-1].body.position[1] - mouse_pos[1]) # -ve because pygame y coordinates increase down the screen
    # cue_angle = math.degrees(math.atan2(y_dist, x_dist))
    # cue.update(cue_angle)
    # cue.draw(screen)


    screen.fill("white")  # Fill the display with a solid color

    # Render the graphics here.
    # ...

    # drawing sides of pool table
    pygame.draw.line(screen, 'black', (75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 100), 5 )
    pygame.draw.line(screen, 'black', (screen.get_width() - 75, screen.get_height() - 100), (screen.get_width() - 75, screen.get_height() - 600), 5 )
    pygame.draw.line(screen, 'black', (screen.get_width() - 75, screen.get_height() - 600), (75, screen.get_height() - 600), 5 )
    pygame.draw.line(screen, 'black', (75, screen.get_height() - 600), (75, screen.get_height() - 100), 5 )

    # drawing pockets of pool table
    # for pos in pocket_positions:
    #     pygame.draw.circle(screen, (0, 0, 0), pos, pocket_radius)  # Draw the pockets as black circles

    count = 0
    for shape in space.shapes:
        position = shape.body.position
        if count % 2 == 0:
            color = (255, 0, 0)
            count += 1
        else:
            color = (0, 0, 255)
            count += 1

        pygame.draw.circle(screen, color, (int(position.x), int(position.y)), radius)

    pygame.draw.circle(screen, (255, 0, 255), (int(test_ball.position.x), int(test_ball.position.y)), 18)


        # Check if the test ball is not moving
    if test_ball.velocity.length < 1:  # Check if the speed is less than 1
        # Draw the cue stick
        cue_start = (ball_pos.x, ball_pos.y )
        cue_end = (ball_pos.x + cue_length * math.cos(cue_angle),
                       ball_pos.y + cue_length * math.sin(cue_angle))
        pygame.draw.line(screen, 'black', cue_start, cue_end, 10)

        pygame.draw.line(screen, 'black', cue_start, cue_end, 10)
    # In your main loop, apply friction to each ball
    # for shape in space.shapes:
    #     if isinstance(shape, pymunk.Circle):  # Assuming your balls are Circles
    #         apply_friction(shape.body)


    pygame.display.flip()  # Refresh on-screen display
    clock.tick(144) # wait until next frame (at 60 FPS)
    space.step(1/144) # running the simulation