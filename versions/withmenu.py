import pygame
import math
import random
import numpy as np
import matplotlib.pyplot as plt

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE
CAR_COLOR = (255, 0, 0)
WALL_COLOR = (0, 0, 255)
SOURCE_COLOR = (0, 0, 0)  # Invisible color (same as background)
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 24
COUNTDOWN_SECONDS = 60  # Set countdown timer (60 seconds)

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Driving Game with Walls")

# Game states
MENU, GROUND_MAPPING, AERIAL_MAPPING, GAME_OVER = 0, 1, 2, 3
current_state = MENU

class Walls:
    def __init__(self):
        self.walls = set()

    def add_wall(self, x, y):
        self.walls.add((x, y))

    def draw(self):
        for wall in self.walls:
            draw_wall(wall[0], wall[1])

walls = Walls()

def draw_car(x, y):
    pygame.draw.rect(screen, CAR_COLOR, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_wall(x, y):
    pygame.draw.rect(screen, WALL_COLOR, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_source(x, y):
    pygame.draw.rect(screen, SOURCE_COLOR, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def distance_squared(x1, y1, x2, y2):
    return (x2 - x1) ** 2 + (y2 - y1) ** 2

def draw_counts(counts, x, y):
    font = pygame.font.SysFont(None, FONT_SIZE)
    text = font.render(f"Counts: {counts:.2f}", True, FONT_COLOR)
    screen.blit(text, (x, y))

def draw_timer(time_left):
    font = pygame.font.SysFont(None, FONT_SIZE)
    text = font.render(f"Time Left: {time_left:.1f} seconds", True, FONT_COLOR)
    screen.blit(text, (SCREEN_WIDTH - 200, 10))

def draw_menu():
    font = pygame.font.SysFont(None, 2 * FONT_SIZE)
    text1 = font.render("Select Mapping Type:", True, FONT_COLOR)
    text2 = font.render("1. Ground Mapping", True, FONT_COLOR)
    text3 = font.render("2. Aerial Mapping", True, FONT_COLOR)
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 2 - text1.get_height()))
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, SCREEN_HEIGHT // 2 + text2.get_height()))

def main():
    clock = pygame.time.Clock()
    car_x, car_y = 1, 1
    # Randomly place the source in the grid
    source_x, source_y = random.randint(1, GRID_WIDTH - 1), random.randint(1, GRID_HEIGHT - 1)

    # Add a single wall
    walls.add_wall(5, 3)

    global current_state
    game_over = False
    score = 0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if current_state == MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_state = GROUND_MAPPING
                    elif event.key == pygame.K_2:
                        current_state = AERIAL_MAPPING

        if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING:
            keys = pygame.key.get_pressed()
            new_car_x, new_car_y = car_x, car_y
            if keys[pygame.K_LEFT]:
                new_car_x -= 1
            if keys[pygame.K_RIGHT]:
                new_car_x += 1
            if keys[pygame.K_UP]:
                new_car_y -= 1
            if keys[pygame.K_DOWN]:
                new_car_y += 1

            # Check if the new position is within the screen boundaries and not a wall
            if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT and (new_car_x, new_car_y) not in walls.walls:
                car_x, car_y = new_car_x, new_car_y

            # Update count data for the heat map
            if current_state == GROUND_MAPPING:
                count_data[car_y, car_x] = max(count_data[car_y, car_x], 10000 / max(1, distance_squared(car_x, car_y, source_x, source_y)))

            # Calculate remaining time based on the current time and the start time
            current_time = pygame.time.get_ticks()
            time_left = max(0, COUNTDOWN_SECONDS * 1000 - (current_time - start_time))

            # Draw everything on the screen
            screen.fill((0, 0, 0))  # Clear the screen
            draw_car(car_x, car_y)

            walls.draw()
            draw_source(source_x, source_y)
            draw_counts(count_data[car_y, car_x], car_x * GRID_SIZE, car_y * GRID_SIZE)

            draw_timer(time_left / 1000)  # Draw countdown timer

            # Check if the time is up
            if time_left <= 0:
                current_state = GAME_OVER

            pygame.display.update()
            clock.tick(60)  # Adjust the speed of the game (60 FPS)

        elif current_state == MENU:
            draw_menu()
            pygame.display.update()
            clock.tick(60)  # Adjust the speed of the game (60 FPS)


    if current_state != MENU:
        print(f"Your final score: {score:.2f}")

        if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING:
            # Create and display the log-scaled heat map
            plt.imshow(np.log1p(count_data), cmap='hot', interpolation='nearest')
            plt.colorbar()
            plt.title('Log-Scaled Heat Map of Counts')
            plt.show()

    pygame.quit()

if __name__ == "__main__":
    # Initialize count data for the heat map
    count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))
    # Countdown timer setup
    start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds

    main()
