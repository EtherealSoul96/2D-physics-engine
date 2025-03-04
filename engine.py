

from math import pi, tau, sin, cos, copysign, inf
from random import random, randint, seed
from time import time, sleep


import pyglet
from pyglet.window import key, mouse

from engine_parts import simple_gl
from engine_parts.simple_gl import *
from engine_parts.tom_lib.vectors import Vec2, Angle, vector_list_to_normal_list
from engine_parts.tom_lib.useful_stuff import CircularList, time_flag, print_time_flag, my_sum, my_avg

from engine_parts.get_circle_lines_resolution import get_arc_lines_resolution
from engine_parts.triangulation import triangulate
from engine_parts.get_triangle_m_and_I import get_triangle_m_and_I



number_of_objects = 20
draw_fill = True
draw_border = True

seed(5)



# engine parts:
#   collision detection
#   collision response
#   drawing
#   CM, I calculator
#   common object shapes



# Object classes:

class PolarVec2:
    def __init__(self, a, r):
        self.a = a
        self.r = r

    def to_vec2(self):
        return Vec2(cos(self.a), sin(self.a)) * self.r

    def rotated(self, a):
        return PolarVec2(self.a + a, self.r)

    @staticmethod
    def from_Vec2(v):
        return PolarVec2(v.angle(), abs(v))


class SolidObject:
    def __init__(self, p=Vec2(0, 0), v=Vec2(0, 0), a=0, w=0, m=1, I=1, b=1, density=1, fr_e=1, fr_d=1, parts=[]):

        print("v is ", v)

        self.p = p ; self.a = a
        self.v = v ; self.w = w
        self.m = m ; self.I = I

        self.density = density

        self.b = b
        self.fr_e = fr_e
        self.fr_d = fr_d

        self.points = []
        self.triangles_indices = []


        self.create_points()
        self.triangulate()
        self.calculate_m_and_I()
        self.center_points()

        print(parts)
        for part in self.parts:
            part.bind(self)
            part.update()

    def center_points(self):
        self.points = [point - self.p for point in self.points]
        print(self.points)

    def move(self):
        self.p += self.v
        self.a += self.w

        for part in self.parts:
            part.update()

    def apply_impulse(self, p, j):
        self.v += j / self.m
        r = p - self.p
        self.w += (r.x * j.y - r.y * j.x) / self.I

    def create_points(self):
        for part in self.parts:

            if type(part) == Line:
                self.points.append(part.p0)

            elif type(part) == Arc_old:
                if part.r == 0:
                    continue
                a_diff = float(part.a1 - part.a0)
                if a_diff == 0:
                    a_diff = tau
                n = get_arc_lines_resolution(part.r, a_diff, 0.25)
                for i in range(n):
                    a = part.a0 + (i/n) * a_diff
                    self.points.append(part.base_p + PolarVec2(a, part.r).to_vec2())
            else:
                print("type is not Line or Arc")

    def triangulate(self):
        print(self.points)
        self.triangles_indices = triangulate(self.points)

    def calculate_m_and_I(self):

        total_mass = 0
        total_moi = 0

        obj_cm = Vec2(0, 0)

        for t_i in range(0, len(self.triangles_indices), 3):
            p0 = self.points[self.triangles_indices[t_i + 0]]
            p1 = self.points[self.triangles_indices[t_i + 1]]
            p2 = self.points[self.triangles_indices[t_i + 2]]

            m, I = get_triangle_m_and_I(p0, p1, p2)
            trig_cm = (p0 + p1 + p2) / 3

            obj_cm += m * trig_cm
            total_mass += m
            total_moi += I

        obj_cm /= total_mass

        for t_i in range(0, len(self.triangles_indices), 3):
            p0 = self.points[self.triangles_indices[t_i + 0]]
            p1 = self.points[self.triangles_indices[t_i + 1]]
            p2 = self.points[self.triangles_indices[t_i + 2]]

            m, I = get_triangle_m_and_I(p0, p1, p2)
            trig_cm = (p0 + p1 + p2) / 3

            total_moi += m * (trig_cm - obj_cm).abs_2()


        total_mass *= self.density
        total_moi  *= self.density


        print(self.triangles_indices)
        print(total_mass, total_moi)

        self.p = obj_cm
        self.m = total_mass
        self.I = total_moi



    def bind_parts(self):
        for part in self.parts:
            part.bind(self)

    def add_line(self, p0, p1):
        self.parts.append(Line(self, p0, p1))
    def add_arc(self, p, a0, a1, r):
        self.parts.append(Arc_old(self, p, a0, a1, r))

