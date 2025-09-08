from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time, math

fovY = 120  # Field of view
road_scroll = 0.0

LANE_X = [-300.0, 0.0, 300.0]
NUM_LANES = len(LANE_X)
player = {
    "lane": 1,            # index into LANE_X (start center)
    "x": LANE_X[1],
    "y": 2000,             # player is at origin along y
    "z": 40.0,            # height above ground
    "width": 50.0,
    "height": 50.0
}

# Hoverboard mode
is_hoverboard = False
hoverboard_height = 80.0  # height above ground when hovering
hoverboard_tilt = 0.0     # tilt angle for animation
hoverboard_bob = 0.0      # vertical bobbing motion
HOVERBOARD_BOB_SPEED = 4.0
HOVERBOARD_TILT_SPEED = 3.0
hoverboard_fast_mode = False  # NEW: track when space is pressed on hoverboard # NEW: track when space is pressed on hoverboard# NEW: timer for fast mode duration
 # NEW: 5 seconds duration

# hovering
hoverboard_tilt = 0.0     # tilt angle for animation
hoverboard_bob = 0.0      # vertical bobbing motion
HOVERBOARD_BOB_SPEED = 4.0
HOVERBOARD_TILT_SPEED = 3.0
hoverboard_fast_mode = False  # NEW: track when space is pressed on hoverboard # NEW: track when space is pressed on hoverboard# NEW: timer for fast mode duration
 # NEW: 5 seconds duration
forward_speed = 400.0    # units per second that obstacles move toward player (i.e., world speed)


# Player jump
is_jumping = False
jump_velocity = 0.0
GRAVITY = -1000.0   # units per second^2
JUMP_SPEED = 500.0  # initial jump velocity
GROUND_Z = 40.0     # player's base z position

# Player slide
is_sliding = False
slide_duration = 0.5   # seconds for full slide
slide_timer = 0.0
SLIDE_HEIGHT = 25.0    # height of player when sliding
NORMAL_HEIGHT = 50.0
SLIDE_Z = -25.0      # z position when fully sliding on road
   # normal standing player height

# Movement / difficulty
forward_speed = 400.0    # units per second that obstacles move toward player (i.e., world speed)
distance_traveled = 0.0
score = 0



