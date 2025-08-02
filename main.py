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

BG_COLOR = (10, 10, 20)
NEUTRON_COLOR = (0, 255, 255)

clock = pygame.time.Clock()
FPS = 60

NEUTRON_RADIUS = 4
NEUTRON_SPEED = 1
GRID_CELL_SIZE = 40

RIGHT = 0
DOWN = math.pi / 2
LEFT = math.pi
UP = 3 * math.pi / 2
UP_RIGHT = math.pi / 4
DOWN_RIGHT = math.pi / 4 + math.pi / 2
DOWN_LEFT = 3 * math.pi / 4
UP_LEFT = 5 * math.pi / 4

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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, (0, 255, 0), (self.x, self.y), 6)
        else:
            pygame.draw.circle(surface, (100, 100, 100), (self.x, self.y), 6)


uranium_nuclei = []
for i in range(0, 16):
        for j in range(0,12):
            uranium_nuclei.append(Uranium(XgridToPos(i+2), YgridToPos(j+2)))

neutrons = [Neutron(XgridToPos(10), YgridToPos(8), RIGHT)]

paused = True

running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
                
    for nucleus in uranium_nuclei:
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
                if dist < 12 + 4:
                    nucleus.active = False
                    collision_sound.play()

                    for _ in range(3):
                        random_angle = random.uniform(0, 2 * math.pi)
                        neutrons.append(Neutron(nucleus.x, nucleus.y, random_angle))

                    neutrons.remove(neutron)
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