class ConvexPolygon(SolidObject):
    def __init__(self, points, *args, **kwargs):

        self.parts = []
        points = CircularList(points)
        for i in range(len(points)):

            p0 = points[i]
            p1 = points[i+1]
            p2 = points[i+2]

            self.add_line(p0, p1)
            self.add_arc(
                p1,
                (p1-p0).angle() - pi / 2,
                (p2-p1).angle() - pi / 2,
                0
            )

        super().__init__(*args, **kwargs)
        # super().bind_parts()

class FatLine(SolidObject):

    def __init__(self, p0, p1, r, *args, **kwargs):

        self.parts = []

        cm = (p0 + p1) / 2
        normal_vec = (p1 - p0).normalized().rotated_270() * r
        a0 = (p1 - p0).angle()

        self.add_line((p0 ) + normal_vec, ((p1) + normal_vec)),
        self.add_arc ((p1 ), a0 - pi / 2, a0 + pi / 2, r),
        self.add_line((p1 ) - normal_vec, ((p0) - normal_vec)),
        self.add_arc ((p0 ), a0 + pi / 2, a0 - pi / 2, r),

        super().__init__(p=cm, *args, **kwargs)
        print("cm", cm)

    def add_line(self, p0, p1):
        self.parts.append(Line(self, p0, p1))
    def add_arc(self, p, a0, a1, r):
        self.parts.append(Arc_old(self, p, a0, a1, r))


class ObjectPart:

    id = 0

    def __init__(self, parent):

        self.id = ObjectPart.id
        ObjectPart.id += 1

        self.parent = parent

        self.min_x = Vertex(self, 0, 0)
        self.max_x = Vertex(self, 0, 1)
        self.min_y = Vertex(self, 0, 0)
        self.max_y = Vertex(self, 0, 1)

    def bind(self, parent):
        self.parent = parent

    def update(self):
        pass

    def update_collision_area(self):
        pass

class Line(ObjectPart):
    def __init__(self, parent, p0: Vec2, p1: Vec2):

        self.base_p0 = p0 ; self.p0 = p0
        self.base_p1 = p1 ; self.p1 = p1

        super().__init__(parent)

    def bind(self, parent):
        # be careful if the parent has an initial a != 0
        self.parent = parent
        self.base_p0 = self.p0 - parent.p
        self.base_p1 = self.p1 - parent.p
        print("binding line", self.parent.p, self.p0, self.p1)

    def update(self):
        self.p0 = self.parent.p + self.base_p0.rotated(self.parent.a)
        self.p1 = self.parent.p + self.base_p1.rotated(self.parent.a)

        self.update_collision_area()

    def update_collision_area(self):
        self.max_x.value = max(self.p0.x, self.p1.x) + 10
        self.max_y.value = max(self.p0.y, self.p1.y) + 10
        self.min_x.value = min(self.p0.x, self.p1.x) - 10
        self.min_y.value = min(self.p0.y, self.p1.y) - 10

class Arc_old(ObjectPart):
    def __init__(self, parent, p: Vec2, a0: Angle, a1: Angle, r):

        # calculate the points of both extremes
        # get the point in the middle
        # make it the center of the hitbox "circle"

        self.base_p  = p  ; self.p  = p  # parent.p + self.base_p.rotated(parent.a).to_vec2()
        self.base_a0 = a0 ; self.a0 = a0
        self.base_a1 = a1 ; self.a1 = a1
        self.r = r

        super().__init__(parent)

    def bind(self, parent):
        self.parent = parent
        self.base_p = self.p - parent.p
        self.base_a0 = self.a0
        self.base_a1 = self.a1

    def update(self):
        self.p  = self.parent.p + self.base_p.rotated(self.parent.a)
        self.a0 = self.base_a0 + self.parent.a
        self.a1 = self.base_a1 + self.parent.a

        self.update_collision_area()

    def update_collision_area(self):

        p0 = self.p + Vec2.versor(self.a0) * self.r
        p1 = self.p + Vec2.versor(self.a1) * self.r

        self.max_x.value = self.p.x + self.r if Angle(0.00 * tau).between(self.a0, self.a1) else max(p0.x, p1.x) + 0
        self.max_y.value = self.p.y + self.r if Angle(0.25 * tau).between(self.a0, self.a1) else max(p0.y, p1.y) + 0
        self.min_x.value = self.p.x - self.r if Angle(0.50 * tau).between(self.a0, self.a1) else min(p0.x, p1.x) - 0
        self.min_y.value = self.p.y - self.r if Angle(0.75 * tau).between(self.a0, self.a1) else min(p0.y, p1.y) - 0