def draw_hoverboard():
    """Draw a futuristic hoverboard with glowing effects, tilting animation, and rotating wheels."""
    global hoverboard_tilt, hoverboard_bob, forward_speed, hoverboard_fast_mode
    
    glPushMatrix()
    
    # Hoverboard dimensions
    board_length = 120
    board_width = 40
    board_thickness = 8
    
    # Apply tilting animation
    tilt_angle = math.sin(hoverboard_tilt * math.pi / 180) * 5  # 5 degrees max tilt
    glRotatef(tilt_angle, 0, 0, 1)  # tilt around Z axis (vertical) for horizontal board
    
    # Main board body - oriented parallel to the road
    glColor3f(0.2, 0.2, 0.2)  # dark gray base
    glPushMatrix()
    glScalef(board_length, board_width, board_thickness)  # back to original orientation
    glutSolidCube(1)
    glPopMatrix()
    
    # Glowing edges - also oriented parallel to road
    if hoverboard_fast_mode:
        # Intense glow in fast mode
        glColor3f(1.0, 0.2, 0.0)  # bright red glow for speed
        glPushMatrix()
        glScalef(board_length + 8, board_width + 8, board_thickness + 4)  # larger glow
        glutWireCube(1)
        glPopMatrix()
    else:
        # Normal cyan glow
        glColor3f(0.0, 0.8, 1.0)  # cyan glow
        glPushMatrix()
        glScalef(board_length + 4, board_width + 4, board_thickness + 2)  # back to original orientation
        glutWireCube(1)
        glPopMatrix()
    
    # Rotating wheels (4 wheels total) - positioned for horizontal board
    wheel_radius = 8
    wheel_width = 5
    wheel_positions = [
        (-board_width/2 - 15, -board_length/2 + 20),  # left front
        (-board_width/2 - 15, board_length/2 - 20),   # left rear
        (board_width/2 + 15, -board_length/2 + 20),   # right front
        (board_width/2 + 15, board_length/2 - 20)     # right rear
    ]
    
    # Calculate wheel rotation based on time and movement
    # Rotate wheels in opposite direction of road scrolling for forward motion illusion
    #wheel_rotation = -(hoverboard_bob * 50 + forward_speed * 0.1) % 360
    
    for i, (wheel_x, wheel_y) in enumerate(wheel_positions):
        glPushMatrix()
        glTranslatef(wheel_x, wheel_y, -board_thickness/2 - wheel_radius)
        
        # Wheels are stationary (no rotation)
        
        # Wheel body - oriented parallel to road
        glColor3f(0.1, 0.1, 0.1)  # dark wheel
        glRotatef(90, 0, 1, 0)  # rotate cylinder to be parallel to road
        gluCylinder(gluNewQuadric(), wheel_radius, wheel_radius, wheel_width, 12, 2)
        
        # Wheel rim (glowing edge) - parallel orientation
        glColor3f(0.0, 0.8, 1.0)  # cyan rim
        glPushMatrix()
        glTranslatef(-1, 0, 0)
        gluCylinder(gluNewQuadric(), wheel_radius + 1, wheel_radius + 1, 2, 12, 2)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(wheel_width, 0, 0)
        gluCylinder(gluNewQuadric(), wheel_radius + 1, wheel_radius + 1, 2, 12, 2)
        glPopMatrix()
        
        # Wheel spokes (for visual detail) - parallel orientation
        glColor3f(0.3, 0.3, 0.3)
        for spoke in range(6):
            glPushMatrix()
            glRotatef(spoke * 60, 1, 0, 0)  # rotate around X axis for parallel wheel
            glTranslatef(wheel_width/2, 0, 0)
            glRotatef(90, 1, 0, 0)  # orient spoke correctly
            gluCylinder(gluNewQuadric(), 1, 1, wheel_radius - 3, 4, 2)
            glPopMatrix()
        
        # Wheel center hub - parallel orientation
        glColor3f(0.4, 0.4, 0.4)
        glTranslatef(wheel_width/2, 0, 0)
        glutSolidSphere(4, 8, 8)
        
        glPopMatrix()
    
    # Thrusters (rear) - positioned for horizontal board
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0, side * (board_length/2 - 15), -board_thickness/2 - 10)
        
        # Thruster body
        glColor3f(0.3, 0.3, 0.3)
        gluCylinder(gluNewQuadric(), 8, 6, 20, 8, 2)
        
        # Thruster glow
        if hoverboard_fast_mode:
            # Intense thruster glow in fast mode
            glColor3f(1.0, 0.5, 0.0)  # orange/red glow
            glTranslatef(0, 0, 20)
            glutSolidSphere(10, 8, 8)  # larger glow
        else:
            # Normal thruster glow
            glColor3f(0.0, 0.6, 1.0)
            glTranslatef(0, 0, 20)
            glutSolidSphere(6, 8, 8)
        glPopMatrix()
    
    # Front lights - positioned for horizontal board
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0, side * (board_length/2 - 10), board_thickness/2 + 5)
        glColor3f(1.0, 1.0, 0.0)  # yellow lights
        glutSolidSphere(3, 6, 6)
        glPopMatrix()
    
    glPopMatrix()


