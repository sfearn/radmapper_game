import pygame
import sys
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


class Button:
    def __init__(self, text, x, y, width, height, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen, FONT_COLOR):
        pygame.draw.rect(screen, (150, 150, 150), self.rect)
        font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)
        text_surface = font.render(self.text, True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def draw_hovered(self, screen, FONT_COLOR):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)
        text_surface = font.render(self.text, True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Walls:
    def __init__(self):
        self.walls = set()

    def add_wall(self, x, y):
        self.walls.add((x, y))

    def draw(self, screen, wall_image, GRID_SIZE):
        for wall in self.walls:
            draw_wall(wall[0], wall[1], wall_image, GRID_SIZE, screen)


def draw_car(x, y, image, CELL_SIZE, screen):
    centered_x = x * CELL_SIZE + (CELL_SIZE - image.get_width()) // 2
    centered_y = y * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2

    screen.blit(image, (centered_x, centered_y))


def draw_wall(x, y, wall_image, GRID_SIZE, screen):
    screen.blit(wall_image, (x * GRID_SIZE, y * GRID_SIZE))


def has_line_of_sight(source_x, source_y, target_x, target_y, wall_positions):
    dx = target_x - source_x
    dy = target_y - source_y

    x, y = source_x, source_y

    if dx > 0 and dy > 0:
        for i in range(dx):
            for j in range(dy):
                if (x + i, y + j) in wall_positions:
                    return False
    elif dx > 0 and dy < 0:
        for i in range(dx):
            for j in range(-dy):
                if (x + i, y - j) in wall_positions:
                    return False
    elif dx < 0 and dy > 0:
        for i in range(-dx):
            for j in range(dy):
                if (x - i, y + j) in wall_positions:
                    return False
    elif dx < 0 and dy < 0:
        for i in range(-dx):
            for j in range(-dy):
                if (x - i, y - j) in wall_positions:
                    return False

    return True  # No walls encountered, line of sight is clear


def distance_squared(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) + 0.1


def distance_squared_3D(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2 + 10 ** 2) + 0.1


def draw_counts(counts, x, y, screen):
    font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 16)
    text1 = font.render(f"CPS:", True, (255, 0, 0))
    text2 = font.render(f"{counts:.2f}", True, (255, 0, 0))
    screen.blit(text1, (x - text1.get_width(), y))
    screen.blit(text2, (x - text2.get_width(), y + text1.get_height()))


def draw_floor(floors, screen, floor_image, CELL_SIZE):
    for floor in floors:
        screen.blit(floor_image, (floor[0] * CELL_SIZE, floor[1] * CELL_SIZE))


def draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image):
    for i in range(GRID_WIDTH + 1):
        for j in range(GRID_HEIGHT + 1):
            screen.blit(grass_image, (i * GRID_SIZE, j * GRID_SIZE))