class Vertex:
    def __init__(self, parent, value, type_):
        self.parent = parent
        self.value = value
        self.type = type_  # 0 means min, 1 means max

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return f"value: {round(self.value, 2)}, type: {self.type}, parent: {self.parent.id}"



# collision detection functions:

def detect_collisions():
    # if box_collisions:
        # print(box_collisions)
    for i in range(len(box_collisions) - 1, -1, -1):
        i_p0, i_p1 = box_collisions[i]
        if parts_collision_count[i_p0][i_p1] < 2:
            box_collisions.pop(i)
            continue

        # warning, this works only if there are only two part types
        part0, part1 = parts[i_p0], parts[i_p1]
        # print(i_p0, i_p1)

        if type(part0) == Line:
            if type(part1) == Line:
                box_collisions.pop(i)
            else:
                detect_collision_line_arc(part0, part1)
                # print(1, i_p0, i_p1)
        else:
            if type(part1) == Line:
                detect_collision_line_arc(part1, part0)
                # print(2, i_p0, i_p1)
            else:
                detect_collision_arc_arc(part0, part1)

def detect_collision_line_arc(line, arc):

    # maybe add extra condition that the arc must fit in the line, and not pass sideways

    if arc.r < 0:
        return False


    line_normalized = (line.p1 - line.p0).normalized()
    line_normalized_2 = line_normalized.rotated_270()
    d = (arc.p - line.p0).dot(line_normalized_2)
    # print(line_normalized, line_normalized_2, d)

    # print(d - arc.r > 0)
    if d - arc.r > 0:
        # print("       ", d)
        return False
    # print("here!!!", d)
    # fix and improve this
    l = line.p1 - line.p0
    if not 0 <= (arc.p - line.p0).dot(l/l.abs_2()) <= 1:
        return False
    # print(line.p0, line.p1, arc.p, arc.p - line.p0)


    # print("collideeeeee")
    a = line_normalized.angle()
    if arc.a0 == arc.a1 or (a + pi/2).between(arc.a0, arc.a1):

        collide(line.parent, arc.parent,
                line.p0 + (arc.p - line.p0).dot(line_normalized) * line_normalized,
                arc.p + arc.r * Vec2.versor(a + pi / 2),
                a+pi
                )
        return True  # maybe

def detect_collision_arc_arc(arc0, arc1):

    # can I have a cleaner function that is more general and doesn't need all these ifs?
    # what should I do with concave arcs' angles?

    if 0 == arc0.r == arc1.r:
        return False

    if arc0.r >= 0:
        if arc1.r >= 0:

            # this can be transformed into a single algorithm more flexible.

            p_r = arc1.p - arc0.p
            d = abs(p_r)
            if d > arc0.r + arc1.r:
                return False

            a = p_r.angle()
            if arc0.a0 != arc0.a1 and not a.between(arc0.a0, arc0.a1):
                return False

            if arc1.a0 != arc1.a1 and not (a+pi).between(arc1.a0, arc1.a1):
                return False

            collide(arc0.parent, arc1.parent,
                    arc0.p + Vec2.versor(a) * arc0.r,
                    arc1.p + Vec2.versor(a+pi) * arc1.r,
                    a - pi/2
                    )

        else:

            if arc0.r >= -arc1.r:
                return False

            p_r = arc1.p - arc0.p
            d = abs(p_r)

            # if d + arc0.r < -arc1.r:
            # if arc0.r + arc1.r < -d:
            if -d > arc0.r + arc1.r:
                return False

            a = p_r.angle()
            if arc0.a0 != arc0.a1 and not (a + pi).between(arc0.a0, arc0.a1):
                return False

            # here it's where it depends on what angle standard you choose: "pure" or "fixed"
            # maybe fixed is simpler?

            # fixed:
            if arc1.a0 != arc1.a1 and not (a + pi).between(arc1.a0, arc1.a1):
                return False

            collide(arc0.parent, arc1.parent,
                    arc0.p + Vec2.versor(a+pi) * arc0.r,
                    arc1.p + Vec2.versor(a+pi) * arc1.r,
                    a + pi/2
                    )

    else:
        if arc1.r >= 0:
            if arc1.r >= -arc0.r:
                return False

            p_r = arc0.p - arc1.p
            d = abs(p_r)

            if d + arc1.r < -arc0.r:
                return False

            a = p_r.angle()
            if arc1.a0 != arc1.a1 and not (a + pi).between(arc1.a0, arc1.a1):
                return False

            if arc0.a0 != arc0.a1 and not (a + pi).between(arc0.a0, arc0.a1):
                return False

            # be careful with this case!
            # unsure angle!

            collide(arc1.parent, arc0.parent,
                    arc1.p + Vec2.versor(a+pi) * arc1.r,
                    arc0.p + Vec2.versor(a+pi) * arc0.r,
                    a - pi/2  # ???
                    )

        else:
            return False




