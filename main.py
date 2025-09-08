from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


camera_pos = (0,500,500)
fovY = 120

def keyboardListener(key, x, y):
    pass
def specialKeyListener(key, x, y):
    pass


def mouseListener(button, state, x, y):
    pass


def setupCamera():
    glMatrixMode(GL_PROJECTION) 
    glLoadIdentity() 
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos
    gluLookAt(x, y, z,
              0, 0, 0,
              0, 0, 1)


def idle():
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D OpenGL Intro")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()



def draw_coin(c):
    """Draw a spinning coin perpendicular to the road using only GL_QUADS and GL_TRIANGLES."""
    global coin_rotation_angle

    x, y, z = c["x"], c["y"], c["z"]
    radius = c["size"] / 2
    height = c["size"] / 5
    sides = 32

    glPushMatrix()
    glTranslatef(x, y, z + height + 10)
    glRotatef(90, 1, 0, 0)
    glRotatef(coin_rotation_angle, 0, 1, 0)
    glColor3f(1.0, 0.68, 0.0)

    glBegin(GL_QUADS)
    for i in range(sides):
        theta1 = (2 * math.pi * i) / sides
        theta2 = (2 * math.pi * (i + 1)) / sides
        x1, y1 = radius * math.cos(theta1), radius * math.sin(theta1)
        x2, y2 = radius * math.cos(theta2), radius * math.sin(theta2)
        glVertex3f(x1, y1, -height / 2)
        glVertex3f(x2, y2, -height / 2)
        glVertex3f(x2, y2, height / 2)
        glVertex3f(x1, y1, height / 2)
    glEnd()

    for i in range(sides):  # top face
        theta1 = (2 * math.pi * i) / sides
        theta2 = (2 * math.pi * (i + 1)) / sides
        x1, y1 = radius * math.cos(theta1), radius * math.sin(theta1)
        x2, y2 = radius * math.cos(theta2), radius * math.sin(theta2)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, height / 2)
        glVertex3f(x1, y1, height / 2)
        glVertex3f(x2, y2, height / 2)
        glEnd()

    for i in range(sides):  # bottom face
        theta1 = (2 * math.pi * i) / sides
        theta2 = (2 * math.pi * (i + 1)) / sides
        x1, y1 = radius * math.cos(theta1), radius * math.sin(theta1)
        x2, y2 = radius * math.cos(theta2), radius * math.sin(theta2)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, -height / 2)
        glVertex3f(x2, y2, -height / 2)
        glVertex3f(x1, y1, -height / 2)
        glEnd()

    glPopMatrix()

