import cv2
import numpy as np
import pygame
import random

# Initialize Pygame
pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Initialize the OpenCV video capture
cap = cv2.VideoCapture(0)

# Colors
blue = (0, 0, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# Define HSV ranges for detecting red (two ranges for red in HSV)
lower_red1 = np.array([0, 100, 100])  # Adjust the values to avoid noise
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([170, 100, 100])
upper_red2 = np.array([180, 255, 255])

# Minimum area to filter small rectangles
min_area = 1500  # Adjust this value to filter out small rectangles

# Function to generate a random curvy road
def generate_road():
    points = []
    x_start = 0
    for i in range(5):
        x_start += random.randint(100, 150)
        y_pos = random.randint(100, height - 100)
        points.append((x_start, y_pos))
    return points

# Function to draw the road
def draw_road(surface, road_points):
    pygame.draw.lines(surface, black, False, road_points, 40)

# Generate a random road
road_points = generate_road()

# Randomly place the blue dot near the start of the road
blue_dot_pos = road_points[0]

# Main game loop
running = True
while running:
    # Capture frame from the camera
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize the frame to fit the game window
    frame_resized = cv2.resize(frame, (width, height))

    # Convert the frame from BGR (OpenCV) to RGB (Pygame)
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    # Convert to HSV color space for color detection
    hsv_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2HSV)

    # Create two masks for the red color (for two red ranges in HSV)
    mask1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

    # Combine the masks
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Show the red mask using OpenCV to visualize what is being detected
    cv2.imshow('Red Mask', red_mask)  # Display the mask to see if it detects red blobs

    # Use the Canny edge detector to find edges
    edges = cv2.Canny(red_mask, 50, 150)

    # Show the edges mask using OpenCV to visualize the edges detected
    cv2.imshow('Edges Mask', edges)  # Display the edges detected by Canny

    # Find contours from the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and detect rectangles
    for contour in contours:
        # Approximate the contour
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # If the contour has four vertices, it's possibly a rectangle
        if len(approx) == 4:
            # Get the bounding box of the contour
            x, y, w, h = cv2.boundingRect(approx)

            # Filter based on the area (width * height)
            area = w * h
            if area > min_area:  # Only process rectangles larger than the minimum area
                # Check the aspect ratio of the rectangle to ensure it's not too thin or too wide
                aspect_ratio = w / float(h)
                if 0.8 <= aspect_ratio <= 1.2:  # Adjust aspect ratio range for rectangle detection
                    # Draw a red rectangle around the detected object in Pygame
                    pygame.draw.rect(screen, red, (x, y, w, h), 3)

    # Transpose the frame to match Pygame's coordinate system
    frame_rgb = np.transpose(frame_rgb, (1, 0, 2))  # Swap rows and columns

    # Flip the frame vertically to correct the upside-down issue
    frame_rgb = np.flip(frame_rgb, axis=0)  # Flip along the horizontal axis (axis=0)

    # Convert to Pygame surface
    frame_surface = pygame.surfarray.make_surface(frame_rgb)

    # Draw the camera stream as the background
    screen.blit(frame_surface, (0, 0))

    # Draw the black road on top of the camera feed
    draw_road(screen, road_points)

    # Draw the blue dot
    pygame.draw.circle(screen, blue, blue_dot_pos, 10)

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(30)

    # Close the OpenCV mask window when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close Pygame
cap.release()
cv2.destroyAllWindows()
pygame.quit()
