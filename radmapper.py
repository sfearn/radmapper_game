import pygame
import sys
import time
import random
import math
import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("plots", exist_ok=True)


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


def draw_car(x, y, image, CELL_SIZE, screen):
    centered_x = x * CELL_SIZE + (CELL_SIZE - image.get_width()) // 2
    centered_y = y * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2

    screen.blit(image, (centered_x, centered_y))


def draw_wall(x, y, wall_image, GRID_SIZE, screen):
    screen.blit(wall_image, (x * GRID_SIZE, y * GRID_SIZE))


def counts_to_hot_rgb_array(counts, min_count, max_count):
    """
    Convert a 2D array of counts to an array of RGB values corresponding to the 'hot' colormap.

    Parameters:
    - counts: A 2D numpy array of counts to be converted.
    - min_count: The minimum count (corresponding to black).
    - max_count: The maximum count (corresponding to white).

    Returns:
    - A 3D numpy array where the last dimension is 3, representing the RGB values.
    """
    # Normalize the counts to the range [0, 1]
    normalized = (counts - min_count) / (max_count - min_count)
    normalized = np.clip(normalized, 0, 1)  # Clamp to [0, 1]

    # Initialize the RGB arrays
    r = np.zeros_like(normalized)
    g = np.zeros_like(normalized)
    b = np.zeros_like(normalized)

    # Define the segments
    segment1 = normalized < 1 / 3
    segment2 = (normalized >= 1 / 3) & (normalized < 2 / 3)
    segment3 = normalized >= 2 / 3

    # Apply the colormap to each segment
    r[segment1] = (normalized[segment1] * 3) * 255
    r[segment2] = 255
    r[segment3] = 255

    g[segment1] = 0
    g[segment2] = ((normalized[segment2] - 1 / 3) * 3) * 255
    g[segment3] = 255

    b[segment1] = 0
    b[segment2] = 0
    b[segment3] = ((normalized[segment3] - 2 / 3) * 3) * 255

    # Stack the RGB arrays along the last dimension to form the final 3D array
    rgb_array = np.stack((r, g, b), axis=-1).astype(np.uint8)

    return rgb_array


def has_line_of_sight(source_x, source_y, target_x, target_y, wall_positions):
    """Check line of sight using Bresenham's line algorithm."""
    x0, y0 = source_x, source_y
    x1, y1 = target_x, target_y
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if (x0, y0) != (source_x, source_y) and (x0, y0) != (target_x, target_y):
            if (x0, y0) in wall_positions:
                return False
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return True


def distance_squared(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) + 0.1


def distance_squared_3D(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2 + 10 ** 2) + 0.1


def draw_floor(floors, screen, floor_image, CELL_SIZE):
    for floor in floors:
        screen.blit(floor_image, (floor[0] * CELL_SIZE, floor[1] * CELL_SIZE))


def draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image):
    for i in range(GRID_WIDTH + 1):
        for j in range(GRID_HEIGHT + 1):
            screen.blit(grass_image, (i * GRID_SIZE, j * GRID_SIZE))


def draw_source(source_x, source_y, CELL_SIZE, source_image, screen):
    screen.blit(source_image, (source_x * CELL_SIZE, source_y * CELL_SIZE))


