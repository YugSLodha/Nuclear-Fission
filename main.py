import pygame
import sys
import random
import math

pygame.init()

pygame.mixer.init()
collision_sound = pygame.mixer.Sound("collision.mp3")

pygame.font.init()
font = pygame.font.SysFont(None, 24)

WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nuclear Fission Simulation")

FPS = 60
sim_time = 0
GRID_CELL_SIZE = 20

NEUTRON_RADIUS = 4
NEUTRON_SPEED = 1
NEUTRON_COLOR = (0, 255, 255)

URANIUM_RADIUS = 6
PURITY = 0.05
NON_FISSILE = 0.01
REACTIVATION_DELAY_MIN = 1
REACTIVATION_DELAY_MAX = 10
COLLISION_DISTANCE = URANIUM_RADIUS + NEUTRON_RADIUS

BG_COLOR = (10, 10, 20)
FISSILE_COLOR = (0, 255, 0)
NONFISSILE_COLOR = (100, 100, 100)
INACTIVE_COLOR = (21, 71, 52)

RIGHT = 0
DOWN = math.pi / 2
LEFT = math.pi
UP = 3 * math.pi / 2
UP_RIGHT = math.pi / 4
DOWN_RIGHT = math.pi / 4 + math.pi / 2
DOWN_LEFT = 3 * math.pi / 4
UP_LEFT = 5 * math.pi / 4

clock = pygame.time.Clock()

def XgridToPos(gridx):
    return gridx*GRID_CELL_SIZE

def YgridToPos(gridy):
    return gridy*GRID_CELL_SIZE

class Neutron:
    def __init__(self, x, y, angle=None):
        self.x = x
        self.y = y
        if angle is None:
            angle = random.uniform(0, 2 * math.pi)
        self.angle = angle
        self.dx = math.cos(angle) * NEUTRON_SPEED
        self.dy = math.sin(angle) * NEUTRON_SPEED

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, NEUTRON_COLOR, (int(self.x), int(self.y)), NEUTRON_RADIUS)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class Uranium:
    def __init__(self, x, y, fissile=True):
        self.x = x
        self.y = y
        self.fissile = fissile

        if self.fissile:
            self.active = random.random() < PURITY
        else:
            self.active = True

        self.reactivation_time = None
        self.deactivated_time = None

    def draw(self, surface):
        if self.active:
            if self.fissile:
                color = FISSILE_COLOR
            else:
                color = NONFISSILE_COLOR
        else:
            color = INACTIVE_COLOR
        pygame.draw.circle(surface, color, (self.x, self.y), URANIUM_RADIUS)

    def deactivate(self, current_time):
        self.active = False
        delay = random.uniform(REACTIVATION_DELAY_MIN, REACTIVATION_DELAY_MAX)
        self.reactivation_time = current_time + delay

    def try_reactivate(self, current_time):
        if not self.active and self.reactivation_time is not None:
            if current_time >= self.reactivation_time:
                self.active = True
                self.reactivation_time = None


uranium_nuclei = []
for i in range(0, 36):
        for j in range(0,28):
            isfissile = random.random() > NON_FISSILE
            uranium_nuclei.append(Uranium(XgridToPos(i+2), YgridToPos(j+2), isfissile))
neutrons = [Neutron(XgridToPos(20), YgridToPos(16), RIGHT)]
paused = True
running = True
while running:
    clock.tick(FPS)
    delta_time = clock.get_time() / 1000.0  # Convert milliseconds to seconds
    if not paused:
        sim_time += delta_time
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    for nucleus in uranium_nuclei:
        nucleus.try_reactivate(sim_time)
        nucleus.draw(screen)

    for neutron in neutrons[:]:
        neutron.draw(screen)
        
    if not paused:
        for neutron in neutrons[:]:
            neutron.move()

            if neutron.off_screen():
                neutrons.remove(neutron)

        for nucleus in uranium_nuclei:
            if not nucleus.active:
                continue

            for neutron in neutrons[:]:
                dist = math.hypot(neutron.x - nucleus.x, neutron.y - nucleus.y)
                if dist < COLLISION_DISTANCE:
                    nucleus.deactivate(sim_time)
                    neutrons.remove(neutron)
                    
                    if nucleus.fissile:
                        collision_sound.play()
                        for _ in range(3):
                            random_angle = random.uniform(0, 2 * math.pi)
                            neutrons.append(Neutron(nucleus.x, nucleus.y, random_angle))
                    break
    else:
        pause_text = font.render("Paused", True, (255, 0, 0))
        text_rect = pause_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
        screen.blit(pause_text, text_rect)

    neutron_count = len(neutrons)
    text = font.render(f"Neutrons: {neutron_count}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    pygame.display.flip()

pygame.quit()
sys.exit()