from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

window_width=500
window_height=500
projectiles=[]
projectile_speed=5
spaceship_speed=10
circles=[]
speed=2
spaceship_x=200
spaceship_y=30
projectile_radius=5
score=0
game_paused=False
missed_circles=0
misfires=0
game_over=False
score_x=0
score_y=490
restart_button_pos=(0, 450)
play_pause_button_pos=(250, 450)
exit_button_pos=(450, 450)
button_width=70
button_height=25

def add_circle():
    x = random.randint(50, window_width - 50)
    y = window_height + 50
    r = random.randint(15, 35)
    color = (random.random(), random.random(), random.random())
    circles.append({'x': x, 'y': y, 'radius': r, 'color': color})


def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx)>abs(dy):
        if dx>0 and dy>0:
            return 0
        if dx<0 and dy>0:
            return 3
        if dx<0 and dy<0:
            return 4
        if dx>0 and dy<0:
            return 7
    if abs(dy)>abs(dx):
        if dx>0 and dy>0:
            return 1
        if dx<0 and dy>0:
            return 2
        if dx<0 and dy<0:
            return 5
        if dx>0 and dy<0:
            return 6

def convert_to_zone0(x, y, zone):
    if zone == 1:
        x, y = y, x
    elif zone == 2:
        x, y = y, x
        x = -x
    elif zone == 3:
        x = -x
        y = y
    elif zone == 4:
        x = -x
        y = -y
    elif zone == 5:
        x, y = -y, -x
    elif zone == 6:
        x, y = y, x
        x = -x
    elif zone == 7:
        y = -y
    return x, y

def convert_from_zone0(x, y, zone):
    if zone == 1:
        x, y = y, x
    elif zone == 2:
        x, y = y, x
        x = -x
    elif zone == 3:
        x = -x
    elif zone == 4:
        x,y = -x,-y
    elif zone == 5:
        x, y = -y, -x
    elif zone == 6:
        x, y = y, -x
    elif zone == 7:
        x, y = x,-y
    return x, y

def draw_line(x1, y1, x2, y2):
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    zone = find_zone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone0(x1, y1, zone)
    x2, y2 = convert_to_zone0(x2, y2, zone)

    dx = x2 - x1
    dy = y2 - y1
    if dx == 0:
        for y in range(y1, y2 + 1):
            points_converted=[convert_from_zone0(x1, y, zone)]
            for p in points_converted:
                draw_point(p[0], p[1])
        return

    D = 2*dy-dx
    e = 2*dy
    ne = 2*(dy-dx)
    x = x1
    y = y1

    points = [(x, y)]

    while x < x2:
        if D > 0:
            y =y+1
            D =D+ne
        else:
            D =D+e
        x =x+1
        points.append((x, y))

    points_converted = [convert_from_zone0(x, y, zone) for x, y in points]
    for p in points_converted:
        draw_point(p[0], p[1])

def draw_point(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()

def draw_circle_midpoint(x_center, y_center, r):
    x = 0
    y = r
    d = 1 - r
    while x <= y:
        draw_symmetric_points(x_center, y_center, x, y)
        x =x+1
        if d < 0:
            d =d+2*x+1
        else:
            y =y-1
            d =d+2*(x-y)+1

def draw_symmetric_points(x_center, y_center, x, y):
    draw_point(x_center + x, y_center + y)
    draw_point(x_center - x, y_center + y)
    draw_point(x_center + x, y_center - y)
    draw_point(x_center - x, y_center - y)
    draw_point(x_center + y, y_center + x)
    draw_point(x_center - y, y_center + x)
    draw_point(x_center + y, y_center - x)
    draw_point(x_center - y, y_center - x)

def draw_spaceship(x, y):
    glColor3f(1.0, 1.0, 0.0)
    draw_line(x, y, x+50, y)
    draw_line(x, y+80, x+50, y+80)
    draw_line(x, y, x, y+80)
    draw_line(x+50, y, x+50, y+80)


    draw_line(x-10, y+80, x+25, y+120)
    draw_line(x+60, y+80, x+25, y+120)
    draw_line(x+60, y+80, x-10, y+80)


    glColor3f(1.0, 0.5, 0.0)
    draw_line(x, 0, x, y)
    draw_line(x + 5, 0, x + 5, y)
    draw_line(x + 15, 0, x + 15, y)
    draw_line(x + 20, 0, x + 20, y)
    draw_line(x + 30, 0, x + 30, y)
    draw_line(x + 35, 0, x + 35, y)
    draw_line(x + 45, 0, x + 45, y)
    draw_line(x + 50, 0, x + 50, y)

def draw_projectiles():
    glColor3f(1.0, 0.0, 0.0)
    for projectile in projectiles:
        draw_circle_midpoint(projectile['x'], projectile['y'], projectile_radius)

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_button(x, y, label, button_width, button_height):
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + button_width, y)
    glVertex2f(x + button_width, y + button_height)
    glVertex2f(x, y + button_height)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    draw_text(x + 5, y + 5, label)