# collision reaction:

collisions_count = 0
def collide(o0: SolidObject, o1: SolidObject, p0, p1, a):  # en principio tomo vectores de colisión diferentes porque los objetos se superponen

    global collisions_count

    b = (o0.b + o1.b) / 2     # mejorar estas formulas
    fd = (o0.fr_d + o1.fr_d) / 2
    fe = (o0.fr_e + o1.fr_e) / 2

    r0 = (p0 - o0.p).rotated(-a)
    r1 = (p1 - o1.p).rotated(-a)

    p0_v = o0.v.rotated(-a) + o0.w * r0.rotated_90()  # Vec(-r0.y, r0.x)
    p1_v = o1.v.rotated(-a) + o1.w * r1.rotated_90()  # Vec(-r1.y, r1.x)

    v = p1_v - p0_v
    # print("r0", r0, r1, p0_v, p1_v, v)

    if v.y >= 0:
        # print(a, o1.v, v)
        # print("exiting collision")
        return

    collisions_count += 1


    M = 1 / o0.m + 1 / o1.m

    dy_y = M + r0.x**2 / o0.I + r1.x**2 / o1.I
    dx_x = M + r0.y**2 / o0.I + r1.y**2 / o1.I
    dy_x = -((r0.x * r0.y) / o0.I + (r1.x * r1.y) / o1.I)

    # my desired resulting trajectory, perhaps:
    dy = -v.y * (1 + b)
    dx = -v.x * (1 + b)
    # why??? shouldn't it be plain b?
    # or this is the formula of how much velocity you want to create?
    # (you would want twice to first stop and then accelerate again)

    fy = (dy * dx_x - dx * dy_x)  # / (dx_x * dy_y - dy_x * dy_x) (later they are divided by that)
    fx = (dx * dy_y - dy * dy_x)  # / (dx_x * dy_y - dy_x * dy_x)

    if fy <= 0:
        return


    ratio = fx / fy


    if abs(ratio) > fe:

        div = (dx_x * dy_y - dy_x * dy_x)
        fy /= div
        fx = copysign(fy * fd, fx)
    else:
        div = (dx_x * dy_y - dy_x * dy_x)
        fy /= div
        fx /= div

    f = Vec2(fx, fy).rotated(a)

    o1.apply_impulse(p1, f)
    o0.apply_impulse(p0, -f)

    p0_rot = p0.rotated(-a)
    p1_rot = p1.rotated(-a)




objects = []
parts = []
x_vertex_list = []
y_vertex_list = []
parts_collision_count = []
box_collisions = []


# adding objects:

