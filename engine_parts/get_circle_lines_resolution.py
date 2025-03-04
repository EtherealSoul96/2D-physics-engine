
# should points go beyond so



from .simple_gl import *
from pyglet.window import mouse, key
from tom_lib.vectors import Vec2
from pyglet import gl
from math import acos, ceil, tau


def get_circle_lines_resolution(radius, resolution):
    a = 2 * acos(max(0, 1 - resolution / radius))
    n = ceil(tau / a)
    print("n", n)
    return max(3, n)

def get_arc_lines_resolution(radius, angle, resolution):
    if angle == 0:
        angle = tau
        # or get_circle_lines_resolution?
        # or draw the circle in another way?

    min_a = 2 * acos(max(0, 1 - resolution / radius))
    n = ceil(angle / min_a)
    return n



class App(Window):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 100
        self.resolution = 4
        self.draw_points = True
        self.center = Vec2(0, 0)
        self.draw_HD = False


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.center += Vec2(dx, dy)

    def on_key_press(self, symbol, modifiers):


        if symbol == key.P:
            self.draw_points = not self.draw_points
        if symbol == key.H:
            self.draw_HD = not self.draw_HD

        if symbol == key.UP:
            self.radius *= 1.05
        if symbol == key.DOWN:
            self.radius /= 1.05
        if symbol == key.RIGHT:
            # self.resolution += 0.1
            self.resolution *= 2
        if symbol == key.LEFT:
            # self.resolution = max(0.1, self.resolution - 0.1)
            self.resolution /= 2

        print("radius:", self.radius, "resolution:",  self.resolution)

    def on_draw(self):

        self.clear()


        gl.glLineWidth(15)

        center = Vec2(self.width, self.height) / 2 + self.center
        n = get_circle_lines_resolution(self.radius, self.resolution)

        points  = []
        points2 = []
        points_HD = []
        # offset = 0
        offset = self.resolution/2
        for i in range(n):
            points  += [*(center + Vec2(self.radius + offset, 0).rotated(i / n * tau))]
            points2 += [*(center + Vec2(self.radius -0.5, 0).rotated((i+0.5) / n * tau))]
            for j in range(8):
                points_HD += [*(center + Vec2(self.radius, 0).rotated((i + (j / 8)) / n * tau))]

        if self.draw_HD:
            set_color(0.7)
            draw(gl.GL_TRIANGLE_FAN, points_HD)


        set_color(0.5)
        # draw(gl.GL_TRIANGLE_FAN, points)
        draw(gl.GL_LINE_LOOP, points)


        if self.draw_points:
            set_color(YELLOW)
            draw_points(points2)



if __name__ == "__main__":
    App(resizable=True)
    run()