def draw_buttons():
        global button_width, button_height
        draw_button(*restart_button_pos, "Restart", button_width, button_height)
        draw_button(*play_pause_button_pos, "Pause" if not game_paused else "Play", button_width, button_height)
        draw_button(*exit_button_pos, "Exit", button_width, button_height)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_spaceship(spaceship_x, spaceship_y)
    draw_projectiles()

    for circle in circles:
        glColor3f(*circle['color'])
        draw_circle_midpoint(circle['x'], circle['y'], circle['radius'])

    glColor3f(1.0, 1.0, 1.0)
    draw_text(10, 480, f"Score: {score}")
    draw_buttons()
    glutSwapBuffers()


def update(value):
    global circles, projectiles, score, missed_circles, misfires, game_over

    if game_paused or game_over:
        glutTimerFunc(16, update, 0)
        return

    if random.random() < 0.01:
        add_circle()

    for circle in circles[:]:
        circle['y']=circle['y']-speed
        if circle['y'] + circle['radius'] < 0:
            circles.remove(circle)
            missed_circles =missed_circles+1
            if missed_circles >= 3:
                game_over = True
                print(f"Game Over! Final Score: {score}")
                return


    for projectile in projectiles[:]:
        projectile['y'] =projectile['y']+projectile_speed
        if projectile['y'] > window_height:
            projectiles.remove(projectile)
            misfires=misfires+1
            if misfires >= 3:
                game_over = True
                print(f"Game Over! Final Score: {score}")
                return


    for projectile in projectiles[:]:
        for circle in circles[:]:
            distance = ((projectile['x']-circle['x'])**2+(projectile['y']-circle['y'])**2)**0.5
            if distance < circle['radius']:
                projectiles.remove(projectile)
                circles.remove(circle)
                score=score+10
                break

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
    global spaceship_x, spaceship_y, game_paused, game_over
    if game_over:
        return

    if key == b'a':
        spaceship_x = max(0,spaceship_x-spaceship_speed)
    elif key == b'd':
        spaceship_x = min(window_width-50,spaceship_x+spaceship_speed)
    elif key == b' ':
        projectile_x = spaceship_x + 25
        projectile_y = spaceship_y + 120
        projectiles.append({'x': projectile_x, 'y': projectile_y})

    glutPostRedisplay()

def mouse(button, state, x, y):
    global game_paused, game_over, button_width, button_height
    if game_over:
        return

    y = window_height - y

    if (button == GLUT_LEFT_BUTTON or button == GLUT_RIGHT_BUTTON) and state == GLUT_DOWN:
        if restart_button_pos[0] <= x <= restart_button_pos[0] + button_width and  restart_button_pos[1] <= y <= restart_button_pos[1] + button_height:
            print(f"Starting Over!!")
            restart_game()

        if play_pause_button_pos[0] <= x <= play_pause_button_pos[0] + button_width and play_pause_button_pos[1] <= y <= play_pause_button_pos[1] + button_height:
            game_paused = not game_paused

        if exit_button_pos[0] <= x <= exit_button_pos[0] + button_width and exit_button_pos[1] <= y <= exit_button_pos[1] + button_height:
                print(f"Good Bye!!")
                glutLeaveMainLoop()

def restart_game():
    global circles, projectiles, score, missed_circles, misfires, game_over, spaceship_x
    circles.clear()
    projectiles.clear()
    score = 0
    missed_circles = 0
    misfires = 0
    game_over = False
    spaceship_x = 200
    add_circle()

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(window_width, window_height)
glutCreateWindow(b"Shooting Game")
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutTimerFunc(25, update, 0)
glutMainLoop()
