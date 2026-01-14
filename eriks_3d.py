import pygame

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Transformation:
    def transform(self, v):
        """
            Transforms a given vector to a new vector
        """
        return Vector3(v.x, v.y, v.z)

class Translate(Transformation):
    def __init__(self, d_x, d_y, d_z):
        super().__init__()
        self.d_x = d_x
        self.d_y = d_y
        self.d_z = d_z

    def transform(self, v):
        return Vector3(v.x + self.d_x, v.y + self.d_y, v.z + self.d_z)

class Scale(Transformation):
    def __init__(self, s_x, s_y, s_z):
        super().__init__()
        self.s_x = s_x
        self.s_y = s_y
        self.s_z = s_z

    def transform(self, v):
        return Vector3(v.x * self.s_x, v.y * self.s_y, v.z * self.s_z)


class Object:
    def __init__(self):
        self._projected_vertexes = []
        self._transformations = []

    def reset_transformation(self):
        self._transformations = []

    def add_transformation(self, t):
        self._transformations.append(t)

    def update_projection(self, d, screen_center):
        # TODO optimize with a fixed list size later, as we know the size of the list
        self._projected_vertexes = []
        for v in self.vertexes():
            r_v = v
            for t in self._transformations:
                r_v = t.transform(r_v)
            self._projected_vertexes.append(projection(d, screen_center, r_v))

    def projected_vertex(self, index):
        return self._projected_vertexes[index]

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

class FlatQuad(Object):
    def __init__(self, x, y, z, w, h):
        super().__init__()
        self._vs = [Vector3(x, y, z), Vector3(x+w, y, z), Vector3(x+w, y+w, z), Vector3(x, y+w, z)]

    def trigons(self):
        return [(0, 1, 3), (1, 2, 3)]

    def vertexes(self):
        return self._vs

def projection(d, screen_center, v):
    f = d/(v.z+d)
    return (screen_center[0] + v.x*f, screen_center[1] + v.y*f)

def render_objects(screen, d, objects):
    w = screen.get_width()
    h = screen.get_height()

    screen_center = (w/2, h/2)

    for o in objects:
        o.update_projection(d, screen_center)
        if o.visible():
            ts = o.trigons()
            for t in ts:
                for i in range(3):
                    pygame.draw.line(screen, (255, 255, 255), o.projected_vertex(t[i]), o.projected_vertex(t[(i+1) % 3]))

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

objects = [FlatQuad(-400, -300, 100, 800, 600)]

delta = 10
z = 100

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

    z += delta
    if z > 1000 or z < 100:
        delta = -delta

    objects[0].reset_transformation()
    objects[0].add_transformation(Scale(z/1000.0, z/1000.0, z/1000.0))

pygame.quit()