def draw_timer(time_left, starting_time, screen, FONT_SIZE, SCREEN_WIDTH):
    font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", FONT_SIZE)
    text = font.render(f"Battery:{100 * time_left // starting_time:.1f} %", True, (0, 0, 140))
    screen.blit(text, (SCREEN_WIDTH - (5 + text.get_width()), text.get_height() // 2))


def draw_menu(FONT_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, screen, trefoil_image):
    font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 2 * FONT_SIZE)
    text1 = font.render("Radmapper V1.5", True, (255, 105, 180))
    screen.blit(text1,
                (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT - (SCREEN_HEIGHT / 70) * text1.get_height()))
    screen.blit(trefoil_image, (SCREEN_WIDTH // 2 - trefoil_image.get_width() // 2, SCREEN_HEIGHT - (
                (SCREEN_HEIGHT / 70) * text1.get_height()) + trefoil_image.get_height() // 3))


def draw_show_maps(screen, SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE):
    screen.fill((255, 255, 255))
    font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", FONT_SIZE)
    text1 = font.render("Ground Map", True, (0, 0, 0))
    text2 = font.render("Aerial Map", True, (0, 0, 0))
    screen.blit(text1, (SCREEN_WIDTH // 4 - text1.get_width() // 2, 2 * text1.get_height()))
    screen.blit(text2, (3 * SCREEN_WIDTH // 4 - text2.get_width() // 2, 2 * text2.get_height()))


def increase_volume(current_volume):
    current_volume = min(1.0, current_volume + 0.05)  # Increase by 10%
    pygame.mixer.music.set_volume(current_volume)
    return current_volume


def decrease_volume(current_volume):
    current_volume = max(0.0, current_volume - 0.05)  # Decrease by 10%
    pygame.mixer.music.set_volume(current_volume)
    return current_volume


def main(screen):
    pygame.display.set_caption("Radmapper V1.5 (now fullscreen!)")

    SCREEN_HEIGHT = screen.get_height()
    SCREEN_WIDTH = screen.get_width()
    GRID_SIZE = 30
    GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE
    CAR_COLOR = (255, 0, 0)
    WALL_COLOR = (0, 0, 255)
    SOURCE_COLOR = (0, 0, 0)  # Invisible color (same as background)
    FONT_COLOR = (255, 255, 255)
    FONT_SIZE = 24
    CELL_SIZE = GRID_SIZE
    GROUND_MAPPING_TIME = 35
    AERIAL_MAPPING_TIME = 20

    # Load textures
    wall_image = pygame.image.load("textures/redbrick.png")
    floor_image = pygame.image.load("textures/floor.jpg")
    grass_image = pygame.image.load("textures/grass.png")
    roof_image = pygame.image.load("textures/woodroofing.png")
    man_back_image = pygame.image.load("textures/man_back.png")
    man_front_image = pygame.image.load("textures/man_front.png")
    drone_image = pygame.image.load("textures/drone.png")
    trefoil_image = pygame.image.load("textures/trefoil.png")

    # Resize textures
    wall_image = pygame.transform.scale(wall_image, (CELL_SIZE, CELL_SIZE))
    floor_image = pygame.transform.scale(floor_image, (CELL_SIZE, CELL_SIZE))
    grass_image = pygame.transform.scale(grass_image, (CELL_SIZE, CELL_SIZE))
    roof_image = pygame.transform.scale(roof_image, (CELL_SIZE, CELL_SIZE))
    man_front_image = pygame.transform.scale(man_front_image, (CELL_SIZE * 2, CELL_SIZE * 2))
    man_back_image = pygame.transform.scale(man_back_image, (CELL_SIZE * 2, CELL_SIZE * 2))
    drone_image = pygame.transform.scale(drone_image, (CELL_SIZE * 3, CELL_SIZE * 3))
    trefoil_image = pygame.transform.scale(trefoil_image, (CELL_SIZE * 5, CELL_SIZE * 5))

    # Game states
    MENU, GROUND_MAPPING, AERIAL_MAPPING, GAME_OVER, SHOW_SOURCE, CALL_MAIN, SHOW_MAPS, QUIT = 0, 1, 2, 3, 4, 5, 6, 7

    current_state = MENU

    # Create buttons for the menu
    buttons = [
        Button("Ground Mapping", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 40, GROUND_MAPPING),
        Button("Aerial Mapping", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 40, AERIAL_MAPPING),
        Button("Show Maps", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 40, SHOW_MAPS),
        Button("Quit", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 40, QUIT),
        Button("Show Source", SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT - 50, 200, 40, SHOW_SOURCE),
        Button("Return to Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40, CALL_MAIN),
    ]

    # Create the walls
    walls = Walls()

    current_volume = 0.5  # Initial music volume

    clock = pygame.time.Clock()
    car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2
    # Randomly place the source in the grid
    source_x, source_y = random.randint(1, GRID_WIDTH - 1), random.randint(1, GRID_HEIGHT - 1)

    # Initialize count data for the heat map
    count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))

    heatmap_image = None

    floors = []
    for i in range(5, GRID_HEIGHT - 5):
        for j in range(5, GRID_WIDTH - 5):
            floors.append((j, i))

    # Create a list of wall positions
    building_features = []

    back_wall_y = GRID_HEIGHT - 5
    back_wall_x = [i for i in range(5, GRID_WIDTH // 2 - 1)]
    back_wall_x.extend([i for i in range(GRID_WIDTH // 2 + 1, GRID_WIDTH - 4)])
    for i in back_wall_x:
        building_features.append((i, back_wall_y))

    left_wall_x = 5
    left_wall_y = [i for i in range(5, GRID_HEIGHT - 4)]
    for i in left_wall_y:
        building_features.append((left_wall_x, i))

    right_wall_x = GRID_WIDTH - 5
    right_wall_y = [i for i in range(5, GRID_HEIGHT - 4)]
    for i in right_wall_y:
        building_features.append((right_wall_x, i))

    front_wall_y = 5
    front_wall_x = [i for i in range(5, GRID_WIDTH - 4)]
    for i in front_wall_x:
        building_features.append((i, front_wall_y))

    # horizontal wall for rooms on left side
    inside_wall1_y = GRID_HEIGHT // 2
    inside_wall1_x = [i for i in range(5, GRID_WIDTH // 2 - 4)]
    for i in inside_wall1_x:
        building_features.append((i, inside_wall1_y))

    # horizontal wall for rooms on right side
    inside_wall2_y = GRID_HEIGHT // 2
    inside_wall2_x = [i for i in range(GRID_WIDTH // 2 + 4, GRID_WIDTH - 4)]
    for i in inside_wall2_x:
        building_features.append((i, inside_wall2_y))

    # vertical wall for top room on left side
    inside_wall3_x = GRID_WIDTH // 2 - 5
    inside_wall3_y = [i for i in range(5, GRID_HEIGHT // 2 - 4)] + [GRID_HEIGHT // 2 + i for i in range(-2, 4)]
    for i in inside_wall3_y:
        building_features.append((inside_wall3_x, i))

    # vertical wall for top room on right side
    inside_wall4_x = GRID_WIDTH // 2 + 4
    inside_wall4_y = [i for i in range(5, GRID_HEIGHT // 2 - 4)] + [GRID_HEIGHT // 2 + i for i in range(-2, 4)]
    for i in inside_wall4_y:
        building_features.append((inside_wall4_x, i))

    # horizontal wall for top room in middle
    inside_wall5_y = GRID_HEIGHT // 2 - 5
    inside_wall5_x = [i for i in range(GRID_WIDTH // 2 - 4, GRID_WIDTH // 2 - 1)]
    inside_wall5_x.extend([i for i in range(GRID_WIDTH // 2 + 1, GRID_WIDTH // 2 + 4)])
    for i in inside_wall5_x:
        building_features.append((i, inside_wall5_y))

    # vertical wall for bottom room on left side
    inside_wall6_x = GRID_WIDTH // 2 - 5
    inside_wall6_y = [i for i in range(GRID_HEIGHT // 2 + 6, GRID_HEIGHT - 4)]
    for i in inside_wall6_y:
        building_features.append((inside_wall6_x, i))

    # vertical wall for bottom room on right side
    inside_wall7_x = GRID_WIDTH // 2 + 4
    inside_wall7_y = [i for i in range(GRID_HEIGHT // 2 + 6, GRID_HEIGHT - 4)]
    for i in inside_wall7_y:
        building_features.append((inside_wall7_x, i))

    for wall_position in building_features:
        walls.add_wall(*wall_position)

    game_over = False
    prev_state = 10

    while not game_over:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if current_state == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                # There's some code to add back window content here.
                screen = pygame.display.set_mode((event.w, event.h),
                                                 pygame.RESIZABLE)

                if current_state != GROUND_MAPPING and current_state != AERIAL_MAPPING:
                    main(screen)
                else:
                    SCREEN_HEIGHT = screen.get_height()
                    SCREEN_WIDTH = screen.get_width()
                    GRID_SIZE = 30
                    GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE

                    # re-initialize count data for the heat map with new size
                    previous_count_data = count_data.copy()
                    count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))
                    for i in range(min(previous_count_data.shape[0], count_data.shape[0])):
                        for j in range(min(previous_count_data.shape[1], count_data.shape[1])):
                            count_data[i][j] = previous_count_data[i][j]

                    if car_y >= GRID_HEIGHT:
                        car_y = GRID_HEIGHT - 1
                    if car_x >= GRID_WIDTH:
                        car_x = GRID_WIDTH - 1

            if current_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in buttons:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action
            if current_state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in buttons[4:]:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action
            if current_state == SHOW_SOURCE or current_state == SHOW_MAPS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in buttons[5:]:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action

            if current_state == MENU:
                draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image)
                for button in buttons[:4]:
                    # Check if the mouse pointer is over the button
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        button.hovered = True
                    else:
                        button.hovered = False

                    # Draw the button with appropriate color
                    if button.hovered:
                        button.draw_hovered(screen, FONT_COLOR)
                    else:
                        button.draw(screen, FONT_COLOR)
                draw_menu(FONT_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, screen, trefoil_image)

        if keys[pygame.K_ESCAPE]:
            current_state = QUIT
        if keys[pygame.K_LEFTBRACKET]:
            current_volume = decrease_volume(current_volume)
        if keys[pygame.K_RIGHTBRACKET]:
            current_volume = increase_volume(current_volume)

        if current_state == MENU:
            if prev_state != current_state:
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/menu.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop
                pygame.mixer.music.set_volume(0.5)

        if current_state == GROUND_MAPPING:
            if prev_state != current_state:
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/adventure.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop
                pygame.mixer.music.set_volume(current_volume)
                car_image = man_front_image
                starting_time = GROUND_MAPPING_TIME

        if current_state == AERIAL_MAPPING:
            if prev_state != current_state:
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/platforming.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop
                pygame.mixer.music.set_volume(current_volume)
                car_image = drone_image
                starting_time = AERIAL_MAPPING_TIME

        if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING:
            new_car_x, new_car_y = car_x, car_y
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_car_x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_car_x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                new_car_y -= 1
                if current_state == GROUND_MAPPING:
                    car_image = man_back_image
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                new_car_y += 1
                if current_state == GROUND_MAPPING:
                    car_image = man_front_image

            # Check if the new position is within the screen boundaries and not a wall
            if current_state == GROUND_MAPPING:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT and (
                new_car_x, new_car_y) not in walls.walls:
                    car_x, car_y = new_car_x, new_car_y
            elif current_state == AERIAL_MAPPING:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT:
                    car_x, car_y = new_car_x, new_car_y

            # Update count data for the heat map and timer
            if current_state == GROUND_MAPPING:
                current_time = pygame.time.get_ticks()
                time_left = max(0, GROUND_MAPPING_TIME * 1000 - (current_time - start_time))
                bg = np.random.poisson(0.7)
                line_of_sight = has_line_of_sight(car_x, car_y, source_x, source_y, walls.walls)
                if not line_of_sight:
                    count_data[car_y, car_x] = min(5000, bg + np.random.poisson(
                        5000 / distance_squared(car_x, car_y, source_x, source_y)))
                else:
                    count_data[car_y, car_x] = min(10000, bg + np.random.poisson(
                        10000 / distance_squared(car_x, car_y, source_x, source_y)))
            elif current_state == AERIAL_MAPPING:
                current_time = pygame.time.get_ticks()
                time_left = max(0, AERIAL_MAPPING_TIME * 1000 - (current_time - start_time))
                bg = np.random.poisson(0.7 / 3)
                count_data[car_y, car_x] = min(10000, bg + np.random.poisson(
                    10000 / distance_squared_3D(car_x, car_y, source_x, source_y)))

            # Draw everything on the screen
            draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image)
            draw_floor(floors, screen, floor_image, CELL_SIZE)
            walls.draw(screen, wall_image, GRID_SIZE)
            draw_car(car_x, car_y, car_image, CELL_SIZE, screen)
            draw_counts(count_data[car_y, car_x], car_x * GRID_SIZE, car_y * GRID_SIZE, screen)

            draw_timer(time_left / 1000, starting_time, screen, FONT_SIZE, SCREEN_WIDTH)  # Draw countdown timer

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
                plt.Figure(figsize=(GRID_HEIGHT, GRID_HEIGHT))
                plt.imshow(count_data + 1, cmap='hot', interpolation='nearest', norm=LogNorm())
                plt.colorbar().set_label('Radiation Intensity (counts per second)')
                plt.title('Your Radiation Heat Map')
                plt.axis('off')
                plt.savefig(f'plots/heatmap_{extension}.png')  # Save the plot as an image
                plt.close()
                # show source
                plt.imshow(count_data + 1, cmap='hot', interpolation='nearest', norm=LogNorm())
                plt.colorbar().set_label('Radiation Intensity (counts per second)')
                plt.title(f'Your {extension} radiation heat map')
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
                    button.draw_hovered(screen, FONT_COLOR)
                else:
                    button.draw(screen, FONT_COLOR)
        elif current_state == SHOW_SOURCE:
            for button in buttons[-1:]:
                # Check if the mouse pointer is over the button
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hovered = True
                else:
                    button.hovered = False

                # Draw the button with appropriate color
                if button.hovered:
                    button.draw_hovered(screen, FONT_COLOR)
                else:
                    button.draw(screen, FONT_COLOR)

        if current_state == SHOW_MAPS:
            draw_show_maps(screen, SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE)
            for button in buttons[-1:]:
                # Check if the mouse pointer is over the button
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hovered = True
                else:
                    button.hovered = False

                # Draw the button with appropriate color
                if button.hovered:
                    button.draw_hovered(screen, FONT_COLOR)
                else:
                    button.draw(screen, FONT_COLOR)

            ground_map = pygame.image.load(
                f'plots/heatmap_ground_withsource.png')  # Load the heatmap image
            ground_map = pygame.transform.scale(ground_map, (SCREEN_WIDTH // 2, SCREEN_HEIGHT / 1.5))

            aerial_map = pygame.image.load(
                f'plots/heatmap_aerial_withsource.png')
            aerial_map = pygame.transform.scale(aerial_map, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))

            screen.blit(aerial_map, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))  # Display the heatmap image
            screen.blit(ground_map, (0, SCREEN_HEIGHT // 6))  # Display the heatmap image

        if current_state == CALL_MAIN:
            current_state = MENU
            main(screen)

        pygame.display.update()

        if current_state == GROUND_MAPPING:
            clock.tick(10)  # Adjust the speed of the game
        elif current_state == AERIAL_MAPPING:
            clock.tick(25)  # Adjust the speed of the game
        else:
            clock.tick(60)
        prev_state = current_state


if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    # Create the screen
    infoObject = pygame.display.Info()
    screen = pygame.display.set_mode((infoObject.current_w * 0.95, infoObject.current_h * 0.9), pygame.RESIZABLE)
    main(screen)
