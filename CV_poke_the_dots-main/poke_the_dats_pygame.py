import cv2
import pygame
import numpy as np
import Hand as htm  # Your custom Hand tracking module
import random as rand
import math
import time

# Initialize Pygame
pygame.init()

# Set screen dimensions
camera_width, camera_height = 640, 480
screen = pygame.display.set_mode((camera_width, camera_height))
pygame.display.set_caption("Hand Tracking Game")

# Set up the camera using OpenCV
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

# Initialize the hand detector
detector = htm.HandDetector(detectionCon=0.7)

# Set up fonts
font = pygame.font.SysFont('Arial', 30)
large_font = pygame.font.SysFont('Arial', 60)

def reset_game():
    global score, start_time, game_duration, game_over
    global circle_positions, circle_speeds, circle_colors

    # Initialize game variables
    num_circles = rand.randint(5, 9)  # Start with at least 5 circles
    circle_positions = circle_coordinates(num_circles)
    circle_speeds = [(rand.randint(-2, 2), rand.randint(-2, 2)) for _ in range(num_circles)]
    circle_colors = [random_color() for _ in range(num_circles)]

    score = 0
    start_time = time.time()
    game_duration = 20  # Game lasts for 20 seconds
    game_over = False

def circle_coordinates(number_of_circles):
    positions = []
    for _ in range(number_of_circles):
        center_x = rand.randint(0, camera_width)
        center_y = rand.randint(0, camera_height)
        positions.append((center_x, center_y))
    return positions

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def random_color():
    return (
        rand.randint(100, 255),  # Red
        rand.randint(0, 155),    # Green
        rand.randint(100, 255)   # Blue
    )

# Initialize game variables
reset_game()

# Main game loop
running = True
while running:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= game_duration:
        game_over = True

    # Capture frame-by-frame from OpenCV
    success, img = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    # # Flip the image horizontally for a mirror effect
    # img = cv2.flip(img, 1)

    # Detect hands and get landmark positions
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    # Convert the image from BGR to RGB color space
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.rot90(img)  # Rotate the image for correct orientation

    # Create a Pygame surface from the image
    frame_surface = pygame.surfarray.make_surface(img)

    # Display the frame on the Pygame window
    screen.blit(frame_surface, (0, 0))

    if not game_over:
        if lmList and len(circle_positions) > 0:
            # Get the index finger tip position
            index_finger_tip = lmList[8][1], lmList[8][2]
            # Adjust x-coordinate due to flipping
            index_finger_tip = (camera_width - index_finger_tip[0], index_finger_tip[1])

            circles_to_remove = []

            # Draw a halo circle around the index finger tip
            activation_radius = 25  # Same as the circle activation distance
            pygame.draw.circle(screen, (255, 255, 0), (int(index_finger_tip[0]), int(index_finger_tip[1])), activation_radius, 2)

            # Check if the index finger tip is touching any circle
            for i, circle_pos in enumerate(circle_positions):
                dist = distance(index_finger_tip, circle_pos)
                if dist < activation_radius:
                    circles_to_remove.append(i)
                    score += 5

            # Remove touched circles and generate new ones
            for index in reversed(circles_to_remove):
                circle_positions.pop(index)
                circle_speeds.pop(index)
                circle_colors.pop(index)

                num_new_circles = rand.randint(1, 3)
                new_circle_positions = circle_coordinates(num_new_circles)
                new_circle_speeds = [(rand.randint(-2, 2), rand.randint(-2, 2)) for _ in range(num_new_circles)]
                new_circle_colors = [random_color() for _ in range(num_new_circles)]
                circle_positions.extend(new_circle_positions)
                circle_speeds.extend(new_circle_speeds)
                circle_colors.extend(new_circle_colors)

        # Move and draw circles
        for i, circle_pos in enumerate(circle_positions):
            center_x, center_y = circle_pos
            speed_x, speed_y = circle_speeds[i]

            center_x += speed_x
            center_y += speed_y

            # Bounce off the edges
            if center_x < 0 or center_x > camera_width:
                circle_speeds[i] = (-speed_x, speed_y)
                center_x = max(0, min(center_x, camera_width))
            if center_y < 0 or center_y > camera_height:
                circle_speeds[i] = (speed_x, -speed_y)
                center_y = max(0, min(center_y, camera_height))

            circle_positions[i] = (center_x, center_y)
            color = circle_colors[i]

            # Draw the circle
            pygame.draw.circle(screen, color, (int(center_x), int(center_y)), 25)

        # Render the score and time left
        score_text = font.render(f"Score: {score}", True, (0, 255, 0))
        time_text = font.render(f"Time left: {int(game_duration - elapsed_time)}", True, (0, 255, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 50))
    else:
        # Display Game Over message and Restart instructions
        text_surface = large_font.render("Game Over", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(camera_width // 2, camera_height // 2 - 50))
        screen.blit(text_surface, text_rect)

        score_surface = font.render(f"Your Score: {score}", True, (255, 0, 0))
        score_rect = score_surface.get_rect(center=(camera_width // 2, camera_height // 2))
        screen.blit(score_surface, score_rect)

        restart_surface = font.render("Press 'R' to Restart", True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(camera_width // 2, camera_height // 2 + 50))
        screen.blit(restart_surface, restart_rect)

    # Update the Pygame display
    pygame.display.update()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

# Release resources
cap.release()
pygame.quit()
