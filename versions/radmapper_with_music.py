import pygame
import math
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 16
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE
CAR_COLOR = (255, 0, 0)
WALL_COLOR = (0, 0, 255)
SOURCE_COLOR = (0, 0, 0)  # Invisible color (same as background)
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 24

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Radmapper V1.2 (now with music!)")

# Game states
MENU, GROUND_MAPPING, AERIAL_MAPPING, GAME_OVER, SHOW_SOURCE, CALL_MAIN, SHOW_MAPS = 0, 1, 2, 3, 4, 5, 6

current_state = MENU

class Button:
    def __init__(self, text, x, y, width, height, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, (150, 150, 150), self.rect)
        font = pygame.font.SysFont(None, FONT_SIZE)
        text_surface = font.render(self.text, True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def draw_hovered(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        font = pygame.font.SysFont(None, FONT_SIZE)
        text_surface = font.render(self.text, True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# Create buttons for the menu
buttons = [
    Button("Ground Mapping", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 40, GROUND_MAPPING),
    Button("Aerial Mapping", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 40, AERIAL_MAPPING),
    Button("Show Maps", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 40, SHOW_MAPS),
    Button("Quit", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 40, pygame.QUIT),
    Button("Show Source", SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT - 50, 200, 40, SHOW_SOURCE),
    Button("Return to Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40, CALL_MAIN),
]

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

def distance_squared_3D(x1, y1, x2, y2):
    return (x2 - x1) ** 2 + (y2 - y1) ** 2 + 10 ** 2

def draw_counts(counts, x, y):
    font = pygame.font.SysFont(None, FONT_SIZE)
    text = font.render(f"Counts: {counts:.2f}", True, FONT_COLOR)
    screen.blit(text, (x, y))

def draw_timer(time_left):
    font = pygame.font.SysFont(None, FONT_SIZE)
    text = font.render(f"Time Left: {time_left:.1f} seconds", True, FONT_COLOR)
    screen.blit(text, (SCREEN_WIDTH - 200, 10))

def draw_menu():
    font = pygame.font.SysFont(None, 4 * FONT_SIZE)
    text1 = font.render("Radmapper V1.0", True, (255,105,180))
    font = pygame.font.SysFont(None, 2 * FONT_SIZE)
    text2 = font.render("Choose Mapping Method:", True, FONT_COLOR)
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT - 8 * text1.get_height()))
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT - 12 * text2.get_height()))

