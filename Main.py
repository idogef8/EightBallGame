
import pygame, pymunk, math
from pymunk import Vec2d
from pymunk.examples.collisions import post_solve
from pymunk.vec2d import Vec2d

pygame.init()

screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
pygame.font.init()  # you have to call this at the start,
# if you want to use this module.
my_font = pygame.font.SysFont('Roboto', 30)

count = 0
player_1 = 0
player_2 = 1

# load images

test_ball_image = pygame.image.load("ball_16.png")

space = pymunk.Space() # initialized the space in which the physics sim occurs
space.damping = .5
ball_list = []

COLLISION_TYPE_BALL = 1
COLLISION_TYPE_POCKET = 2
COLLISION_TYPE_TEST_BALL = 3

class Ball(pymunk.Body):
    def __init__(self, x, y, image):
        super().__init__(1, pymunk.moment_for_circle(1, 0, 18))
        self.image = image
        self.radius = 18
        self.position = (x, y)
        shape = pymunk.Circle(self, self.radius)
        shape.elasticity = 0.95
        shape.damping = 0.5  # Increasing damping for more noticeable effect
        shape.collision_type = COLLISION_TYPE_BALL
        space.add(self, shape)

    def draw(self, screen):
        screen.blit(self.image, (self.position[0]-self.radius, self.position[1]-self.radius))


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
test_shape.collision_type = COLLISION_TYPE_TEST_BALL
space.add(test_ball, test_shape)

# Cue stick properties
cue_length = 550
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
i = 1
for row in range(rows):
    for col in range(row + 1):
        # Calculate the position of each ball
        x = row * (radius * 2) + 900  # Positioning vertically (now horizontal)
        y = (col - row / 2) * (radius * 2) + (((2*screen.get_height()) - 700)/2)  # Centering the triangle vertically
        ball_list.append(Ball(x, y, pygame.image.load(f"ball_{i}.png").convert_alpha()))
        i += 1


cue_stick_image = pygame.image.load("cue.png")


def convert_coordinates(point): # converting pygame coordinates to pymunk coordinates (pymunk coordinates put the origin in the bottom left corner
    return point[0], screen.get_height() - point[1]



class Text():
    def __init__(self, words):
        text_surface = my_font.render(words, False, (0, 0, 0))
        screen.blit(text_surface, (20, 20))

class Cue():
  def __init__(self, pos):
    self.original_image = cue_stick_image
    self.angle = 0
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = pos

  def update(self, angle):
    self.angle = angle

  def draw(self, surface):
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    surface.blit(self.image,
      (self.rect.centerx - self.image.get_width() / 2,
      self.rect.centery - self.image.get_height() / 2)
     )

cue = Cue(test_ball.position)


# Define a collision handler
def collision_handler(arbiter, space, data):
    # Get the bodies involved in the collision
    body1, body2 = arbiter.shapes[0].body, arbiter.shapes[1].body

    # Remove the body from the space
    if body1 in ball_list and body2 not in ball_list:
        ball_list.remove(body1)
        space.remove(body1, arbiter.shapes[0])  # Remove the first body and its shape
    if body2 in ball_list and body1 not in ball_list:
        ball_list.remove(body2)
        space.remove(body2, arbiter.shapes[1])  # Remove the first body and its shape

    return True  # Return True to keep the collision from being resolved

def collision_handler2(arbiter, space, data):
    body1, body2 = arbiter.shapes[0].body, arbiter.shapes[1].body
    # Remove the body from the space
    if body1 is test_ball and body2 is not test_ball:
        test_ball.position = (200, (((2*screen.get_height()) - 700)/2))
        test_ball.velocity.x = 0
        test_ball.velocity.y = 0
    if body2 is test_ball and body1 is not test_ball:
        test_ball.position = (200, (((2 * screen.get_height()) - 700) / 2))
        test_ball.velocity.x = 0
        test_ball.velocity.y = 0


