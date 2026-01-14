import pygame

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Object:
    def vertexes(self):
        """
            Return a list of Vector3 representing the vertexes of the object
        """
        return []

    def trigons(self):
        """
            Return a list of tripple-Tuples with trigon corners
        """
        return []

    def visible(self):
        """
            Returns True if the object is visible
        """
        return True

class Blupp(Object):
    def __init__(self, z):
        self.z = z

    def trigons(self):
        return [(0, 1, 2)]

    def vertexes(self):
        return [Vector3(-100, -100, self.z), Vector3(100, -500, self.z), Vector3(400, 300, self.z)]


def projection(d, screen_center, v):
    return (screen_center[0] + v.x*d/(v.z+d), screen_center[1] + v.y*d/(v.z+d))

def render_objects(screen, d, objects):
    w = screen.get_width()
    h = screen.get_height()

    screen_center = (w/2, h/2)

    for o in objects:
        if o.visible():
            vs = o.vertexes()
            ts = o.trigons()
            for t in ts:
                for i in range(3):
                    pygame.draw.line(screen, (255, 255, 255), projection(d, screen_center, vs[t[i]]), projection(d, screen_center, vs[t[(i+1) % len(vs)]]))


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

objects = []
for i in range(10):
    objects.append(Blupp(i*100))

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
