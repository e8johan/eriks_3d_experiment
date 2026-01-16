import cProfile

from math import sin, cos, sqrt
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

class Rotation(Transformation):
    def __init__(self, r_x, r_y, r_z):
        super().__init__()
        self.r_x = r_x
        self.r_y = r_y
        self.r_z = r_z

    def transform(self, v):
        s1 = sin(self.r_y)
        c1 = cos(self.r_y)
        s2 = sin(self.r_x)
        c2 = cos(self.r_x)
        s3 = sin(self.r_z)
        c3 = cos(self.r_z)

        Xv = v.x*(s1*s2*s3 + c1*c3) + v.y*(c2*s3) + v.z*(c1*s2*s3 - c3*s1)
        Yv = v.x*(c3*s1*s2 - c1*s3) + v.y*(c2*c3) + v.z*(c1*c3*s2 + s1*s3)
        Zv = v.x*(c1*s2*s3 - c3*s1) + v.y*(-s2)   + v.z*(c1*c2)

        return Vector3(Xv, Yv, Zv)

class Projection(Transformation):
    def __init__(self, d):
        super().__init__()
        self.d = d

    def transform(self, v):
        f = self.d/(v.z+self.d)
        return Vector3(v.x*f, v.y*f, v.z)

class Object:
    def __init__(self):
        self._transformed_vertexes = []
        self._projected_vertexes = []
        self._normals = []
        self._transformations = []

    def reset_transformation(self):
        self._transformations = []

    def add_transformation(self, t):
        self._transformations.append(t)

    def update_normals(self):
        # TODO optimize with a fixed list size later, as we know the size of the list
        self._normals = []
        for t in self.trigons():
            X1 = self._transformed_vertexes[t[0]].x
            Y1 = self._transformed_vertexes[t[0]].y
            Z1 = self._transformed_vertexes[t[0]].z
            X2 = self._transformed_vertexes[t[1]].x
            Y2 = self._transformed_vertexes[t[1]].y
            Z2 = self._transformed_vertexes[t[1]].z
            X3 = self._transformed_vertexes[t[2]].x
            Y3 = self._transformed_vertexes[t[2]].y
            Z3 = self._transformed_vertexes[t[2]].z

            normal = ((Y1-Y2)*(Z1-Z3) - (Z1-Z2)*(Y1-Y3), -((Z1-Z2)*(X1-X3) - (X1-X2)*(Z1-Z3)), (X1-X2)*(Y1-Y3) - (Y1-Y2)*(X1-X3))
            self._normals.append(normal)

    def update_transformation(self):
        # TODO optimize with a fixed list size later, as we know the size of the list
        self._transformed_vertexes = []
        for v in self.vertexes():
            t_v = v
            for t in self._transformations:
                t_v = t.transform(t_v)
            self._transformed_vertexes.append(t_v)

    def update_projection(self, d, screen_center):
        # TODO optimize with a fixed list size later, as we know the size of the list
        self._projected_vertexes = []
        for v in self._transformed_vertexes:
            self._projected_vertexes.append( (v.x + screen_center[0], v.y + screen_center[1]) )

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

    def trigon_visible(self, index):
        """
            Returns True if the trigon for the given index is visible
        """
        if self._normals[index][2] < 0:
            return True
        else:
            return False

    def normal(self, index):
        return self._normals[index]

    def visible(self):
        """
            Returns True if the object is visible
        """
        return True

class Box(Object):
    def __init__(self, x, y, z, w, h, d):
        super().__init__()
        self._vs = [Vector3(x, y, z), Vector3(x+w, y, z), Vector3(x+w, y+w, z), Vector3(x, y+w, z), Vector3(x, y, z+d), Vector3(x+w, y, z+d), Vector3(x+w, y+w, z+d), Vector3(x, y+w, z+d)]

    def trigons(self):
        return [(0, 3, 1), (1, 3, 2), # Front
                (4, 5, 7), (5, 6, 7), # Back
                (0, 1, 4), (1, 5, 4), # Top
                (1, 2, 5), (2, 6, 5), # Right
                (3, 7, 2), (7, 6, 2), # Bottom
                (0, 4, 3), (3, 4, 7)] # Left

    def vertexes(self):
        return self._vs

