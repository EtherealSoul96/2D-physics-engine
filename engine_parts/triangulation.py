from .simple_gl import *
from tom_lib.vectors import Vec2
from pyglet.window import key, mouse
from random import random, randint, seed


seed(9)


def inside_triangle(p, t0, t1, t2):
    # print("inside triangle?")
    # if not fixed_triangulation:  # # #
    #     return True

    if ((p[0] - t0[0]) * (t1[1] - t0[1]) +
        (p[1] - t0[1]) * (t0[0] - t1[0]) > 0 or

        (p[0] - t1[0]) * (t2[1] - t1[1]) +
        (p[1] - t1[1]) * (t1[0] - t2[0]) > 0 or

        (p[0] - t2[0]) * (t0[1] - t2[1]) +
        (p[1] - t2[1]) * (t2[0] - t0[0]) > 0):
            return False

    return True

def triangulate_with_prints(points, fixed_triangulation):

    print()
    print()

    if len(points) < 3:
        return []

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]

    n = len(points)

    x_ids_fake = sorted(range(n), key=lambda x_id: x_values[x_id])
    y_ids_fake = sorted(range(n), key=lambda y_id: y_values[y_id])

    x_ids = [0] * n
    y_ids = [0] * n

    for i in range(n):
        x_ids[x_ids_fake[i]] = i
        y_ids[y_ids_fake[i]] = i


    triangulation_indices = []


    print("x_values            ", x_values)
    print("x_values[x_ids_fake]", [x_values[id_] for id_ in x_ids_fake])
    print("x_ids_fake          ", x_ids_fake)
    print("x_ids               ", x_ids)


    index_loop = list(range(n))
    removed = [False for i in range(n)]

    i0 = 0
    consecutive_fails = 0
    unclean_count = 0

    while len(index_loop) > 3:

        # print()
        # print("index loop", index_loop)

        if consecutive_fails == len(index_loop):
            print("FAILED TRIANGULATION!")
            print("unclean_count", unclean_count)
            return triangulation_indices

        i1 = (i0 + 1) % len(index_loop)
        i2 = (i0 + 2) % len(index_loop)

        ii0 = index_loop[i0]
        ii1 = index_loop[i1]
        ii2 = index_loop[i2]

        # print("ids:", ii0, ii1, ii2)

        v0 = points[ii0]
        v1 = points[ii1]
        v2 = points[ii2]
        vd1 = [v1[0] - v0[0], v1[1] - v0[1]]
        vd2 = [v2[0] - v0[0], v2[1] - v0[1]]
        vd2_n = [vd2[1], -vd2[0]]
        if vd2_n[0] * vd1[0] + vd2_n[1] * vd1[1] < 0:
            i0 = (i0 + 1) % len(index_loop)
            # print("bad angle")
            consecutive_fails += 1
            continue


        min_x = min(x_ids[ii0], x_ids[ii1], x_ids[ii2])
        max_x = max(x_ids[ii0], x_ids[ii1], x_ids[ii2])
        min_y = min(y_ids[ii0], y_ids[ii1], y_ids[ii2])
        max_y = max(y_ids[ii0], y_ids[ii1], y_ids[ii2])

        # print("mins and maxs", min_x, max_x, min_y, max_y)

        matches = [0 for i in range(n)]

        clean_triangle = True


        for j in range(min_x + 1, max_x):
            matches[x_ids_fake[j]] += 1
        # print("x matches", matches)

        for j in range(min_y + 1, max_y):
            ii = y_ids_fake[j]
            matches[ii] += 1
            if matches[ii] == 2 and ii not in (ii0, ii1, ii2) and not removed[ii] and \
              inside_triangle(points[ii], points[ii0], points[ii1], points[ii2]):
                clean_triangle = False
                # print("not clean", ii, ii0, ii1, ii2)
                consecutive_fails += 1
                unclean_count += 1
                break

        # print("matches", matches)

        if clean_triangle:
            # print("clean", i1)
            triangulation_indices += [ii0, ii1, ii2]
            index_loop.pop(i1)
            removed[ii1] = True
            consecutive_fails = 0


        i0 = (i0 + 1) % len(index_loop)



    triangulation_indices += index_loop

    print(triangulation_indices)
    print("unclean_count", unclean_count)
    return triangulation_indices



# make version more clear using Vector arithmetic

