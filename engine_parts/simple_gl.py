import pyglet
from pyglet.window import Window, key, mouse
from pyglet.graphics import draw as draw_gl
from pyglet.graphics import draw_indexed as draw_indexed_gl
from pyglet.gl import Config, GL_POINTS, GL_LINES, GL_LINE_LOOP, GL_LINE_STRIP, GL_TRIANGLES, GL_QUADS, GL_TRIANGLE_STRIP, glColor3f, glColor4f, glClearColor, glHint, GL_POINT_SMOOTH_HINT, GL_NICEST

window = None

# experiment with variables
# implement efficient draw_points_pp (consider changing the name)
# implement color arrays
# implement add points, so that they can be automatically drawn later efficiently
#   without needing the user to keep track of the points

_stored_points = []
_stored_lines = []
_stored_triangles = []
_stored_quads = []

_stored_points_colors = []
# _stored_lines = []
# _stored_triangles = []
# _stored_quads = []

# colors:
WHITE   = (1, 1, 1)
RED     = (1, 0, 0)
YELLOW  = (1, 1, 0)
GREEN   = (0, 1, 0)
CYAN    = (0, 1, 1)
BLUE    = (0, 0, 1)
MAGENTA = (1, 0, 1)

prim_sec_colors = [
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 1, 1),
    (0, 0, 1),
    (1, 0, 1),
]


# def set_functions():
#     pass

class SimpleWindow(Window):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        run()


def create_window(width=800, height=600, resizable=True, fullscreen=False, double_buffer=False):

    global window
    # window = Window(width=width, height=height, resizable=resizable, config=Config(double_buffer=double_buffer), vsync=False)
    window = Window(width=width, height=height, resizable=resizable, config=Config(double_buffer=double_buffer), vsync=False)
    if fullscreen:
        window.set_fullscreen(True)

    # pyglet.gl.glEnable(pyglet.gl.GL_POINT_SMOOTH)
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    return window