for i in range(number_of_objects // 2):

    rnd_v = Vec2(200 + random() * 800, 120 + random() * 500)
    objects.append(ConvexPolygon(
        points=[
            # rnd_v + PolarVec2(i * tau / 6, (5 + random() * 60)).to_vec2()
            rnd_v + PolarVec2(i * tau / 6, (20 + random() * 40)).to_vec2()
            for i in range(6)
        ],
        b=0.8,
        fr_d=1,
        fr_e=1,
        # I=2000

    ))

    rnd_v = Vec2(200 + random() * 800, 120 + random() * 500)
    objects.append(FatLine(
        rnd_v,
        rnd_v + Vec2(random() * 100, random() * 50),
        random()**2 * 40 + 10,
        b=0.8,
        fr_d=1,
        fr_e=1,
    ))

for obj in objects:
    parts += obj.parts

for part in parts:
    x_vertex_list += [part.min_x, part.max_x]
    y_vertex_list += [part.min_y, part.max_y]

parts_collision_count = [[0 for part in parts] for part in parts]

box_collisions = []






def sort_vertex_lists():

    swap_count = 0

    for vertex_list in (x_vertex_list, y_vertex_list):

        check_list = [i for i in range(len(vertex_list)-2, -1, -1)]

        while check_list:
            i = check_list.pop()

            v0, v1 = vertex_list[i], vertex_list[i + 1]

            if v0 > v1:
                swap_count += 1

                min_id = min(v0.parent.id, v1.parent.id)
                max_id = max(v0.parent.id, v1.parent.id)

                if   v0.type == 0 and v1.type == 1:
                    parts_collision_count[min_id][max_id] -= 1

                elif v0.type == 1 and v1.type == 0:
                    parts_collision_count[min_id][max_id] += 1

                    if parts_collision_count[min_id][max_id] == 2:
                        if v0.parent.parent != v1.parent.parent:
                            box_collisions.append((min_id, max_id))

                vertex_list[i], vertex_list[i+1] = vertex_list[i+1], vertex_list[i]

                if i != 0:
                    check_list.append(i-1)

    return swap_count

print("total swaps:", sort_vertex_lists())

# for e in x_vertex_list:
#     print(e)

class App(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse_buttons_pressed = [False, False, False, False, False]
        self.cursor_pos = Vec2(0, 0)

        self.previous_energy = 1

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        self.f(1)

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor_pos = Vec2(x, y)
        self.mouse_buttons_pressed[button] = True


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cursor_pos = Vec2(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.cursor_pos = Vec2(x, y)
        self.mouse_buttons_pressed[button] = False

    def f(self, dt):

        # print(collisions_count)

        # # print energy:
        # E = 0
        # for obj in objects:
        #     if obj.m != inf and obj.I != inf:
        #         E += obj.m * obj.v.abs_2() + obj.I * obj.w ** 2
        # if E > self.previous_energy:
        #     print("more energy!!!", self.previous_energy, E)
        # else:
        #     print("total energy:", E)
        #
        # self.previous_energy = E


        if self.mouse_buttons_pressed[mouse.LEFT]:
            for o in objects:
                if o.m != inf:
                    # o.v += (self.cursor_pos - o.p)/4000
                    try:
                        o.v += (self.cursor_pos - o.p).normalized() * 0.1
                    except ZeroDivisionError:
                        pass

        if self.mouse_buttons_pressed[mouse.RIGHT]:
            for o in objects:
                if o.m != inf:
                    # o.v -= (self.cursor_pos - o.p)/4000
                    try:
                        o.v -= (self.cursor_pos - o.p).normalized() * 0.1
                    except ZeroDivisionError:
                        pass

        if self.mouse_buttons_pressed[mouse.MIDDLE]:
            for o in objects:
                if o.m != inf:
                    # o.v += (self.cursor_pos - o.p).rotated_90()/4000
                    # o.v += Vec2(0, (self.cursor_pos - o.p).y / 4000)
                    # o.v *= 1.01
                    o.w += 0.001



        for obj in objects:
            obj.move()

        sort_vertex_lists()

        detect_collisions()



    def on_draw(self):

        self.clear()
        pyglet.gl.glLineWidth(1)

        if draw_fill:
            set_color(0.5)
            drawing_points = []
            drawing_indices = []
            index_offset = 0
            for obj in objects:

                drawing_points += vector_list_to_normal_list([obj.p + point.rotated(obj.a) for point in obj.points])
                for index in obj.triangles_indices:
                    drawing_indices.append(index_offset + index)
                index_offset += len(obj.points)
            draw_indexed(GL_TRIANGLES, drawing_points, drawing_indices)

        if draw_border:
            set_color(WHITE)
            for i, obj in enumerate(objects):
                points = [obj.p + point.rotated(obj.a) for point in obj.points]
                draw(GL_LINE_LOOP, vector_list_to_normal_list(points))

            draw_stored_lines()


app = App(width=1366, height=768, resizable=True)
pyglet.clock.schedule_interval(app.f, interval=1/120)
run()


