def update_game(dt):
    global forward_speed, road_scroll, score, distance_traveled
    speed_increase_rate = 5.0
    forward_speed += speed_increase_rate * dt

    current_speed = forward_speed * (2.0 if hoverboard_fast_mode else 1.0)

    for obs in obstacles:
        obs["y"] += current_speed * dt

    for c in coins:
        c["y"] += current_speed * dt

    for m in magnets:
        m["y"] += (current_speed * 2) * dt

    distance_traveled += current_speed * dt
    score = int(distance_traveled // 10)
    road_scroll += current_speed * dt

def spawn_coin():
    lane = random.randint(0, NUM_LANES - 1)
    coin = {
        "lane": lane,
        "x": LANE_X[lane],
        "y": SPAWN_Y - random.uniform(0.0, 300.0),
        "z": 20.0,
        "size": COIN_SIZE
    }
    coins.append(coin)

def spawn_magnet():
    lane = random.randint(0, NUM_LANES - 1)
    y_pos = SPAWN_Y - random.uniform(0.0, 300.0)
    can_spawn = True
    for c in coins:
        if c["lane"] == lane and abs(c["y"] - y_pos) < 150:
            can_spawn = False
            break
    if can_spawn:
        magnet = {
            "lane": lane,
            "x": LANE_X[lane],
            "y": y_pos,
            "z": 50,
            "collision_z": -15.0,
            "size": MAGNET_SIZE
        }
        magnets.append(magnet)

for c in coins:
    if magnet_active:
        dx = player["x"] - c["x"]
        dy = player["y"] - c["y"]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < MAGNET_RANGE:
            dir_x = dx / (distance + 1e-6)
            dir_y = dy / (distance + 1e-6)
            c["x"] += dir_x * current_speed * 2 * dt
            c["y"] += dir_y * current_speed * 2 * dt
    if (abs(c["y"] - player["y"]) < COLLIDE_Y_THRESHOLD and abs(c["x"] - player["x"]) < COLLIDE_X_THRESHOLD):
        to_remove_coin.append(c)
        coin_count += 1

score = int(distance_traveled // 10)

for obs in obstacles:
    if (abs(obs["y"] - player["y"]) < COLLIDE_Y_THRESHOLD and abs(obs["x"] - player["x"]) < COLLIDE_X_THRESHOLD):
        obs_bottom = 0.0
        obs_top = OBSTACLE_HEIGHT
        if (player_top_z > obs_bottom) and (player_bottom_z < obs_top):
            to_remove_obs.append(obs)
            lives -= 1
            enemy_active = True
            enemy_timer = ENEMY_DURATION
            enemy["x"] = player["x"]
            enemy["y"] = player["y"] + 190
            enemy["z"] = player["z"]
            if lives < 0:
                lives = 0
                game_over = True
        
        elif key in [b'r', b'R']:
            obstacles.clear()
            coins.clear()
            magnets.clear()
            distance_traveled = 0.0
            score = 0
            lives = 3
            forward_speed = 400.0
            road_scroll = 0.0
            game_over = False
            player["lane"] = 1
            player["x"] = LANE_X[1]
            player["y"] = 2000
            player["z"] = GROUND_Z
            player["height"] = NORMAL_HEIGHT
            is_jumping = False
            jump_velocity = 0.0
            is_sliding = False
            slide_timer = 0.0
            is_fpp_mode = False
            is_hoverboard = False
            hoverboard_fast_mode = False
            hoverboard_tilt = 0.0
            hoverboard_bob = 0.0
            coin_count = 0
            magnets_collected = 0
            magnet_active = False
            magnet_timer = 0.0
            magnet_spin_angle = 0.0
            enemy_active = False
            enemy_timer = 0.0
            enemy_is_jumping = False
            enemy_is_sliding = False
            enemy_jump_velocity = 0.0
            enemy_slide_timer = 0.0
            enemy_decision_cooldown = 0.0
            enemy["x"] = -1000
            enemy["y"] = -1000
            enemy["z"] = 40.0
            camera_pos = (0, player["y"] + 400, 500)
            last_spawn_time = time.time() - 1.0
            print("Game Restarted!")

glMatrixMode(GL_PROJECTION)
glPushMatrix()
glLoadIdentity()
gluOrtho2D(0, 1000, 0, 800)
glMatrixMode(GL_MODELVIEW)
glPushMatrix()
glLoadIdentity()

glColor3f(1, 1, 1)
draw_text_line(10, 770, "Score: ")
glColor3f(1, 1, 0)
draw_text_line(80, 770, f"{score}")

glColor3f(1, 1, 1)
draw_text_line(10, 740, "Lives: ")
glColor3f(1, 1, 0)
draw_text_line(80, 740, f"{lives}")

mode_text = "FPP" if is_fpp_mode else "TPP"
glColor3f(1, 1, 1)
draw_text_line(10, 710, "Camera: ")
glColor3f(1, 1, 0)
draw_text_line(90, 710, f"{mode_text} (Press F)")

hoverboard_text = "HOVERBOARD" if is_hoverboard else "NORMAL"
glColor3f(1, 1, 1)
draw_text_line(10, 680, "Mode: ")
glColor3f(1, 1, 0)
draw_text_line(80, 680, f"{hoverboard_text} (Press C)")

glColor3f(1, 1, 1)
draw_text_line(590, 770, "Distance: ")
glColor3f(1, 1, 0)
draw_text_line(670, 770, f"{int(distance_traveled)} Meters")

glColor3f(1, 1, 1)
draw_text_line(590, 740, "Coins: ")
glColor3f(1, 1, 0)
draw_text_line(670, 740, f"{int(coin_count)}")

glColor3f(1, 1, 1)
draw_text_line(590, 710, "Magnets: ")
glColor3f(1, 1, 0)
draw_text_line(670, 710, f"{magnets_collected}")

glColor3f(1, 1, 1)
draw_text_line(10, 650, "Press 'R' to restart")

if hoverboard_fast_mode:
    glColor3f(1, 1, 1)
    draw_text_line(10, 620, "FAST MODE: ON")

glPopMatrix()
glMatrixMode(GL_PROJECTION)
glPopMatrix()
glMatrixMode(GL_MODELVIEW)