def draw_counts(counts, x, y, screen):
    font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 24)
    text1 = font.render(f"CPS: {counts:.0f}", True, (255, 0, 0))

    # black rectangle with grey fill
    pygame.draw.rect(screen, (0, 0, 0), (text1.get_height()//2, -2+text1.get_height()//2, text1.get_width() + 10, text1.get_height() + 10))
    pygame.draw.rect(screen, (150, 150, 150), (2+text1.get_height()//2, text1.get_height()//2, text1.get_width() + 6, text1.get_height() + 6))
    screen.blit(text1, (6+text1.get_height()//2, text1.get_height()//2))


def draw_menu(FONT_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, screen, trefoil_image):
    font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 2 * FONT_SIZE)
    text1 = font.render("Radmapper V1.7", True, (255, 105, 180))
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


def _hot_color(frac):
    """Return an (R, G, B) tuple for a value 0-1 using the 'hot' colormap."""
    if frac < 1/3:
        return (int(frac * 3 * 255), 0, 0)
    elif frac < 2/3:
        return (255, int((frac - 1/3) * 3 * 255), 0)
    else:
        return (255, 255, int((frac - 2/3) * 3 * 255))


def _draw_outlined_text(surface, font, text, x, y, fg=(255, 255, 255), outline=(0, 0, 0)):
    """Draw text with a 1-pixel black outline for readability."""
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                surface.blit(font.render(text, True, outline), (x + dx, y + dy))
    surface.blit(font.render(text, True, fg), (x, y))


def render_heatmap_surface(width, height, count_data, floors, wall_positions,
                           max_cps, source_positions=None, is_aerial=False):
    """Render a heatmap surface with color scale bar.
    source_positions can be None, a single (x,y) tuple, or a list of (x,y) tuples.
    Returns a pygame.Surface of size (width, height)."""
    grid_h, grid_w = count_data.shape
    # Reserve space for the color bar + labels on the right
    label_font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", max(10, width // 70))
    max_label_w = label_font.size(f"{int(max_cps)}")[0]
    actual_bar_w = max(12, width // 36)
    bar_margin = 6
    right_reserve = bar_margin + actual_bar_w + 4 + max_label_w + bar_margin
    map_w = width - right_reserve
    map_h = height

    surface = pygame.Surface((width, height))
    surface.fill((30, 30, 30))

    sx = map_w / grid_w
    sy = map_h / grid_h

    floors_set = set(floors) if not isinstance(floors, set) else floors

    # Draw floor
    for (fx, fy) in floors_set:
        mx = int(fx * sx)
        my = int(fy * sy)
        pygame.draw.rect(surface, (50, 50, 50),
            (mx, my, max(1, int(sx)), max(1, int(sy))))

    # Draw heatmap tiles using 'hot' colormap style
    for fy in range(grid_h):
        for fx in range(grid_w):
            cv = count_data[fy, fx]
            if cv > 0 and (fx, fy) in floors_set:
                if is_aerial:
                    intensity = min(1.0, cv / max_cps)
                else:
                    intensity = min(1.0, math.log1p(cv) / math.log1p(max_cps))
                mx = int(fx * sx)
                my = int(fy * sy)
                pygame.draw.rect(surface, _hot_color(intensity),
                    (mx, my, max(1, int(sx)), max(1, int(sy))))

    # Draw walls
    for (wx, wy) in wall_positions:
        mx = int(wx * sx)
        my = int(wy * sy)
        pygame.draw.rect(surface, (180, 180, 180),
            (mx, my, max(1, int(sx)), max(1, int(sy))))

    # Draw source markers if provided
    if source_positions is not None:
        # Normalise to a list of tuples
        if isinstance(source_positions, tuple) and len(source_positions) == 2 and not isinstance(source_positions[0], tuple):
            positions = [source_positions]
        else:
            positions = list(source_positions)
        for sp in positions:
            spx = int(sp[0] * sx + sx / 2)
            spy = int(sp[1] * sy + sy / 2)
            radius = max(4, int(min(sx, sy)))
            pygame.draw.circle(surface, (0, 255, 0), (spx, spy), radius)
            pygame.draw.circle(surface, (0, 0, 0), (spx, spy), radius, 2)

    # --- Compact color scale bar ---
    bar_x = map_w + bar_margin
    bar_y_top = 40
    bar_y_bot = map_h - 30
    bar_h = bar_y_bot - bar_y_top

    for i in range(bar_h):
        frac = 1.0 - i / bar_h
        pygame.draw.line(surface, _hot_color(frac),
            (bar_x, bar_y_top + i), (bar_x + actual_bar_w, bar_y_top + i))

    pygame.draw.rect(surface, (200, 200, 200),
        (bar_x, bar_y_top, actual_bar_w, bar_h), 1)

    # Labels to the right of the bar with outlined text
    lx = bar_x + actual_bar_w + 3
    _draw_outlined_text(surface, label_font, "CPS", bar_x, bar_y_top - label_font.get_height() - 4)
    _draw_outlined_text(surface, label_font, f"{int(max_cps)}", lx, bar_y_top - 2)
    _draw_outlined_text(surface, label_font, f"{int(max_cps // 2)}", lx,
        bar_y_top + bar_h // 2 - label_font.get_height() // 2)
    _draw_outlined_text(surface, label_font, "0", lx, bar_y_bot - label_font.get_height() + 2)

    return surface


def increase_volume(current_volume):
    current_volume = min(1.0, current_volume + 0.01)  # Increase by 1%
    pygame.mixer.music.set_volume(current_volume)
    return current_volume


def decrease_volume(current_volume):
    current_volume = max(0.0, current_volume - 0.01)  # Decrease by 1%
    pygame.mixer.music.set_volume(current_volume)
    return current_volume


def generate_and_save_spectrum(isotope, filepath):
    """Generate a simulated gamma-ray spectrum for a given isotope and save as image."""
    energy_bins = np.linspace(0, 2000, 1024)
    spectrum = np.zeros(len(energy_bins))

    # Background - exponential decrease + constant
    background = 20 * np.exp(-energy_bins / 300) + 3
    spectrum += np.random.poisson(background.clip(min=0))

    if isotope == "Cs-137":
        # Photopeak at 662 keV
        photopeak = 500 * np.exp(-0.5 * ((energy_bins - 662) / 12) ** 2)
        spectrum += np.random.poisson(photopeak.clip(min=0))

        # Compton continuum below Compton edge at 477 keV
        compton_cont = np.where(energy_bins < 477,
                                60 * (1 + 0.3 * (energy_bins / 477)),
                                np.where(energy_bins < 662,
                                         10 * np.exp(-(energy_bins - 477) / 30), 0))
        spectrum += np.random.poisson(compton_cont.clip(min=0))

        # Backscatter peak at 184 keV
        backscatter = 80 * np.exp(-0.5 * ((energy_bins - 184) / 20) ** 2)
        spectrum += np.random.poisson(backscatter.clip(min=0))

    elif isotope == "Co-60":
        # Photopeak at 1173 keV
        peak1 = 400 * np.exp(-0.5 * ((energy_bins - 1173) / 15) ** 2)
        spectrum += np.random.poisson(peak1.clip(min=0))

        # Photopeak at 1332 keV
        peak2 = 350 * np.exp(-0.5 * ((energy_bins - 1332) / 16) ** 2)
        spectrum += np.random.poisson(peak2.clip(min=0))

        # Compton continua
        compton1 = np.where(energy_bins < 963, 50 * (1 + 0.2 * energy_bins / 963), 0)
        compton2 = np.where(energy_bins < 1118, 40 * (1 + 0.2 * energy_bins / 1118), 0)
        spectrum += np.random.poisson(compton1.clip(min=0))
        spectrum += np.random.poisson(compton2.clip(min=0))

        # Backscatter peak
        backscatter = 60 * np.exp(-0.5 * ((energy_bins - 214) / 25) ** 2)
        spectrum += np.random.poisson(backscatter.clip(min=0))

    elif isotope == "Eu-152":
        # Eu-152 has many gamma lines - include the prominent ones
        # 121.8 keV
        peak1 = 350 * np.exp(-0.5 * ((energy_bins - 121.8) / 5) ** 2)
        spectrum += np.random.poisson(peak1.clip(min=0))
        # 244.7 keV
        peak2 = 120 * np.exp(-0.5 * ((energy_bins - 244.7) / 7) ** 2)
        spectrum += np.random.poisson(peak2.clip(min=0))
        # 344.3 keV
        peak3 = 320 * np.exp(-0.5 * ((energy_bins - 344.3) / 8) ** 2)
        spectrum += np.random.poisson(peak3.clip(min=0))
        # 411.1 keV
        peak4 = 50 * np.exp(-0.5 * ((energy_bins - 411.1) / 9) ** 2)
        spectrum += np.random.poisson(peak4.clip(min=0))
        # 443.9 keV
        peak5 = 60 * np.exp(-0.5 * ((energy_bins - 443.9) / 9) ** 2)
        spectrum += np.random.poisson(peak5.clip(min=0))
        # 778.9 keV
        peak6 = 160 * np.exp(-0.5 * ((energy_bins - 778.9) / 12) ** 2)
        spectrum += np.random.poisson(peak6.clip(min=0))
        # 867.4 keV
        peak7 = 55 * np.exp(-0.5 * ((energy_bins - 867.4) / 13) ** 2)
        spectrum += np.random.poisson(peak7.clip(min=0))
        # 964.1 keV
        peak8 = 180 * np.exp(-0.5 * ((energy_bins - 964.1) / 14) ** 2)
        spectrum += np.random.poisson(peak8.clip(min=0))
        # 1085.8 keV
        peak9 = 130 * np.exp(-0.5 * ((energy_bins - 1085.8) / 15) ** 2)
        spectrum += np.random.poisson(peak9.clip(min=0))
        # 1112.1 keV
        peak10 = 170 * np.exp(-0.5 * ((energy_bins - 1112.1) / 15) ** 2)
        spectrum += np.random.poisson(peak10.clip(min=0))
        # 1408.0 keV
        peak11 = 250 * np.exp(-0.5 * ((energy_bins - 1408.0) / 17) ** 2)
        spectrum += np.random.poisson(peak11.clip(min=0))

        # Compton continuum from multiple peaks
        compton = np.where(energy_bins < 500, 40 * (1 + 0.3 * energy_bins / 500), 0)
        compton += np.where(energy_bins < 900, 25 * (1 + 0.15 * energy_bins / 900), 0)
        spectrum += np.random.poisson(compton.clip(min=0))

    elif isotope == "Nat. Uranium":
        # Natural uranium - dominated by U-238 decay chain (Pa-234m, Bi-214, Pb-214)
        # and U-235 at 185.7 keV

        # Th-234 / Pa-234m low energy lines
        # 63.3 keV (Th-234)
        peak1 = 200 * np.exp(-0.5 * ((energy_bins - 63.3) / 4) ** 2)
        spectrum += np.random.poisson(peak1.clip(min=0))
        # 92.4 keV (Th-234)
        peak2 = 300 * np.exp(-0.5 * ((energy_bins - 92.4) / 4.5) ** 2)
        spectrum += np.random.poisson(peak2.clip(min=0))
        # 92.8 keV (Th-234) - overlaps
        peak3 = 250 * np.exp(-0.5 * ((energy_bins - 92.8) / 4.5) ** 2)
        spectrum += np.random.poisson(peak3.clip(min=0))

        # U-235 at 185.7 keV
        peak4 = 280 * np.exp(-0.5 * ((energy_bins - 185.7) / 6) ** 2)
        spectrum += np.random.poisson(peak4.clip(min=0))

        # Pb-214 lines
        # 242 keV
        peak5 = 80 * np.exp(-0.5 * ((energy_bins - 242) / 7) ** 2)
        spectrum += np.random.poisson(peak5.clip(min=0))
        # 295.2 keV
        peak6 = 180 * np.exp(-0.5 * ((energy_bins - 295.2) / 8) ** 2)
        spectrum += np.random.poisson(peak6.clip(min=0))
        # 351.9 keV
        peak7 = 340 * np.exp(-0.5 * ((energy_bins - 351.9) / 8) ** 2)
        spectrum += np.random.poisson(peak7.clip(min=0))

        # Bi-214 lines
        # 609.3 keV
        peak8 = 400 * np.exp(-0.5 * ((energy_bins - 609.3) / 11) ** 2)
        spectrum += np.random.poisson(peak8.clip(min=0))
        # 768.4 keV
        peak9 = 60 * np.exp(-0.5 * ((energy_bins - 768.4) / 12) ** 2)
        spectrum += np.random.poisson(peak9.clip(min=0))
        # 1001.0 keV (Pa-234m)
        peak10 = 120 * np.exp(-0.5 * ((energy_bins - 1001.0) / 14) ** 2)
        spectrum += np.random.poisson(peak10.clip(min=0))
        # 1120.3 keV
        peak11 = 150 * np.exp(-0.5 * ((energy_bins - 1120.3) / 15) ** 2)
        spectrum += np.random.poisson(peak11.clip(min=0))
        # 1238.1 keV
        peak12 = 70 * np.exp(-0.5 * ((energy_bins - 1238.1) / 16) ** 2)
        spectrum += np.random.poisson(peak12.clip(min=0))
        # 1764.5 keV
        peak13 = 180 * np.exp(-0.5 * ((energy_bins - 1764.5) / 18) ** 2)
        spectrum += np.random.poisson(peak13.clip(min=0))

        # Enhanced low-energy continuum from beta and scatter
        low_e = 80 * np.exp(-energy_bins / 150)
        spectrum += np.random.poisson(low_e.clip(min=0))

    # Plot and save
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(energy_bins, spectrum, 'b-', linewidth=0.8)
    ax.fill_between(energy_bins, spectrum, alpha=0.3, color='blue')
    ax.set_xlabel('Energy (keV)', fontsize=14)
    ax.set_ylabel('Counts', fontsize=14)
    ax.set_title(f'Measured Spectrum: {isotope}', fontsize=16)
    xlimits = {"Cs-137": 1000, "Co-60": 1600, "Eu-152": 1600, "Nat. Uranium": 2000}
    ax.set_xlim(0, xlimits.get(isotope, 2000))
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    # Add peak annotations
    if isotope == "Cs-137":
        peak_idx = np.argmin(np.abs(energy_bins - 662))
        ax.annotate('662 keV', xy=(662, spectrum[peak_idx]),
                    xytext=(780, spectrum[peak_idx] * 0.85),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=12, color='red')
    elif isotope == "Co-60":
        peak_idx1 = np.argmin(np.abs(energy_bins - 1173))
        peak_idx2 = np.argmin(np.abs(energy_bins - 1332))
        ax.annotate('1173 keV', xy=(1173, spectrum[peak_idx1]),
                    xytext=(1020, spectrum[peak_idx1] * 1.15),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=12, color='red')
        ax.annotate('1332 keV', xy=(1332, spectrum[peak_idx2]),
                    xytext=(1450, spectrum[peak_idx2] * 1.15),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=12, color='red')
    elif isotope == "Eu-152":
        annotations = [(121.8, '122 keV'), (344.3, '344 keV'), (778.9, '779 keV'),
                        (964.1, '964 keV'), (1112.1, '1112 keV'), (1408.0, '1408 keV')]
        for energy, label in annotations:
            idx = np.argmin(np.abs(energy_bins - energy))
            ax.annotate(label, xy=(energy, spectrum[idx]),
                        xytext=(energy + 40, spectrum[idx] * 1.1 + 15),
                        arrowprops=dict(arrowstyle='->', color='red'),
                        fontsize=9, color='red')
    elif isotope == "Nat. Uranium":
        annotations = [(92.4, '92 keV\n(Th-234)'), (185.7, '186 keV\n(U-235)'),
                        (351.9, '352 keV\n(Pb-214)'), (609.3, '609 keV\n(Bi-214)'),
                        (1001.0, '1001 keV\n(Pa-234m)'), (1764.5, '1765 keV\n(Bi-214)')]
        for energy, label in annotations:
            idx = np.argmin(np.abs(energy_bins - energy))
            ax.annotate(label, xy=(energy, spectrum[idx]),
                        xytext=(energy + 50, spectrum[idx] * 1.1 + 15),
                        arrowprops=dict(arrowstyle='->', color='red'),
                        fontsize=9, color='red')

    plt.tight_layout()
    plt.savefig(filepath, dpi=100)
    plt.close()


def generate_random_building(GRID_WIDTH, GRID_HEIGHT):
    """Generate a randomized building layout with outer walls and random internal rooms."""
    building_features = []
    wall_set = set()
    floors = []
    margin = 5
    inner_left = margin
    inner_right = GRID_WIDTH - margin
    inner_top = margin
    inner_bottom = GRID_HEIGHT - margin

    # Floors
    for y in range(inner_top, inner_bottom):
        for x in range(inner_left, inner_right):
            floors.append((x, y))

    def add_wall(x, y):
        if (x, y) not in wall_set:
            wall_set.add((x, y))
            building_features.append((x, y))

    # Front wall (top) - solid
    for x in range(inner_left, inner_right + 1):
        add_wall(x, inner_top)

    # Back wall (bottom) - door in middle
    door_center = GRID_WIDTH // 2
    for x in range(inner_left, inner_right + 1):
        if x != door_center and x != door_center + 1:
            add_wall(x, inner_bottom)

    # Left wall
    for y in range(inner_top, inner_bottom + 1):
        add_wall(inner_left, y)

    # Right wall
    for y in range(inner_top, inner_bottom + 1):
        add_wall(inner_right, y)

    # Random internal walls
    num_h = random.randint(1, 2)
    num_v = random.randint(1, 2)

    # Pick horizontal wall y positions with minimum spacing
    h_positions = []
    for _ in range(50):
        if len(h_positions) >= num_h:
            break
        y = random.randint(inner_top + 4, inner_bottom - 4)
        if all(abs(y - hy) >= 5 for hy in h_positions):
            h_positions.append(y)

    # Pick vertical wall x positions with minimum spacing
    v_positions = []
    for _ in range(50):
        if len(v_positions) >= num_v:
            break
        x = random.randint(inner_left + 4, inner_right - 4)
        if all(abs(x - vx) >= 5 for vx in v_positions):
            v_positions.append(x)

    # Add horizontal walls with doorways
    for wy in h_positions:
        door_x = random.randint(inner_left + 2, inner_right - 3)
        for x in range(inner_left + 1, inner_right):
            if x != door_x and x != door_x + 1:
                add_wall(x, wy)

    # Add vertical walls with doorways in each horizontal segment
    for wx in v_positions:
        y_bounds = sorted([inner_top] + h_positions + [inner_bottom])
        for i in range(len(y_bounds) - 1):
            seg_start = y_bounds[i] + 1
            seg_end = y_bounds[i + 1]
            if seg_end - seg_start < 4:
                continue
            door_y = random.randint(seg_start + 1, seg_end - 3)
            for y in range(seg_start, seg_end):
                if y != door_y and y != door_y + 1:
                    add_wall(wx, y)

    return building_features, floors


def main(screen):
    pygame.display.set_caption("Radmapper V1.7 (now with spectral ID!)")

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

    # Load textures
    wall_image = pygame.image.load("textures/redbrick.png")
    floor_image = pygame.image.load("textures/floor.jpg")
    grass_image = pygame.image.load("textures/grass.png")
    man_back_image = pygame.image.load("textures/man_back.png")
    man_front_image = pygame.image.load("textures/man_front.png")
    man_left_image = pygame.image.load("textures/man_left.png")
    man_right_image = pygame.image.load("textures/man_right.png")
    drone_image = pygame.image.load("textures/drone.png")
    trefoil_image = pygame.image.load("textures/trefoil.png")

    # Resize textures
    # sprites here: https://opengameart.org/content/sci-fi-facility-asset-pack
    wall_image = pygame.transform.scale(wall_image, (CELL_SIZE, CELL_SIZE))
    floor_image = pygame.transform.scale(floor_image, (CELL_SIZE, CELL_SIZE))
    grass_image = pygame.transform.scale(grass_image, (CELL_SIZE, CELL_SIZE))
    man_front_image = pygame.transform.scale(man_front_image, (CELL_SIZE * 2, CELL_SIZE * 2))
    man_back_image = pygame.transform.scale(man_back_image, (CELL_SIZE * 2, CELL_SIZE * 2))
    man_left_image = pygame.transform.scale(man_left_image, (CELL_SIZE * 2, CELL_SIZE * 2))
    man_right_image = pygame.transform.scale(man_right_image, (CELL_SIZE * 2, CELL_SIZE * 2))
    drone_image = pygame.transform.scale(drone_image, (CELL_SIZE * 3, CELL_SIZE * 3))
    trefoil_image = pygame.transform.scale(trefoil_image, (CELL_SIZE * 5, CELL_SIZE * 5))
    source_image = pygame.transform.scale(trefoil_image, (CELL_SIZE, CELL_SIZE))

    # Game states
    MENU, GROUND_MAPPING, AERIAL_MAPPING, TEACHING_MODE, GAME_OVER, SHOW_SOURCE, CALL_MAIN, SHOW_MAPS, QUIT, SPECTRUM_MODE, SETTINGS = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

    current_state = MENU

    # Configurable settings
    settings = {
        'ground_time': 35,
        'aerial_time': 20,
        'max_sources': 3,
    }
    GROUND_MAPPING_TIME = settings['ground_time']
    AERIAL_MAPPING_TIME = settings['aerial_time']

    # Create buttons for the menu
    buttons = [
        Button("Ground Mapping", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 40, GROUND_MAPPING),
        Button("Aerial Mapping", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 40, AERIAL_MAPPING),
        Button("Show Maps", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 40, SHOW_MAPS),
        Button("Spectrum ID", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 40, SPECTRUM_MODE),
        Button("Teaching Mode", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 160, 200, 40, TEACHING_MODE),
        Button("Settings", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 210, 200, 40, SETTINGS),
        Button("Quit", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 260, 200, 40, QUIT),
        Button("Show Source", SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 50, 200, 40, SHOW_SOURCE),
        Button("Return to Menu", SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 50, 200, 40, CALL_MAIN),
    ]

    menu_buttons = buttons[:7]
    in_game_buttons = [buttons[-1]]
    end_game_buttons = buttons[7:]
    shown_source_buttons = [buttons[8]]

    current_volume = 0.1  # Initial music volume

    clock = pygame.time.Clock()
    car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2

    # Initialize count data for the heat map
    count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))

    heatmap_image = None
    heatmap_source_image = None
    last_heatmap_data = {}

    # Generate building layout
    building_features_list, floors = generate_random_building(GRID_WIDTH, GRID_HEIGHT)
    building_features = set(building_features_list)

    simple_walls = []

    left_wall_x = GRID_WIDTH // 2 - 2
    left_wall_y = [i for i in range(GRID_HEIGHT // 2 - 1, GRID_HEIGHT // 2 + 2)]
    for i in left_wall_y:
        simple_walls.append((left_wall_x, i))

    right_wall_x = GRID_WIDTH // 2 + 2
    right_wall_y = [i for i in range(GRID_HEIGHT // 2 - 1, GRID_HEIGHT // 2 + 2)]
    for i in right_wall_y:
        simple_walls.append((right_wall_x, i))

    front_wall_y = GRID_HEIGHT//2 - 2
    front_wall_x = [i for i in range(GRID_WIDTH // 2 - 1 , GRID_WIDTH // 2 + 2)]
    for i in front_wall_x:
        simple_walls.append((i, front_wall_y))
    simple_walls_set = set(simple_walls)

    # Randomly place the source in the grid
    source_x, source_y = random.randint(1, GRID_WIDTH - 1), random.randint(1, GRID_HEIGHT - 1)
    # If the source is in a wall, place it again until it isn't
    while (source_x, source_y) in building_features:
        source_x, source_y = random.randint(1, GRID_WIDTH - 1), random.randint(1, GRID_HEIGHT - 1)

    game_over = False
    prev_state = 10
    a = 0
    prev_pos = (0, 0)

    # Spectrum mode variables
    spectrum_sources = []
    showing_spectrum = False
    spectrum_surface = None
    measured_sources = set()

    # Teaching mode variables
    teaching_instructions_shown = False
    showing_instructions = False
    teaching_spectrum_surface = None
    showing_teaching_spectrum = False
    teaching_source_isotope = "Cs-137"
    teaching_measured = False

    # Mapping mode sources (list of (x, y) tuples)
    mapping_sources = []

    # Mapping mode instructions
    showing_mapping_instructions = False
    mapping_instructions_start = 0

    # Spectrum mode instructions
    showing_spectrum_instructions = False

    # Settings menu selection
    settings_selected = 0  # which setting is currently selected
    settings_keys = ['ground_time', 'aerial_time', 'max_sources']
    settings_labels = ['Ground Time (s)', 'Aerial Time (s)', 'Max Sources']
    settings_ranges = {'ground_time': (10, 120), 'aerial_time': (10, 120), 'max_sources': (1, 5)}

    # Mapping HUD tracking
    visited_tiles = set()
    peak_cps = 0
    total_floor_tiles = len(floors)

    while not game_over:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
                    for button in menu_buttons:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action
            if current_state == SETTINGS:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        settings_selected = (settings_selected - 1) % len(settings_keys)
                    elif event.key == pygame.K_DOWN:
                        settings_selected = (settings_selected + 1) % len(settings_keys)
                    elif event.key == pygame.K_LEFT:
                        key = settings_keys[settings_selected]
                        lo, hi = settings_ranges[key]
                        step = 5 if key != 'max_sources' else 1
                        settings[key] = max(lo, settings[key] - step)
                    elif event.key == pygame.K_RIGHT:
                        key = settings_keys[settings_selected]
                        lo, hi = settings_ranges[key]
                        step = 5 if key != 'max_sources' else 1
                        settings[key] = min(hi, settings[key] + step)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        current_state = MENU
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if Back button clicked
                    back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
                    if back_btn_rect.collidepoint(event.pos):
                        current_state = MENU
            if current_state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in end_game_buttons:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action
            if current_state == SHOW_SOURCE or current_state == SHOW_MAPS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in shown_source_buttons:
                        if button.rect.collidepoint(event.pos):
                            current_state = button.action
            if current_state == SPECTRUM_MODE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if showing_spectrum_instructions:
                        showing_spectrum_instructions = False
                    elif showing_spectrum:
                        showing_spectrum = False
                    else:
                        for i, (sx, sy, isotope) in enumerate(spectrum_sources):
                            if abs(car_x - sx) <= 1 and abs(car_y - sy) <= 1:
                                filepath = f'plots/spectrum_{isotope.replace("-", "")}_{i}.png'
                                generate_and_save_spectrum(isotope, filepath)
                                spectrum_surface = pygame.image.load(filepath)
                                spectrum_surface = pygame.transform.scale(spectrum_surface,
                                    (int(SCREEN_WIDTH * 0.7), int(SCREEN_HEIGHT * 0.7)))
                                showing_spectrum = True
                                measured_sources.add(i)
                                break
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if showing_spectrum_instructions:
                        showing_spectrum_instructions = False
                    elif showing_spectrum:
                        showing_spectrum = False
                    else:
                        for button in in_game_buttons:
                            if button.rect.collidepoint(event.pos):
                                current_state = button.action
            if current_state == TEACHING_MODE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if showing_instructions:
                        showing_instructions = False
                    elif showing_teaching_spectrum:
                        showing_teaching_spectrum = False
                    else:
                        if abs(car_x - source_x) <= 1 and abs(car_y - source_y) <= 1:
                            filepath = f'plots/spectrum_teaching_{teaching_source_isotope.replace("-", "").replace(" ", "").replace(".", "")}.png'
                            generate_and_save_spectrum(teaching_source_isotope, filepath)
                            teaching_spectrum_surface = pygame.image.load(filepath)
                            teaching_spectrum_surface = pygame.transform.scale(teaching_spectrum_surface,
                                (int(SCREEN_WIDTH * 0.7), int(SCREEN_HEIGHT * 0.7)))
                            showing_teaching_spectrum = True
                            teaching_measured = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if showing_instructions:
                        showing_instructions = False
                    elif showing_teaching_spectrum:
                        showing_teaching_spectrum = False
                    else:
                        for button in in_game_buttons:
                            if button.rect.collidepoint(event.pos):
                                current_state = button.action
            if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING:
                if showing_mapping_instructions:
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
                       (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                        showing_mapping_instructions = False
                        start_time = pygame.time.get_ticks()
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for button in in_game_buttons:
                            if button.rect.collidepoint(event.pos):
                                current_state = button.action

            if current_state == MENU:
                draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image)
                for button in menu_buttons:
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

            if current_state == SETTINGS:
                draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image)

                # Darken background
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(180)
                screen.blit(overlay, (0, 0))

                font_title = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 32)
                font_item = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 22)
                font_hint = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 16)

                title = font_title.render("Settings", True, (255, 105, 180))
                screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 6))

                y_start = SCREEN_HEIGHT // 6 + title.get_height() + 40
                for i, (key, label) in enumerate(zip(settings_keys, settings_labels)):
                    val = settings[key]
                    lo, hi = settings_ranges[key]
                    is_sel = (i == settings_selected)

                    color = (255, 255, 0) if is_sel else (200, 200, 200)
                    arrow_l = "< " if is_sel else "  "
                    arrow_r = " >" if is_sel else "  "
                    line_text = f"{arrow_l}{label}: {val}{arrow_r}"
                    rendered = font_item.render(line_text, True, color)
                    screen.blit(rendered, (SCREEN_WIDTH // 2 - rendered.get_width() // 2, y_start + i * 50))

                    # Draw a bar showing the value range
                    bar_w = 200
                    bar_h = 6
                    bar_x = SCREEN_WIDTH // 2 - bar_w // 2
                    bar_y = y_start + i * 50 + rendered.get_height() + 4
                    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h))
                    fill_frac = (val - lo) / max(1, hi - lo)
                    fill_color = (255, 255, 0) if is_sel else (150, 150, 150)
                    pygame.draw.rect(screen, fill_color, (bar_x, bar_y, int(bar_w * fill_frac), bar_h))

                # Hints
                hint1 = font_hint.render("UP/DOWN to select, LEFT/RIGHT to change", True, (160, 160, 160))
                hint2 = font_hint.render("ENTER or ESC to return to menu", True, (160, 160, 160))
                screen.blit(hint1, (SCREEN_WIDTH // 2 - hint1.get_width() // 2, y_start + len(settings_keys) * 50 + 30))
                screen.blit(hint2, (SCREEN_WIDTH // 2 - hint2.get_width() // 2, y_start + len(settings_keys) * 50 + 55))

                # Back button
                back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
                mouse_pos = pygame.mouse.get_pos()
                if back_btn_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (255, 0, 0), back_btn_rect)
                else:
                    pygame.draw.rect(screen, (150, 150, 150), back_btn_rect)
                back_label = font_item.render("Back", True, FONT_COLOR)
                screen.blit(back_label, (back_btn_rect.centerx - back_label.get_width() // 2,
                                         back_btn_rect.centery - back_label.get_height() // 2))

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_LEFTBRACKET]:
            current_volume = decrease_volume(current_volume)
        if keys[pygame.K_RIGHTBRACKET]:
            current_volume = increase_volume(current_volume)

        if current_state == MENU:
            if prev_state != current_state and (prev_state != SHOW_MAPS or prev_state != SHOW_SOURCE):
                # Countdown timer setup
                start_time = pygame.time.get_ticks()  # Get the initial start time in milliseconds
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/menu.mp3")  # Replace "music.mp3" with your music file's path
                pygame.mixer.music.play(-1)  # -1 plays the music in an infinite loop
                pygame.mixer.music.set_volume(current_volume)

        if current_state == TEACHING_MODE:
            if prev_state != current_state:
                source_x, source_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
                starting_time = 10000
                teaching_source_isotope = random.choice(["Cs-137", "Co-60", "Eu-152", "Nat. Uranium"])
                teaching_measured = False
                showing_teaching_spectrum = False
                teaching_spectrum_surface = None
                showing_instructions = True
                start_time = pygame.time.get_ticks()
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/adventure.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(current_volume)
                car_image = man_front_image
                car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2

        if current_state == GROUND_MAPPING:
            if prev_state != current_state:
                building_features_list, floors = generate_random_building(GRID_WIDTH, GRID_HEIGHT)
                building_features = set(building_features_list)
                total_floor_tiles = len(floors)
                count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))
                heatmap_image = None
                car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2
                # Place 1-N random sources
                num_sources = random.randint(1, settings['max_sources'])
                mapping_sources = []
                for _ in range(num_sources):
                    sx, sy = random.randint(6, GRID_WIDTH - 6), random.randint(6, GRID_HEIGHT - 6)
                    while (sx, sy) in building_features or any(abs(sx - ex) < 4 and abs(sy - ey) < 4 for ex, ey in mapping_sources):
                        sx, sy = random.randint(6, GRID_WIDTH - 6), random.randint(6, GRID_HEIGHT - 6)
                    mapping_sources.append((sx, sy))
                starting_time = settings['ground_time']
                showing_mapping_instructions = True
                visited_tiles = set()
                peak_cps = 0
                # Countdown timer setup
                start_time = pygame.time.get_ticks()
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/adventure.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(current_volume)
                car_image = man_front_image


        if current_state == AERIAL_MAPPING:
            if prev_state != current_state:
                building_features_list, floors = generate_random_building(GRID_WIDTH, GRID_HEIGHT)
                building_features = set(building_features_list)
                total_floor_tiles = len(floors)
                count_data = np.zeros((GRID_HEIGHT, GRID_WIDTH))
                heatmap_image = None
                car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2
                # Place 1-N random sources
                num_sources = random.randint(1, settings['max_sources'])
                mapping_sources = []
                for _ in range(num_sources):
                    sx, sy = random.randint(6, GRID_WIDTH - 6), random.randint(6, GRID_HEIGHT - 6)
                    while (sx, sy) in building_features or any(abs(sx - ex) < 4 and abs(sy - ey) < 4 for ex, ey in mapping_sources):
                        sx, sy = random.randint(6, GRID_WIDTH - 6), random.randint(6, GRID_HEIGHT - 6)
                    mapping_sources.append((sx, sy))
                showing_mapping_instructions = True
                visited_tiles = set()
                peak_cps = 0
                # Countdown timer setup
                start_time = pygame.time.get_ticks()
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/platforming.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(current_volume)
                car_image = drone_image
                starting_time = settings['aerial_time']

        if current_state == SPECTRUM_MODE:
            if prev_state != current_state:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("music/adventure.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(current_volume)
                car_image = man_front_image
                car_x, car_y = GRID_WIDTH // 2, GRID_HEIGHT - 2
                showing_spectrum = False
                showing_spectrum_instructions = True
                spectrum_surface = None
                measured_sources = set()
                # Place sources randomly with spacing
                spectrum_sources = []
                all_isotopes = ["Cs-137", "Co-60", "Eu-152", "Nat. Uranium"]
                isotopes = random.choices(all_isotopes, k=5)
                # Ensure at least 3 different isotopes appear
                while len(set(isotopes)) < 3:
                    isotopes = random.choices(all_isotopes, k=5)
                random.shuffle(isotopes)
                for iso in isotopes:
                    placed = False
                    for _ in range(100):
                        sx = random.randint(4, GRID_WIDTH - 4)
                        sy = random.randint(4, GRID_HEIGHT - 4)
                        too_close = False
                        for (ex, ey, _ei) in spectrum_sources:
                            if abs(sx - ex) < 5 and abs(sy - ey) < 5:
                                too_close = True
                                break
                        if not too_close:
                            spectrum_sources.append((sx, sy, iso))
                            placed = True
                            break
                    if not placed:
                        spectrum_sources.append((sx, sy, iso))

        if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING or current_state == TEACHING_MODE:
            can_move = True
            if current_state == TEACHING_MODE and (showing_instructions or showing_teaching_spectrum):
                can_move = False
            if (current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING) and showing_mapping_instructions:
                can_move = False
            new_car_x, new_car_y = car_x, car_y
            if can_move and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                new_car_x -= 1
                if current_state == GROUND_MAPPING or current_state == TEACHING_MODE:
                    car_image = man_left_image
            if can_move and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                new_car_x += 1
                if current_state == GROUND_MAPPING or current_state == TEACHING_MODE:
                    car_image = man_right_image
            if can_move and (keys[pygame.K_UP] or keys[pygame.K_w]):
                new_car_y -= 1
                if current_state == GROUND_MAPPING or current_state == TEACHING_MODE:
                    car_image = man_back_image
            if can_move and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                new_car_y += 1
                if current_state == GROUND_MAPPING or current_state == TEACHING_MODE:
                    car_image = man_front_image

            # Check if the new position is within the screen boundaries and not a wall
            if current_state == GROUND_MAPPING:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT and (
                new_car_x, new_car_y) not in building_features:
                    car_x, car_y = new_car_x, new_car_y
            elif current_state == TEACHING_MODE:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT and (
                new_car_x, new_car_y) not in simple_walls_set:
                    car_x, car_y = new_car_x, new_car_y
            elif current_state == AERIAL_MAPPING:
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT:
                    car_x, car_y = new_car_x, new_car_y

            current_time = pygame.time.get_ticks()
            if (current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING) and showing_mapping_instructions:
                start_time = current_time - 0  # Keep resetting so timer doesn't tick
            time_left = max(0, starting_time * 1000 - (current_time - start_time))

            # Update count data for the heat map and timer
            if current_state == GROUND_MAPPING:
                bg = np.random.poisson(7)
                total_signal = 0
                for (msx, msy) in mapping_sources:
                    los = has_line_of_sight(car_x, car_y, msx, msy, building_features)
                    d2 = distance_squared(car_x, car_y, msx, msy)
                    if not los:
                        total_signal += np.random.poisson(5000 / d2)
                    else:
                        total_signal += np.random.poisson(10000 / d2)
                count_data[car_y, car_x] = min(10000, bg + total_signal)
            elif current_state == TEACHING_MODE:
                bg = np.random.poisson(7)
                line_of_sight = has_line_of_sight(car_x, car_y, source_x, source_y, simple_walls_set)
                if not line_of_sight:
                    count_data[car_y, car_x] = min(5000, bg + np.random.poisson(
                        5000 / distance_squared(car_x, car_y, source_x, source_y)))
                else:
                    count_data[car_y, car_x] = min(10000, bg + np.random.poisson(
                        10000 / distance_squared(car_x, car_y, source_x, source_y)))
            elif current_state == AERIAL_MAPPING:
                bg = np.random.poisson(7 / 3)
                total_signal = 0
                for (msx, msy) in mapping_sources:
                    total_signal += np.random.poisson(10000 / distance_squared_3D(car_x, car_y, msx, msy))
                count_data[car_y, car_x] = min(10000, bg + total_signal)

            # Track visited tiles and peak CPS for mapping modes
            if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING:
                visited_tiles.add((car_x, car_y))
                current_cps = count_data[car_y, car_x]
                if current_cps > peak_cps:
                    peak_cps = current_cps

            # Draw everything on the screen
            draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image)
            if current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING:
                draw_floor(floors, screen, floor_image, CELL_SIZE)
                for wall in building_features:
                    draw_wall(wall[0], wall[1], wall_image, GRID_SIZE, screen)
            if current_state == TEACHING_MODE:
                draw_source(source_x, source_y, CELL_SIZE, source_image, screen)
                if teaching_measured:
                    pygame.draw.rect(screen, (0, 255, 0),
                        (source_x * CELL_SIZE - 2, source_y * CELL_SIZE - 2,
                         CELL_SIZE + 4, CELL_SIZE + 4), 3)
                for wall in simple_walls:
                    draw_wall(wall[0], wall[1], wall_image, GRID_SIZE, screen)
            draw_car(car_x, car_y, car_image, CELL_SIZE, screen)

            if prev_pos != (car_x, car_y):
                counts = count_data[car_y, car_x]

            draw_counts(counts, car_x * GRID_SIZE, car_y * GRID_SIZE, screen)

            prev_pos = (car_x, car_y)

            # Draw minimap and stats HUD for mapping modes
            if (current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING) and not showing_mapping_instructions:
                # Coverage, peak CPS, and battery HUD
                font_hud = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)
                battery_pct = 100 * (time_left / 1000) / starting_time
                coverage_pct = 100 * len(visited_tiles) / max(1, total_floor_tiles)
                bat_color = (0, 200, 255) if battery_pct > 25 else (255, 80, 80)
                bat_text = font_hud.render(f"Battery: {battery_pct:.0f}%", True, bat_color)
                cov_text = font_hud.render(f"Coverage: {coverage_pct:.0f}%", True, (0, 255, 0))
                peak_text = font_hud.render(f"Peak CPS: {peak_cps:.0f}", True, (255, 200, 0))

                # Background panel for stats
                panel_w = max(bat_text.get_width(), cov_text.get_width(), peak_text.get_width()) + 20
                panel_h = bat_text.get_height() + cov_text.get_height() + peak_text.get_height() + 24
                panel_x = SCREEN_WIDTH - panel_w - 8
                panel_y = 8
                panel_bg = pygame.Surface((panel_w, panel_h))
                panel_bg.fill((0, 0, 0))
                panel_bg.set_alpha(160)
                screen.blit(panel_bg, (panel_x, panel_y))
                line_h = bat_text.get_height()
                screen.blit(bat_text, (panel_x + 8, panel_y + 4))
                screen.blit(cov_text, (panel_x + 8, panel_y + line_h + 8))
                screen.blit(peak_text, (panel_x + 8, panel_y + 2 * line_h + 12))

                # Live minimap in bottom-left
                minimap_w = 220
                minimap_h = int(minimap_w * GRID_HEIGHT / GRID_WIDTH)
                minimap_surface = pygame.Surface((minimap_w, minimap_h))
                minimap_surface.fill((30, 30, 30))

                scale_x = minimap_w / GRID_WIDTH
                scale_y = minimap_h / GRID_HEIGHT

                # Draw floor area
                for (fx, fy) in floors:
                    mx = int(fx * scale_x)
                    my = int(fy * scale_y)
                    pygame.draw.rect(minimap_surface, (60, 60, 60),
                        (mx, my, max(1, int(scale_x)), max(1, int(scale_y))))

                # Draw visited tiles with heat color
                # Scale differently for ground vs aerial (matches heatmap plot ranges)
                minimap_max = 50 if current_state == AERIAL_MAPPING else 500
                for (vx, vy) in visited_tiles:
                    cv = count_data[vy, vx]
                    intensity = min(1.0, cv / minimap_max)
                    r_val = int(255 * intensity)
                    b_val = int(255 * (1 - intensity))
                    mx = int(vx * scale_x)
                    my = int(vy * scale_y)
                    pygame.draw.rect(minimap_surface, (r_val, 50, b_val),
                        (mx, my, max(1, int(scale_x)), max(1, int(scale_y))))

                # Draw walls on minimap
                for (wx, wy) in building_features:
                    mx = int(wx * scale_x)
                    my = int(wy * scale_y)
                    pygame.draw.rect(minimap_surface, (180, 180, 180),
                        (mx, my, max(1, int(scale_x)), max(1, int(scale_y))))

                # Draw player position
                px = int(car_x * scale_x)
                py = int(car_y * scale_y)
                pygame.draw.circle(minimap_surface, (0, 255, 0), (px, py), 3)

                # Border and blit
                minimap_x = 8
                minimap_y = SCREEN_HEIGHT - minimap_h - 40
                border_rect = pygame.Rect(minimap_x - 2, minimap_y - 2, minimap_w + 4, minimap_h + 4)
                pygame.draw.rect(screen, (255, 255, 255), border_rect, 2)
                screen.blit(minimap_surface, (minimap_x, minimap_y))

                # Minimap label
                map_label = font_hud.render("Minimap", True, (255, 255, 255))
                screen.blit(map_label, (minimap_x, minimap_y - map_label.get_height() - 2))

            # Mapping mode instructions overlay
            if (current_state == GROUND_MAPPING or current_state == AERIAL_MAPPING) and showing_mapping_instructions:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(200)
                screen.blit(overlay, (0, 0))

                font_title = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 32)
                font_body = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)

                if current_state == GROUND_MAPPING:
                    title = font_title.render("Ground Mapping - Instructions", True, (255, 105, 180))
                    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 6))

                    instructions = [
                        "Welcome to Ground Mapping!",
                        "",
                        "One or more hidden radioactive sources",
                        "are inside the building. Your mission is",
                        "to map the radiation and locate them.",
                        "",
                        "Use WASD or arrow keys to move.",
                        "",
                        "The CPS (counts per second) display shows",
                        "the radiation level at your position.",
                        "Higher readings mean you are closer!",
                        "",
                        "Walls will attenuate the radiation,",
                        "so readings behind walls will be lower.",
                        "",
                        f"You have {settings['ground_time']} seconds - map as much",
                        "as you can before the battery runs out!",
                        "",
                        "Press SPACE or click to begin!",
                    ]
                else:
                    title = font_title.render("Aerial Mapping - Instructions", True, (255, 105, 180))
                    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 6))

                    instructions = [
                        "Welcome to Aerial Mapping!",
                        "",
                        "You are piloting a drone above the",
                        "building to survey the radiation from",
                        "the air.",
                        "",
                        "Use WASD or arrow keys to fly.",
                        "",
                        "The drone flies above the walls, so you",
                        "can move freely across the whole area.",
                        "",
                        "Readings from the air are weaker than",
                        "ground level due to the extra distance,",
                        "but you get a broader overview.",
                        "",
                        f"You have {settings['aerial_time']} seconds - cover as",
                        "much area as you can!",
                        "",
                        "Press SPACE or click to begin!",
                    ]

                y_offset = SCREEN_HEIGHT // 6 + title.get_height() + 30
                for line in instructions:
                    text = font_body.render(line, True, (255, 255, 255))
                    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                    y_offset += text.get_height() + 4

            # Teaching mode HUD
            if current_state == TEACHING_MODE:
                font_hud = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 18)

                # Hint bar at top
                hint = font_hud.render("Walk to the source and press SPACE to measure its spectrum", True, (255, 255, 255))
                hint_bg = pygame.Surface((hint.get_width() + 10, hint.get_height() + 6))
                hint_bg.fill((0, 0, 0))
                hint_bg.set_alpha(180)
                screen.blit(hint_bg, (SCREEN_WIDTH // 2 - hint.get_width() // 2 - 5, 5))
                screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 8))

                # Proximity prompt
                if abs(car_x - source_x) <= 1 and abs(car_y - source_y) <= 1:
                    prompt = font_hud.render("Press SPACE to measure spectrum!", True, (255, 255, 0))
                    prompt_bg = pygame.Surface((prompt.get_width() + 10, prompt.get_height() + 6))
                    prompt_bg.fill((0, 0, 0))
                    prompt_bg.set_alpha(200)
                    screen.blit(prompt_bg, (SCREEN_WIDTH // 2 - prompt.get_width() // 2 - 5, 35))
                    screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 38))

                # Show instruction overlay
                if showing_instructions:
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.fill((0, 0, 0))
                    overlay.set_alpha(200)
                    screen.blit(overlay, (0, 0))

                    font_title = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 32)
                    font_body = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)

                    title = font_title.render("Teaching Mode - Instructions", True, (255, 105, 180))
                    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 6))

                    instructions = [
                        "Welcome to Teaching Mode!",
                        "",
                        "A radioactive source is placed in the centre",
                        "of the map (marked with a trefoil symbol).",
                        "",
                        "Use WASD or arrow keys to move your character.",
                        "",
                        "The CPS (counts per second) display shows the",
                        "radiation intensity at your current position.",
                        "Notice how it increases as you get closer!",
                        "",
                        "Walk next to the source and press SPACE to",
                        "measure its gamma-ray spectrum.",
                        "",
                        "Walls block some radiation - compare readings",
                        "on each side of a wall.",
                        "",
                        "Press SPACE or click to begin!",
                    ]

                    y_offset = SCREEN_HEIGHT // 6 + title.get_height() + 30
                    for line in instructions:
                        text = font_body.render(line, True, (255, 255, 255))
                        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                        y_offset += text.get_height() + 4

                # Show spectrum overlay
                if showing_teaching_spectrum and teaching_spectrum_surface is not None:
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.fill((0, 0, 0))
                    overlay.set_alpha(150)
                    screen.blit(overlay, (0, 0))
                    sp_x = (SCREEN_WIDTH - teaching_spectrum_surface.get_width()) // 2
                    sp_y = (SCREEN_HEIGHT - teaching_spectrum_surface.get_height()) // 2
                    screen.blit(teaching_spectrum_surface, (sp_x, sp_y))
                    dismiss = font_hud.render("Press SPACE or click to close", True, (255, 255, 255))
                    screen.blit(dismiss, (SCREEN_WIDTH // 2 - dismiss.get_width() // 2,
                                          sp_y + teaching_spectrum_surface.get_height() + 10))

            # Check if the time is up
            if time_left <= 0:
                if current_state == GROUND_MAPPING:
                    extension = 'ground'
                elif current_state == AERIAL_MAPPING:
                    extension = 'aerial'
                current_state = GAME_OVER

        if current_state == SPECTRUM_MODE:
            if not showing_spectrum and not showing_spectrum_instructions:
                new_car_x, new_car_y = car_x, car_y
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    new_car_x -= 1
                    car_image = man_left_image
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    new_car_x += 1
                    car_image = man_right_image
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    new_car_y -= 1
                    car_image = man_back_image
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    new_car_y += 1
                    car_image = man_front_image
                if 0 <= new_car_x < GRID_WIDTH and 0 <= new_car_y < GRID_HEIGHT:
                    car_x, car_y = new_car_x, new_car_y

            # Draw the world
            draw_grass(GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, screen, grass_image)

            # Draw sources with measured highlight
            for i, (sx, sy, isotope) in enumerate(spectrum_sources):
                draw_source(sx, sy, CELL_SIZE, source_image, screen)
                if i in measured_sources:
                    pygame.draw.rect(screen, (0, 255, 0),
                        (sx * CELL_SIZE - 2, sy * CELL_SIZE - 2,
                         CELL_SIZE + 4, CELL_SIZE + 4), 3)

            draw_car(car_x, car_y, car_image, CELL_SIZE, screen)

            # Draw HUD text
            font_hud = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 18)

            # Hint text
            hint = font_hud.render("Walk to a source and press SPACE to measure", True, (255, 255, 255))
            hint_bg = pygame.Surface((hint.get_width() + 10, hint.get_height() + 6))
            hint_bg.fill((0, 0, 0))
            hint_bg.set_alpha(180)
            screen.blit(hint_bg, (SCREEN_WIDTH // 2 - hint.get_width() // 2 - 5, 5))
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 8))

            # Score text
            score_text = font_hud.render(
                f"Sources measured: {len(measured_sources)}/{len(spectrum_sources)}",
                True, (255, 255, 0))
            score_bg = pygame.Surface((score_text.get_width() + 10, score_text.get_height() + 6))
            score_bg.fill((0, 0, 0))
            score_bg.set_alpha(180)
            screen.blit(score_bg, (5, SCREEN_HEIGHT - score_text.get_height() - 15))
            screen.blit(score_text, (10, SCREEN_HEIGHT - score_text.get_height() - 12))

            # Proximity prompt
            for i, (sx, sy, isotope) in enumerate(spectrum_sources):
                if abs(car_x - sx) <= 1 and abs(car_y - sy) <= 1:
                    prompt = font_hud.render("Press SPACE to measure!", True, (255, 255, 0))
                    prompt_bg = pygame.Surface((prompt.get_width() + 10, prompt.get_height() + 6))
                    prompt_bg.fill((0, 0, 0))
                    prompt_bg.set_alpha(200)
                    screen.blit(prompt_bg, (SCREEN_WIDTH // 2 - prompt.get_width() // 2 - 5, 35))
                    screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 38))
                    break

            # Draw spectrum overlay if showing
            if showing_spectrum and spectrum_surface is not None:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(150)
                screen.blit(overlay, (0, 0))
                sp_x = (SCREEN_WIDTH - spectrum_surface.get_width()) // 2
                sp_y = (SCREEN_HEIGHT - spectrum_surface.get_height()) // 2
                screen.blit(spectrum_surface, (sp_x, sp_y))
                dismiss = font_hud.render("Press SPACE or click to close", True, (255, 255, 255))
                screen.blit(dismiss, (SCREEN_WIDTH // 2 - dismiss.get_width() // 2,
                                      sp_y + spectrum_surface.get_height() + 10))

            # Draw spectrum mode instructions overlay
            if showing_spectrum_instructions:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(200)
                screen.blit(overlay, (0, 0))

                font_title = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 32)
                font_body = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)

                title = font_title.render("Spectrum ID - Instructions", True, (255, 105, 180))
                screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 6))

                instructions = [
                    "Welcome to Spectrum ID Mode!",
                    "",
                    "Several radioactive sources are scattered",
                    "across the map (marked with trefoil symbols).",
                    "",
                    "Use WASD or arrow keys to walk around.",
                    "",
                    "When you are near a source, press SPACE",
                    "to measure its gamma-ray spectrum.",
                    "",
                    "Each source could be Cs-137, Co-60,",
                    "Eu-152, or Natural Uranium.",
                    "",
                    "Try to identify each source from its",
                    "characteristic energy peaks!",
                    "",
                    "Measured sources will be highlighted green.",
                    "",
                    "Press SPACE or click to begin!",
                ]

                y_offset = SCREEN_HEIGHT // 6 + title.get_height() + 30
                for line in instructions:
                    text = font_body.render(line, True, (255, 255, 255))
                    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                    y_offset += text.get_height() + 4

        if current_state == GAME_OVER:
            if heatmap_image is None:
                is_aerial = (extension == "aerial")
                max_v = 150 if is_aerial else 10000
                heatmap_image = render_heatmap_surface(
                    SCREEN_WIDTH, SCREEN_HEIGHT, count_data, floors,
                    building_features, max_v, source_positions=None, is_aerial=is_aerial)
                heatmap_source_image = render_heatmap_surface(
                    SCREEN_WIDTH, SCREEN_HEIGHT, count_data, floors,
                    building_features, max_v, source_positions=mapping_sources, is_aerial=is_aerial)
                # Also save smaller versions for Show Maps
                last_heatmap_data[extension] = {
                    'count_data': count_data.copy(),
                    'floors': list(floors),
                    'walls': set(building_features),
                    'max_v': max_v,
                    'source_positions': list(mapping_sources),
                    'is_aerial': is_aerial,
                }

        if current_state == SHOW_SOURCE:
            screen.blit(heatmap_source_image, (0, 0))
        elif current_state == GAME_OVER:
            screen.blit(heatmap_image, (0, 0))

        if current_state == GAME_OVER:
            for button in end_game_buttons:
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
            for button in shown_source_buttons:
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
            for button in shown_source_buttons:
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

            map_disp_w = SCREEN_WIDTH // 2
            map_disp_h = int(SCREEN_HEIGHT / 1.5)
            if 'ground' in last_heatmap_data:
                d = last_heatmap_data['ground']
                ground_map = render_heatmap_surface(
                    map_disp_w, map_disp_h, d['count_data'], d['floors'],
                    d['walls'], d['max_v'], d['source_positions'], d['is_aerial'])
            else:
                ground_map = pygame.Surface((map_disp_w, map_disp_h))
                ground_map.fill((30, 30, 30))
                no_data_font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)
                no_data = no_data_font.render("No data yet", True, (180, 180, 180))
                ground_map.blit(no_data, (map_disp_w // 2 - no_data.get_width() // 2,
                                          map_disp_h // 2 - no_data.get_height() // 2))
            if 'aerial' in last_heatmap_data:
                d = last_heatmap_data['aerial']
                aerial_map = render_heatmap_surface(
                    map_disp_w, map_disp_h, d['count_data'], d['floors'],
                    d['walls'], d['max_v'], d['source_positions'], d['is_aerial'])
            else:
                aerial_map = pygame.Surface((map_disp_w, map_disp_h))
                aerial_map.fill((30, 30, 30))
                no_data_font = pygame.font.Font("font/PixeloidMono-d94EV.ttf", 20)
                no_data = no_data_font.render("No data yet", True, (180, 180, 180))
                aerial_map.blit(no_data, (map_disp_w // 2 - no_data.get_width() // 2,
                                          map_disp_h // 2 - no_data.get_height() // 2))

            screen.blit(ground_map, (0, SCREEN_HEIGHT // 6))
            screen.blit(aerial_map, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))

        if current_state == CALL_MAIN:
            current_state = MENU

        if current_state == QUIT:
            pygame.quit()
            sys.exit()

        if current_state == TEACHING_MODE or current_state == AERIAL_MAPPING or current_state == GROUND_MAPPING or current_state == SPECTRUM_MODE:
            for button in in_game_buttons:
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

        pygame.display.update()

        if current_state == GROUND_MAPPING or current_state == TEACHING_MODE or current_state == SPECTRUM_MODE:
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
    #screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.RESIZABLE)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    main(screen)
