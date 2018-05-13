"""
from pyglet.gl import *
from cocos.director import director

def exec():
    return 0

def test_a():
    assert exec()==0

# Direct OpenGL commands to this window.
director.init()
window = director.window
joysticks = pyglet.input.get_joysticks()
if joysticks:
    joystick = joysticks[0]

print(joystick)
@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(window.width, 0)
    glVertex2f(window.width, window.height)
    glEnd()

@joystick.event
def on_joybutton_press(joystick, button):
    print(joystick, button)



director.run()

"""
