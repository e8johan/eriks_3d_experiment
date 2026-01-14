import pygame

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Object:
    def vertexes(self):
        return []

class Blupp(Object):
    def __init__(self, z):
        self.z = z

    def vertexes(self):
        return [Vector3(-100, -100, self.z), Vector3(100, -500, self.z), Vector3(400, 300, self.z)]


def projection(d, screen_center, v):
    return (screen_center[0] + v.x*d/(v.z+d), screen_center[1] + v.y*d/(v.z+d))

def render_objects(screen, d, objects):
    w = screen.get_width()
    h = screen.get_height()

    screen_center = (w/2, h/2)

    for o in objects:
        vs = o.vertexes()
        for i in range(len(vs)):
            pygame.draw.line(screen, (255, 255, 255), projection(d, screen_center, vs[i]), projection(d, screen_center, vs[(i+1) % len(vs)]))


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

objects = [Blupp(100), Blupp(200)]

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    render_objects(screen, 640, objects)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