def draw_player():
    """Draw a stylized human player with running, jumping, sliding, and hoverboard animations."""
    global jump_velocity, is_jumping, is_sliding, is_hoverboard

    # Basic body dimensions
    head_radius = 15
    neck_height = 10
    torso_height = 60
    torso_width = 30
    torso_depth = 15
    arm_length = 60
    leg_length = 80

    # --- Animation timing ---
    t = time.time()
    
    # Running animation
    base_swing_angle = math.sin(t * 6) * 60  # arm swing
    base_leg_angle = math.sin(t * 6 + math.pi) * 40  # leg movement
    
    # Apply animation based on state
    if is_sliding and is_hoverboard:
        # Sliding on hoverboard - surfing pose with arms out for balance
        swing_angle = math.sin(t * 6) * 15  # arms out for balance
        leg_angle = math.sin(t * 6 + math.pi) * 10  # subtle leg movement
    elif is_sliding:
        swing_angle = 0
        leg_angle = 0
    
    elif is_hoverboard:
        if hoverboard_fast_mode:
            # Hoverboard fast mode: much faster animation for speed effect
            swing_angle = math.sin(t * 12) * 60  # much faster arm movement
            leg_angle = math.sin(t * 12 + math.pi) * 40  # much faster leg movement
        else:
            # Normal hoverboard mode: more relaxed, surfing-like pose
            swing_angle = math.sin(t * 4) * 20  # gentler arm movement
            leg_angle = math.sin(t * 4 + math.pi) * 15  # subtle leg movement
    else:
        swing_angle = base_swing_angle
        leg_angle = base_leg_angle

    # Jump animation enhancement
    if is_jumping:
        swing_angle = 60 * math.sin(t * 10)  # faster arm movement when jumping
        leg_angle = 45 * math.sin(t * 10)    # faster leg movement when jumping

    # Calculate jump height (using the original working method)
    jump_z = 0
    if is_jumping:
        # The jump height is already calculated in update_game() 
        # and applied to player["z"], so we don't need extra calculation here
        jump_z = 0

    # Determine final player position
    if is_sliding and is_hoverboard:
        # Sliding on hoverboard - stay at hoverboard height
        player_z_pos = player["z"] + jump_z+30 # hoverboard height is already set in update_game
    elif is_sliding:
        player_z_pos = 5.0  # slide just above the road surface (road is at z=1)
    elif is_hoverboard:
        # Standing on hoverboard - elevate player above hoverboard
        player_z_pos = player["z"] + jump_z  # hoverboard is at z=30, so add 40 to stand on top
    else:
        player_z_pos = player["z"] + jump_z

    glPushMatrix()
    glTranslatef(player["x"], player["y"], player_z_pos)
    
    # Draw hoverboard first if in hoverboard mode
    if is_hoverboard:
        glPushMatrix()
        glTranslatef(0, 0, 0)  # position hoverboard below player so player stands on top
        draw_hoverboard()
        glPopMatrix()

    if is_sliding and is_hoverboard:
        # ---------------------------
        # SLIDING ON HOVERBOARD POSE - same as default sliding but on hoverboard
        # ---------------------------
        
        # Legs - stretched forward along the road (same as default sliding)
        for i, lx in enumerate([-10, 10]):
            glPushMatrix()
            glTranslatef(lx, 0, 32)  # slightly above hoverboard surface
            
            # Rotate to point forward (positive Y direction)
            glRotatef(90, 1, 0, 0)  # legs point forward
            
            glColor3f(0.96, 0.96, 0.86)  # beige pants
            gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
            
            # Shoes at the end of legs
            glTranslatef(0, 0, leg_length+32)
            glColor3f(0.0, 0.0, 0.0)  # black shoes
            glutSolidSphere(12, 10, 10)
            glPopMatrix()

        # Torso - lying flat on the hoverboard (same as default sliding)
        glPushMatrix()
        glTranslatef(0, 0, 30)  # slightly above hoverboard surface
        glRotatef(90, 1, 0, 0)  # lie down facing forward
        
        glColor3f(0.5, 0.25, 0.25)  # maroon shirt
        glBegin(GL_QUADS)
        # Create a flat torso
        reduced_height = 20  # flatter when sliding
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, reduced_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, reduced_height)
        glEnd()
        glPopMatrix()

        # Arms - stretched forward along the road (same as default sliding)
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, 10)
            
            # Point arms forward (positive Y direction)
            glRotatef(90, 1, 0, 0)  # arms point forward
            
            glColor3f(0.9, 0.75, 0.65)  # skin color
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            
            # Hands at the end of arms
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()

        # Head - positioned at the front, facing forward (same as default sliding)
        glPushMatrix()
        glTranslatef(0, torso_height/2 + 10, 15+50)  # position head at front of torso
        glColor3f(0.9, 0.75, 0.65)  # skin color
        glutSolidSphere(head_radius, 12, 12)
        
        # Cowboy hat (lying flat)
        glColor3f(0.55, 0.27, 0.07)
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        glTranslatef(0, 0, 8)
        gluCylinder(gluNewQuadric(), 15, 12, 12, 12, 2)
        glPopMatrix()
        
    elif is_sliding:
        # ---------------------------
        # SLIDING POSE - lying flat, facing forward
        # ---------------------------
        
        # Legs - stretched forward along the road
        for i, lx in enumerate([-10, 10]):
            glPushMatrix()
            glTranslatef(lx, 0, 5)  # slightly above ground
            
            # Rotate to point forward (positive Y direction)
            glRotatef(90, 1, 0, 0)  # legs point forward
            
            glColor3f(0.96, 0.96, 0.86)  # beige pants
            gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
            
            # Shoes at the end of legs
            glTranslatef(0, 0, leg_length)
            glColor3f(0.0, 0.0, 0.0)  # black shoes
            glutSolidSphere(12, 10, 10)
            glPopMatrix()

        # Torso - lying flat on the road
        glPushMatrix()
        glTranslatef(0, 0, 10)  # slightly above ground
        glRotatef(90, 1, 0, 0)  # lie down facing forward
        
        glColor3f(0.5, 0.25, 0.25)  # maroon shirt
        glBegin(GL_QUADS)
        # Create a flat torso
        reduced_height = 20  # flatter when sliding
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, reduced_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, reduced_height)
        glEnd()
        glPopMatrix()

        # Arms - stretched forward along the road
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, 8)
            
            # Point arms forward (positive Y direction)
            glRotatef(90, 1, 0, 0)  # arms point forward
            
            glColor3f(0.9, 0.75, 0.65)  # skin color
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            
            # Hands at the end of arms
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()

        # Head - positioned at the front, facing forward
        glPushMatrix()
        glTranslatef(0, torso_height/2 + 10, 15)  # position head at front of torso
        glColor3f(0.9, 0.75, 0.65)  # skin color
        glutSolidSphere(head_radius, 12, 12)
        
        # Cowboy hat (lying flat)
        glColor3f(0.55, 0.27, 0.07)
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        glTranslatef(0, 0, 8)
        gluCylinder(gluNewQuadric(), 15, 12, 12, 12, 2)
        glPopMatrix()

    else:
        # ---------------------------
        # STANDING/RUNNING/JUMPING POSE
        # ---------------------------
        
        # Legs
        # Left leg
        glPushMatrix()
        glTranslatef(-10, 0, leg_length)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_angle, 1, 0, 0)
        glColor3f(0.96, 0.96, 0.67)  # beige pants
        gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.0, 0.0)  # black shoes
        glutSolidSphere(12, 10, 10)
        glPopMatrix()

        # Right leg
        glPushMatrix()
        glTranslatef(10, 0, leg_length)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_angle, 1, 0, 0)
        glColor3f(0.96, 0.96, 0.67)   # beige pants
        gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.0, 0.0)  # black shoes
        glutSolidSphere(12, 10, 10)
        glPopMatrix()

        # Torso
        glPushMatrix()
        glTranslatef(0, 0, leg_length)
        glColor3f(0.5, 0, 0)  # maroon shirt
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, torso_height)
        # Back face
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, torso_height)
        # Left face
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, torso_height)
        # Right face
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, torso_height)
        glEnd()
        glPopMatrix()

        # Arms
        for side, ang in [(-1, swing_angle), (1, -swing_angle)]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, leg_length + torso_height - 10)
            glRotatef(90, 1, 0, 0)
            glRotatef(ang, 1, 0, 0)
            glColor3f(0.9, 0.75, 0.65)  # skin color
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)  # hands
            glPopMatrix()

        # Neck
        glPushMatrix()
        glTranslatef(0, 0, leg_length + torso_height)
        glColor3f(0.9, 0.75, 0.65)  # skin color
        gluCylinder(gluNewQuadric(), 5, 5, neck_height, 8, 2)
        glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(0, 0, leg_length + torso_height + neck_height + head_radius)
        glColor3f(0.9, 0.75, 0.65)  # skin color
        glutSolidSphere(head_radius, 12, 12)
        
        # Cowboy hat
        glColor3f(0.55, 0.27, 0.07)  # brown hat
        # Hat brim
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        # Hat crown
        glTranslatef(0, 0, 10)
        gluCylinder(gluNewQuadric(), 15, 12, 15, 12, 2)
        glPopMatrix()

    glPopMatrix()  # end player transform