class FlatQuad(Object):
    def __init__(self, x, y, z, w, h):
        super().__init__()
        self._vs = [Vector3(x, y, z), Vector3(x+w, y, z), Vector3(x+w, y+w, z), Vector3(x, y+w, z)]

    def trigons(self):
        return [(0, 1, 3), (1, 2, 3)]

    def vertexes(self):
        return self._vs

class StlMesh(Object):
    def __init__(self, filename):
        super().__init__()
        self._ts = []
        self._vs = []

        # State-machine to load a solid
        #
        #   This loader is quite forgiving, but it outputs unexpected file contents
        with open(filename, 'r') as f:
            state = 'in file'
            for raw_line in f:
                line = raw_line.strip()
                match state:
                    case 'in file':
                        if line.startswith('solid ') or line == 'solid':
                            state = 'in solid'
                        else:
                            print(state, line)
                    case 'in solid':
                        if line.startswith('facet normal '):
                            pass
                        elif line.startswith('outer loop'):
                            state = 'in loop'
                        elif line == 'endsolid':
                            state = 'in file'
                        else:
                            print(state, line)
                    case 'in loop':
                        if line == 'endfacet':
                            vss = len(self._vs)
                            self._ts.append( (vss-3, vss-2, vss-1) )
                            state = 'in solid'
                        elif line == 'outer loop' or line == 'endloop':
                            pass
                        elif line.startswith('vertex '):
                            parts = line.split(' ')
                            self._vs.append( Vector3(float(parts[1]), float(parts[2]), float(parts[3])) )
                        else:
                            print(state, line)

    def trigons(self):
        return self._ts

    def vertexes(self):
        return self._vs

def render_objects(screen, d, objects):
    w = screen.get_width()
    h = screen.get_height()

    screen_center = (w/2, h/2)

    for o in objects:
        o.update_transformation()
        o.update_projection(d, screen_center)
        if o.visible():
            o.update_normals()
            ts = o.trigons()
            for i in range(len(ts)):
                if o.trigon_visible(i):
                    t = ts[i]
                    n = o.normal(i)
                    shade = n[0]/sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])/2+0.5
                    pygame.draw.polygon(screen, (255*shade, 255*shade, 255*shade), (o.projected_vertex(t[0]), o.projected_vertex(t[1]), o.projected_vertex(t[2])))
                    # pygame.draw.lines(screen, (255, 0, 0), True, (o.projected_vertex(t[0]), o.projected_vertex(t[1]), o.projected_vertex(t[2])))

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

objects = [Box(-100, -100, 100, 200, 200, 200), StlMesh("Owl_Facing_Left_fixed_sc.stl")]

projection_transformation = Projection(640)

delta = 10
z = 0

profile = cProfile.Profile()
profile.enable()

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
    if z > 360 or z < 0:
        delta = -delta
        running = False

    objects[0].reset_transformation()
    objects[0].add_transformation(Translate(0, 0, -200))
    objects[0].add_transformation(Rotation(z*3.14/90.0, 0, z*3.14/180.0))
    objects[0].add_transformation(Translate(0, 0, 200))
    objects[0].add_transformation(projection_transformation)

    objects[1].reset_transformation()
    objects[1].add_transformation(Scale(5.0, 5.0, 5.0))
    objects[1].add_transformation(Rotation(0, z*3.14/180.0, z*3.14/90.0))
    objects[1].add_transformation(Translate(-350, 0, 150))
    objects[1].add_transformation(projection_transformation)

profile.disable()
profile.dump_stats("profile_stats")

pygame.quit()
