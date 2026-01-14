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
    def __init__(self):
        pass

    def vertexes(self):
        return [Vector3(100, 100, 100), Vector3(100, 500, 100), Vector3(400, 300, 100)]


def render_objects(screen, objects):
    for o in objects:
        vs = o.vertexes()
        for i in range(len(vs)):
            pygame.draw.line(screen, (255, 255, 255), (vs[i].x, vs[i].y), (vs[(i+1) % len(vs)].x, vs[(i+1) % len(vs)].y))


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

objects = [Blupp()]

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    render_objects(screen, objects)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