def draw(drawing_type, vertices):
    draw_gl(len(vertices)//2, drawing_type, (("v2f", vertices)))
def draw_indexed(drawing_type, vertices, indices):
    draw_indexed_gl(len(vertices)//2, drawing_type, indices, (("v2f", vertices)))

def draw_colored(drawing_type, vertices, colors):
    draw_gl(len(vertices)//2, drawing_type, ("v2f", vertices), ("c3f", colors))

def set_color(*args):

    if len(args) == 1 and type(args[0]) in {list, tuple}:
        args = args[0]

    if len(args) == 1:
        glColor3f(args[0], args[0], args[0])

    elif len(args) == 2:
        glColor4f(args[0], args[0], args[0], args[1])

    elif len(args) == 3:
        glColor3f(args[0], args[1], args[2])

    elif len(args) == 4:
        glColor4f(args[0], args[1], args[2], args[3])

def draw_point(x, y):
    draw_gl(1, GL_POINTS, (("v2f", (x, y))))
def draw_points(vertices):
    draw_gl(len(vertices)//2, GL_POINTS, (("v2f", vertices)))
def store_point(x, y):
    global _stored_points
    _stored_points += [x, y]
def draw_stored_points():
    global _stored_points
    draw_points(_stored_points)
    _stored_points = []

def store_colored_point(x, y, r, g, b):
    global _stored_points, _stored_points_colors
    _stored_points += [x, y]
    _stored_points_colors += [r, g, b]
def draw_stored_colored_points():
    global _stored_points, _stored_points_colors
    draw_colored(GL_POINTS, _stored_points, _stored_points_colors)
    _stored_points = []
    _stored_points_colors = []

def draw_fixed_point(x, y):
    draw_gl(1, GL_POINTS, (("v2f", (x+0.5, y+0.5))))
def store_fixed_point(x, y):
    global _stored_points
    _stored_points += [x+0.5, y+0.5]

def draw_line(x0, y0, x1, y1):
    draw_gl(2, GL_LINES, (("v2f", (x0, y0, x1, y1))))
def draw_lines(vertices):
    draw_gl(len(vertices)//2, GL_LINES, (("v2f", vertices)))
def store_line(x0, y0, x1, y1):
    global _stored_lines
    _stored_lines += [x0, y0, x1, y1]
def draw_stored_lines():
    global _stored_lines
    draw_lines(_stored_lines)
    _stored_lines = []

def draw_line_fixed(x0, y0, x1, y1):
    draw_gl(2, GL_LINES, (("v2f", (x0+0.5, y0+0.5, x1+0.5, y1+0.5))))
def draw_lines_fixed(vertices):
    draw_gl(len(vertices)//2, GL_LINES, (("v2f", [x + 0.5 for x in vertices])))
def store_lines_fixed(x0, y0, x1, y1):
    global _stored_lines
    _stored_lines += [x0 + 0.5, y0 + 0.5, x1 + 0.5, y1 + 0.5]

def draw_line_pp(x0, y0, x1, y1):
    if x0 == x1 and y0 == y1:
        draw_gl(1, GL_POINTS, (("v2f", (x0, y0))))
        return
    x2 = x1 - x0
    y2 = y1 - y0
    mod = (x2**2 + y2**2)**0.5
    draw_gl(2, GL_LINES, (("v2f", (x0 + 0.5, y0 + 0.5, x1+x2/mod + 0.5, y1+y2/mod + 0.5))))

def draw_triangle(x0, y0, x1, y1, x2, y2):
    draw_gl(3, GL_TRIANGLES, (("v2f", (
            x0, y0,
            x1, y1,
            x2, y2
    ))))
def draw_triangles(vertices):
    draw_gl(len(vertices)//2, GL_TRIANGLES, (("v2f", vertices)))
def store_triangle(x0, y0, x1, y1, x2, y2):
    global _stored_triangles
    _stored_triangles += [x0, y0, x1, y1, x2, y2]
def draw_stored_triangles():
    global _stored_triangles
    draw_triangles(_stored_triangles)
    _stored_triangles = []

def draw_quad(x0, y0, x1, y1, x2, y2, x3, y3):
    draw_gl(4, GL_QUADS, (("v2f", (
            x0, y0,
            x1, y1,
            x2, y2,
            x3, y3,
        )                       ))       )
def draw_quads(vertices):
    draw_gl(len(vertices)//2, GL_QUADS, (("v2f", vertices)))
def store_quads(x0, y0, x1, y1, x2, y2, x3, y3):
    global _stored_quads
    _stored_quads += [x0, y0, x1, y1, x2, y2, x3, y3]
def draw_stored_quads():
    global _stored_quads
    draw_quads(_stored_quads)
    _stored_quads = []

def draw_rectangle(x, y, w, h):
    draw_gl(4, GL_QUADS, (("v2f", (
            x, y,
            x+w, y,
            x+w,y+h,
            x,y+h
    ))))
def store_rectangle(x, y, w, h):
    global _stored_quads
    _stored_quads += [x, y, x+w, y, x+w, y+h, x, y+h]

def draw_square(x, y, s):
    draw_gl(4, GL_QUADS, (("v2f", (
        x,     y,
        x + s, y,
        x + s, y + s,
        x,     y + s
    ))))
def store_square(x, y, s):
    global _stored_quads
    _stored_quads += [x, y, x + s, y, x + s, y + s, x, y + s]

def set_point_size(s):
    pyglet.gl.glPointSize(s)
def set_clear_color(*args):
    if len(args) == 1 and type(args[0]) in {list, tuple}:
        args = args[0]

    if len(args) == 1:
        glClearColor(args[0], args[0], args[0], 1)

    elif len(args) == 2:
        glClearColor(args[0], args[0], args[0], args[1])

    elif len(args) == 3:
        glClearColor(args[0], args[1], args[2], 1)

    elif len(args) == 4:
        glClearColor(args[0], args[1], args[2], args[3])


# missing circle

# missing colored drawing

# import numpy as np
#
#
# def load_image(img_name):
#     from PIL import Image
#     return np.flip(
#         np.asarray(
#             Image.open(img_name)).copy(), 0
#     )

img_format_names = ["", "L", "", "RGB", "RGBA"]
def draw_image(img, x, y, scale=1, blurry=True):

    raw_data = (pyglet.gl.GLubyte * img.size).from_buffer(img.reshape(-1))
    image_data = pyglet.image.ImageData(
        img.shape[1], img.shape[0], img_format_names[img.shape[2]], raw_data)

    if not blurry:
        pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)
        pyglet.gl.glBindTexture(pyglet.gl.GL_TEXTURE_2D, image_data.get_texture().id)
        pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)

    img_sprite = pyglet.sprite.Sprite(image_data)

    img_sprite.scale = scale
    img_sprite.x = x
    img_sprite.y = y
    img_sprite.draw()









# print(1, id(draw_point))

original_functions = {}

# replace functions for storing functions
for name in {*locals()}:
    if len(name) > 5 and name[:5] == "draw_":
        exec(f"original_functions['{name}'] = {name}")
        # exec("original_functions['draw_line'] = draw_line")

# print(set(original_functions.keys()))
# text = str(set(original_functions.keys()))
# print(str.replace(text, "'", ""))
# text = str.replace(text, "'", "")[1:-1]
# print(text)

def clear_screen():
    window.clear()


# if f is main loop and doesn't take any parameters then create a function that is the same but takes a parameter
def event(f):

    # if f.__name__ = "start":
    #     start

    window.event(f)
    # if f.__name__ == "main_loop":
    #     pyglet.clock.schedule_interval(f, 1/120.0)
    # else:
    #     window.event(f)

def loop(frequency=1/60):
    print("in loop")
    if type(frequency) == type(loop):
        print("you should type 'loop()' or 'loop(frequency)'")
        raise Exception

    def loop_f(f):
        pyglet.clock.schedule_interval(f, frequency)
    return loop_f

def on_draw():
    draw_rectangle(100, 100, 100, 100)

modifiable_function = None

def modifiable_function():
    print("hello!")
# modifiable_function = f1



# print(locals())




def restore_functions():

    text = str(set(original_functions.keys()))
    text = str.replace(text, "'", "")[1:-1]
    exec(f"global {text}")
    for fn_name, fn in original_functions:
        pass



def run():

    global modifiable_function

    pyglet.app.run()

if __name__ == "__main__":
    window.event(on_draw)
    run()