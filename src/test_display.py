from pyglet.gl import *
'''
# Direct OpenGL commands to this window.
window = pyglet.window.Window()
joysticks = pyglet.input.get_joysticks()
if joysticks:
    joystick = joysticks[0]
joystick.open()
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


pyglet.app.run()
'''
