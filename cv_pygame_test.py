import cv2
import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the camera using OpenCV
cap = cv2.VideoCapture(0)  # 0 is the default camera, change if using external camera

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Get the width and height of the camera feed
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set up the Pygame window with the size of the camera feed
screen = pygame.display.set_mode((frame_width, frame_height))

# Set a caption for the Pygame window
pygame.display.set_caption("OpenCV Camera Feed in Pygame")

# Main loop
running = True
while running:
    # Capture frame-by-frame from OpenCV
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Convert the color from BGR (OpenCV) to RGB (Pygame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the OpenCV frame (NumPy array) to Pygame surface
    frame_surface = pygame.surfarray.make_surface(np.rot90(frame))

    # Display the frame on the Pygame window
    screen.blit(frame_surface, (0, 0))

    # Update the Pygame display
    pygame.display.update()

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Release the camera and close the windows
cap.release()
pygame.quit()