def main():
    clock = pygame.time.Clock()
    car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2
    # Randomly place the source in the grid
    source_x, source_y = random.randint(1, GRID_WIDTH - 1), random.randint(1, GRID_HEIGHT - 1)

    ground_time = 30
    aerial_time = 15

    # Initialize count data for the heat map
    count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))

    heatmap_image = None

    # Create a list of wall positions
    building_features = []

    back_wall_y = GRID_HEIGHT - 5
    back_wall_x = [i for i in range(5,GRID_WIDTH//2 - 1)]
    back_wall_x.extend([i for i in range(GRID_WIDTH//2+1, GRID_WIDTH-4)])
    for i in back_wall_x:
        building_features.append((i, back_wall_y))

    left_wall_x = 5
    left_wall_y = [i for i in range(5,GRID_HEIGHT-4)]
    for i in left_wall_y:
        building_features.append((left_wall_x, i))

    right_wall_x = GRID_WIDTH - 5
    right_wall_y = [i for i in range(5,GRID_HEIGHT-4)]
    for i in right_wall_y:
        building_features.append((right_wall_x, i))

    front_wall_y = 5
    front_wall_x = [i for i in range(5, GRID_WIDTH-4)]
    for i in front_wall_x:
        building_features.append((i, front_wall_y))

    # horizontal wall for rooms on left side
    inside_wall1_y = GRID_HEIGHT//2
    inside_wall1_x = [i for i in range(5, GRID_WIDTH//2-4)]
    for i in inside_wall1_x:
        building_features.append((i, inside_wall1_y))

    # horizontal wall for rooms on right side
    inside_wall2_y = GRID_HEIGHT//2
    inside_wall2_x = [i for i in range(GRID_WIDTH//2+4, GRID_WIDTH-4)]
    for i in inside_wall2_x:
        building_features.append((i, inside_wall2_y))

    # vertical wall for top room on left side
    inside_wall3_x = GRID_WIDTH//2 - 5
    inside_wall3_y = [i for i in range(5, GRID_HEIGHT//2-4)] + [GRID_HEIGHT//2 + i for i in range(-2, 4)]
    for i in inside_wall3_y:
        building_features.append((inside_wall3_x, i))

    # vertical wall for top room on right side
    inside_wall4_x = GRID_WIDTH//2 + 4
    inside_wall4_y = [i for i in range(5, GRID_HEIGHT//2-4)] + [GRID_HEIGHT//2 + i for i in range(-2, 4)]
    for i in inside_wall4_y:
        building_features.append((inside_wall4_x, i))

    # horizontal wall for top room in middle
    inside_wall5_y = GRID_HEIGHT//2 - 5
    inside_wall5_x = [i for i in range(GRID_WIDTH//2-4, GRID_WIDTH//2-1)]
    inside_wall5_x.extend([i for i in range(GRID_WIDTH//2+1, GRID_WIDTH//2+4)])
    for i in inside_wall5_x:
        building_features.append((i, inside_wall5_y))

    # vertical wall for bottom room on left side
    inside_wall6_x = GRID_WIDTH//2 - 5
    inside_wall6_y = [i for i in range(GRID_HEIGHT//2+6, GRID_HEIGHT-4)]
    for i in inside_wall6_y:
        building_features.append((inside_wall6_x, i))

    # vertical wall for bottom room on right side
    inside_wall7_x = GRID_WIDTH//2 + 4
    inside_wall7_y = [i for i in range(GRID_HEIGHT//2+6, GRID_HEIGHT-4)]
    for i in inside_wall7_y:
        building_features.append((inside_wall7_x, i))

    for wall_position in building_features:
        walls.add_wall(*wall_position)

    global current_state
    game_over = False
    prev_state = 10

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if current_state == MENU or current_state == GAME_OVER or current_state == SHOW_SOURCE:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in buttons:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action

            if current_state == MENU:
                screen.fill((0, 0, 0))
                for button in buttons[:2]:
                    # Check if the mouse pointer is over the button
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        button.hovered = True
                    else:
                        button.hovered = False

                    # Draw the button with appropriate color
                    if button.hovered:
                        button.draw_hovered()
                    else:
                        button.draw()
                draw_menu()

        if current_state == MENU:
            if prev_state != current_state:
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/menu.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop

        if current_state == GROUND_MAPPING:
            if prev_state != current_state:
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/adventure.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop

        if current_state == AERIAL_MAPPING:
            if prev_state != current_state:
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/platforming.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop

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
            if current_state == GROUND_MAPPING:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT and (new_car_x, new_car_y) not in walls.walls:
                    car_x, car_y = new_car_x, new_car_y
            elif current_state == AERIAL_MAPPING:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT:
                    car_x, car_y = new_car_x, new_car_y

            # Update count data for the heat map and timer
            if current_state == GROUND_MAPPING:
                current_time = pygame.time.get_ticks()
                time_left = max(0, ground_time * 1000 - (current_time - start_time))
                bg = np.random.poisson(0.7)
                count_data[car_y, car_x] = min(10000, bg + np.random.poisson(10000 / distance_squared(car_x, car_y, source_x, source_y) + 1))
            elif current_state == AERIAL_MAPPING:
                current_time = pygame.time.get_ticks()
                time_left = max(0, aerial_time * 1000 - (current_time - start_time))
                bg = np.random.poisson(0.7/3)
                count_data[car_y, car_x] = min(10000, bg + np.random.poisson(10000 / distance_squared_3D(car_x, car_y, source_x, source_y) + 1))


            # Draw everything on the screen
            screen.fill((0, 0, 0))  # Clear the screen
            draw_car(car_x, car_y)

            walls.draw()
            #draw_source(source_x, source_y)
            draw_counts(count_data[car_y, car_x], car_x * GRID_SIZE, car_y * GRID_SIZE)

            draw_timer(time_left / 1000)  # Draw countdown timer

            # Check if the time is up
            if time_left <= 0:
                if current_state == GROUND_MAPPING:
                    extension = 'ground'
                elif current_state == AERIAL_MAPPING:
                    extension = 'aerial'
                current_state = GAME_OVER

        if current_state == GAME_OVER:
            if heatmap_image is None:
                # Save the heatmap plot as an image
                plt.imshow(count_data+1, cmap='hot', interpolation='nearest', norm=LogNorm())
                plt.colorbar().set_label('Radiation Intensity (counts per second)')
                plt.title('Your Radiation Heat Map')
                plt.axis('off')
                plt.savefig(f'plots/heatmap_{extension}.png')  # Save the plot as an image
                plt.close()
                # show source
                plt.imshow(count_data+1, cmap='hot', interpolation='nearest', norm=LogNorm())
                plt.colorbar().set_label('Radiation Intensity (counts per second)')
                plt.title('Your Radiation Heat Map')
                plt.scatter(source_x, source_y, c='limegreen', s=100)
                plt.axis('off')
                plt.savefig(f'plots/heatmap_{extension}_withsource.png')  # Save the plot as an image
                plt.close()

        if current_state == SHOW_SOURCE:
            heatmap_source_image = pygame.image.load(
                f'plots/heatmap_{extension}_withsource.png')  # Load the heatmap image
            heatmap_source_image = pygame.transform.scale(heatmap_source_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(heatmap_source_image, (0, 0))  # Display the heatmap image
        elif current_state == GAME_OVER:
            heatmap_image = pygame.image.load(f'plots/heatmap_{extension}.png')  # Load the heatmap image
            heatmap_image = pygame.transform.scale(heatmap_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(heatmap_image, (0, 0))

        if current_state == GAME_OVER:
            for button in buttons[-2:]:
                # Check if the mouse pointer is over the button
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hovered = True
                else:
                    button.hovered = False

                # Draw the button with appropriate color
                if button.hovered:
                    button.draw_hovered()
                else:
                    button.draw()
        elif current_state == SHOW_SOURCE:
            for button in buttons[-1:]:
                # Check if the mouse pointer is over the button
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hovered = True
                else:
                    button.hovered = False

                # Draw the button with appropriate color
                if button.hovered:
                    button.draw_hovered()
                else:
                    button.draw()

        if current_state == CALL_MAIN:
            current_state = MENU
            main()

        pygame.display.update()

        if current_state == GROUND_MAPPING:
            clock.tick(10)  # Adjust the speed of the game
        elif current_state == AERIAL_MAPPING:
            clock.tick(30)  # Adjust the speed of the game
        else:
            clock.tick(60)
        prev_state = current_state


if current_state != MENU:
    pygame.quit()

if __name__ == "__main__":
    main()