# Set up the collision handler in the space
handler = space.add_collision_handler(COLLISION_TYPE_BALL, COLLISION_TYPE_POCKET)
handler.begin = collision_handler

handler2 = space.add_collision_handler(COLLISION_TYPE_TEST_BALL, COLLISION_TYPE_POCKET)
handler2.begin = collision_handler2



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
                    force_magnitude = pull_back_distance * -100  # Adjust the multiplier as needed
                    force_vector = direction*force_magnitude #-Vec2d(math.cos(cue_angle), math.sin(cue_angle)) * force_magnitude
                    # test_ball.apply_impulse_at_local_point(force_vector, (0, 0))
                    test_ball.apply_impulse_at_world_point(force_vector, (0, 0))
                    is_pulling_back = False
                    force_vector = 0
                    count += 1



    # mouse_x, mouse_y = pygame.mouse.get_pos()
    # mouse_pos = Vec2d(mouse_x, mouse_y)
    ball_pos = test_ball.position
    # cue_angle = math.atan2(mouse_y - (screen.get_height() - ball_pos.y), mouse_x - ball_pos.x)

    mouse_pos = pygame.mouse.get_pos()
    cue.rect.center = test_ball.position
    x_dist = test_ball.position[0] - mouse_pos[0]
    y_dist = -(test_ball.position[1] - mouse_pos[1])  # -ve because pygame y coordinates increase down the screen
    cue_angle = math.degrees(math.atan2(y_dist, x_dist))
    cue.update(cue_angle)
    cue.draw(screen)

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

    # Draw balls with images
    for ball in ball_list:
        ball.draw(screen)

    # Check if the cue ball is not moving
    if test_ball.velocity.length < 1:  # Check if the speed is less than 1
        cue_stick_length = 150  # Length of the cue stick
        cue_stick_start = test_ball.position

        # Calculate the end position of the cue stick based on the angle
        cue_stick_end = (
            cue_stick_start[0] - cue_stick_length * math.cos(math.radians(cue_angle)),
            cue_stick_start[1] + cue_stick_length * math.sin(math.radians(cue_angle))
        )

        # Rotate and draw the cue stick
        cue_stick_rotated = pygame.transform.rotate(cue_stick_image, cue_angle)  # Negate angle for proper rotation
        cue_stick_rect = cue_stick_rotated.get_rect(center=cue_stick_start)

        # Draw the cue stick with the correct position
        screen.blit(cue_stick_rotated, cue_stick_rect.topleft)





    # Draw pockets
    for pocket in pockets:
        position = pocket.body.position
        pygame.draw.circle(screen, (100, 100, 100), (int(position.x), int(position.y)), pocket_radius)


    pygame.draw.circle(screen, (0, 0, 255), (int(test_ball.position.x), int(test_ball.position.y)), 18)
    screen.blit(test_ball_image, (test_ball.position.x - 18, test_ball.position.y - 18))

        # Check if the test ball is not moving
    # if test_ball.velocity.length < 1:  # Check if the speed is less than 1
    #     # Draw the cue stick
    #     cue_start = (ball_pos.x, ball_pos.y)
    #     cue_vector = ball_pos - pygame.mouse.get_pos()
    #     cue_vector = cue_vector.normalized()
    #     cue_end = cue_start + -cue_vector * cue_length
    #
    #
    #     # Calculate angle for rotation
    #     cue_angle_degrees = -math.degrees(cue_angle)  # Convert to degrees for rotation
    #     cue_stick_rotated = pygame.transform.rotate(cue_stick_image, cue_angle_degrees)
    #
    #     # Get the rect for positioning
    #     cue_stick_rect = cue_stick_rotated.get_rect(center=cue_start)
    #
    #     # Blit the rotated cue stick image
    #     screen.blit(cue_stick_rotated, cue_stick_rect.topleft)

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60) # wait until next frame (at 60 FPS)
    space.step(1/60) # running the simulation