def triangulate(points):

    def inside_triangle(p, t0, t1, t2):

        if ((p[0] - t0[0]) * (t1[1] - t0[1]) +
            (p[1] - t0[1]) * (t0[0] - t1[0]) > 0 or

            (p[0] - t1[0]) * (t2[1] - t1[1]) +
            (p[1] - t1[1]) * (t1[0] - t2[0]) > 0 or

            (p[0] - t2[0]) * (t0[1] - t2[1]) +
            (p[1] - t2[1]) * (t2[0] - t0[0]) > 0):

                return False

        return True


    if len(points) < 3:
        return []

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]

    n = len(points)

    x_ids_fake = sorted(range(n), key=lambda x_id: x_values[x_id])
    y_ids_fake = sorted(range(n), key=lambda y_id: y_values[y_id])

    x_ids = [0] * n
    y_ids = [0] * n

    for i in range(n):
        x_ids[x_ids_fake[i]] = i
        y_ids[y_ids_fake[i]] = i

    triangulation_indices = []

    index_loop = list(range(n))
    removed = [False for i in range(n)]

    i0 = 0
    consecutive_fails = 0
    unclean_count = 0

    while len(index_loop) > 3:

        if consecutive_fails == len(index_loop):
            print("FAILED TRIANGULATION!")
            print("unclean_count", unclean_count)
            return triangulation_indices

        i1 = (i0 + 1) % len(index_loop)
        i2 = (i0 + 2) % len(index_loop)

        ii0 = index_loop[i0]
        ii1 = index_loop[i1]
        ii2 = index_loop[i2]

        v0 = points[ii0]
        v1 = points[ii1]
        v2 = points[ii2]
        vd1 = [v1[0] - v0[0], v1[1] - v0[1]]
        vd2 = [v2[0] - v0[0], v2[1] - v0[1]]
        vd2_n = [vd2[1], -vd2[0]]
        if vd2_n[0] * vd1[0] + vd2_n[1] * vd1[1] < 0:
            i0 = (i0 + 1) % len(index_loop)
            consecutive_fails += 1
            continue

        min_x = min(x_ids[ii0], x_ids[ii1], x_ids[ii2])
        max_x = max(x_ids[ii0], x_ids[ii1], x_ids[ii2])
        min_y = min(y_ids[ii0], y_ids[ii1], y_ids[ii2])
        max_y = max(y_ids[ii0], y_ids[ii1], y_ids[ii2])

        matches = [0 for i in range(n)]
        clean_triangle = True

        for j in range(min_x + 1, max_x):
            matches[x_ids_fake[j]] += 1

        for j in range(min_y + 1, max_y):
            ii = y_ids_fake[j]
            matches[ii] += 1
            if matches[ii] == 2 and ii not in (ii0, ii1, ii2) and not removed[ii] and \
              inside_triangle(points[ii], points[ii0], points[ii1], points[ii2]):
                clean_triangle = False
                consecutive_fails += 1
                break

        if clean_triangle:
            triangulation_indices += [ii0, ii1, ii2]
            index_loop.pop(i1)
            removed[ii1] = True
            consecutive_fails = 0


        i0 = (i0 + 1) % len(index_loop)


    triangulation_indices += index_loop

    return triangulation_indices







class App(Window):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.points = []
        self.indices = []
        self.fixed_triangulation = False


    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.points.append((x, y))
            # self.indices = triangulate(self.points, self.fixed_triangulation)
            self.indices = triangulate(self.points)
            print("n points:", len(self.points))

        if button == mouse.RIGHT:
            self.points.pop()
            self.indices = triangulate(self.points)


    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)

        # if symbol == key.T:
        #     self.indices = triangulate(self.points, self.fixed_triangulation)

        if symbol == key.R:
            self.points.pop()
            # self.indices = triangulate(self.points, self.fixed_triangulation)
            self.indices = triangulate(self.points)

        if symbol == key.F:
            self.fixed_triangulation = not self.fixed_triangulation
            # self.indices = triangulate(self.points, self.fixed_triangulation)
            self.indices = triangulate(self.points)

        if symbol == key.DELETE:
            self.points = []
            self.indices = []

    def on_draw(self):
        self.clear()

        set_color(0.4)
        if self.indices:
            points = []
            for point in self.points:
                points += [*point]

            draw_indexed(GL_TRIANGLES, points, self.indices)


        set_color(0.5)
        points = []
        for i in range(0, len(self.indices), 3):
            points.append(self.points[self.indices[i + 0]][0])
            points.append(self.points[self.indices[i + 0]][1])
            points.append(self.points[self.indices[i + 1]][0])
            points.append(self.points[self.indices[i + 1]][1])
            points.append(self.points[self.indices[i + 1]][0])
            points.append(self.points[self.indices[i + 1]][1])
            points.append(self.points[self.indices[i + 2]][0])
            points.append(self.points[self.indices[i + 2]][1])
            points.append(self.points[self.indices[i + 2]][0])
            points.append(self.points[self.indices[i + 2]][1])
            points.append(self.points[self.indices[i + 0]][0])
            points.append(self.points[self.indices[i + 0]][1])

        draw_lines(points)

        set_color(1)
        points = []
        for point in self.points:
            points += [*point]
        draw(GL_LINE_LOOP, points)


if __name__ == "__main__":
    App(resizable=True)
    run()