def keyboardListener(key, x, y):
    global player, NUM_LANES, LANE_X, hoverboard_fast_mode, JUMP_SPEED, hoverboard_fast_mode, slide_duration, SLIDE_HEIGHT, SLIDE_Z

    if key in [b'a', b'A']:
        if player["lane"] < NUM_LANES - 1:
            player["lane"] += 1
            player["x"] = LANE_X[player["lane"]]

    elif key in [b'd', b'D']:
        if player["lane"] > 0:
            player["lane"] -= 1
            player["x"] = LANE_X[player["lane"]]

            if is_hoverboard:
            # On hoverboard: toggle fast animation mode instead of jumping
                hoverboard_fast_mode = not hoverboard_fast_mode
                # Reset timer when turning fast mode ON
              
            print(f"Hoverboard Fast Mode: {'ON' if hoverboard_fast_mode else 'OFF'}")
        elif not is_jumping:
            is_jumping = True
            jump_velocity = JUMP_SPEED
    
    
    elif key in [b's', b'S']:
        if is_hoverboard:
            # On hoverboard: can slide regardless of jumping state
            if not is_sliding:
                is_sliding = True
                slide_timer = slide_duration
                player["height"] = SLIDE_HEIGHT
                player["z"] = SLIDE_Z
        elif not is_sliding and not is_jumping:
            is_sliding = True
            slide_timer = slide_duration
            player["height"] = SLIDE_HEIGHT
            player["z"] = SLIDE_Z

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
    update_game()
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
    global forward_speed, road_scroll, score, distance_traveled, HOVERBOARD_BOB_SPEED, HOVERBOARD_TILT_SPEED, GROUND_Z, hoverboard_height

    speed_increase_rate = 5.0  # Adjust this value to control the rate of speed increase
    forward_speed += speed_increase_rate * dt
    

    # Player Z range calculation
    if is_sliding:
        player_bottom_z = SLIDE_Z
        player_top_z = SLIDE_Z + SLIDE_HEIGHT
    elif is_hoverboard:
        # Hoverboard mode: player floats above ground with bobbing motion
        # Make animation faster when in fast mode
        if hoverboard_fast_mode:
            bob_speed = HOVERBOARD_BOB_SPEED * 2.5  # 2.5x faster bobbing
            tilt_speed = HOVERBOARD_TILT_SPEED * 2.5  # 2.5x faster tilting
        else:
            bob_speed = HOVERBOARD_BOB_SPEED
            tilt_speed = HOVERBOARD_TILT_SPEED
            
        hoverboard_bob += bob_speed * dt
        hoverboard_tilt += tilt_speed * dt
        if hoverboard_tilt >= 360:
            hoverboard_tilt -= 360
        
        # Calculate bobbing height (sine wave for smooth floating)
        bob_offset = math.sin(hoverboard_bob) * 8.0  # 8 units of bobbing
        player["z"] = GROUND_Z + hoverboard_height + bob_offset
        
        # For collision detection, extend range to ground level when standing on hoverboard
        if is_sliding:
            player_bottom_z = player["z"]
            player_top_z = player["z"] + player["height"]
        else:
            # Standing on hoverboard - can collect items at ground level
            player_bottom_z = 0  # ground level
            player_top_z = player["z"] + player["height"]  # top of player
    else:
        player_bottom_z = player["z"]
        player_top_z = player["z"] + player["height"]

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
