import cv2
import pygame
import numpy as np
import Hand as htm  # Your custom Hand tracking module
import random as rand
import math
import time

# Initialize Pygame
pygame.init()

# Constants
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480

ACTIVATION_RADIUS = 25  # Radius for finger activation
GAME_DURATION = 20      # Game lasts for 20 seconds

# Fonts
FONT = pygame.font.SysFont('Arial', 30)
LARGE_FONT = pygame.font.SysFont('Arial', 60)

# MVC Components
class Model:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.circles = self.create_circles(rand.randint(5, 9))  # Start with 5 to 9 circles

    def create_circles(self, num_circles):
        circles = []
        for i in range(num_circles):
            # rand.randint(100, 255),  # Red
            # rand.randint(0, 155),    # Green
            # rand.randint(100, 255)   # Blue
            color = (255, 0, 0)
            state = 'bad'
            if i%2 == 0:
                color = (0, 255, 0)
                state = 'good'
            circle = {
                'position': (
                    rand.randint(0, CAMERA_WIDTH),
                    rand.randint(0, CAMERA_HEIGHT)
                ),
                'speed': (
                    rand.choice([-2, -1, 1, 2]),
                    rand.choice([-2, -1, 1, 2])
                ),
                'color': color,
                'state': state
            }
            circles.append(circle)
        return circles

    def update_circles(self):
        for circle in self.circles:
            x, y = circle['position']
            sx, sy = circle['speed']

            x += sx
            y += sy

            # Bounce off the edges
            if x < 0 or x > CAMERA_WIDTH:
                sx = -sx
                x = max(0, min(x, CAMERA_WIDTH))
            if y < 0 or y > CAMERA_HEIGHT:
                sy = -sy
                y = max(0, min(y, CAMERA_HEIGHT))

            circle['position'] = (x, y)
            circle['speed'] = (sx, sy)

    def check_collisions(self, finger_pos):
        circles_to_remove = []
        for i, circle in enumerate(self.circles):
            dist = math.hypot(
                circle['position'][0] - finger_pos[0],
                circle['position'][1] - finger_pos[1]
            )
            if dist < ACTIVATION_RADIUS:
                circles_to_remove.append(i)
                self.score += 5 if circle['state'] == 'good' else -5

        for index in reversed(circles_to_remove):
            self.circles.pop(index)
            # Add new circles
            new_circles = self.create_circles(rand.randint(1, 3))
            self.circles.extend(new_circles)

    def update_game_state(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= GAME_DURATION:
            self.game_over = True

class View:
    def __init__(self, screen):
        self.screen = screen

        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()  # Get full screen size
        # Scaling factor
        self.scale_x = self.screen_width / CAMERA_WIDTH
        self.scale_y = self.screen_height / CAMERA_HEIGHT
    
    def scale_point(self, point):
        return (int(point[0] * self.scale_x), int(point[1] * self.scale_y))

    def draw_frame(self, frame_surface):
        self.screen.blit(frame_surface, (0, 0))

    def draw_circles(self, circles):
        for circle in circles:
            pygame.draw.circle(
                self.screen,
                circle['color'],
                self.scale_point(circle['position']),
                25
            )

    def draw_halo(self, finger_pos):
        pygame.draw.circle(
            self.screen,
            (255, 255, 0),  # Yellow
            self.scale_point(finger_pos),
            ACTIVATION_RADIUS,
            2
        )

    def draw_text(self, score, time_left):
        score_text = FONT.render(f"Score: {score}", True, (0, 255, 0))
        time_text = FONT.render(f"Time left: {int(time_left)}", True, (0, 255, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(time_text, (10, 50))

    def draw_game_over(self, score):
        text_surface = LARGE_FONT.render("Game Over", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2 - 50))
        self.screen.blit(text_surface, text_rect)

        score_surface = FONT.render(f"Your Score: {score}", True, (255, 0, 0))
        score_rect = score_surface.get_rect(center=(CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)

        restart_surface = FONT.render("Press 'R' to Restart", True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2 + 50))
        self.screen.blit(restart_surface, restart_rect)

class Controller:
    def __init__(self, screen):
        self.model = Model()
        self.view = View(screen)
        self.detector = htm.HandDetector(detectionCon=0.7)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.running = True

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if self.model.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.model.reset_game()

    def update(self):
        # We should move this to "not game over" since we can have a simple default background
        # Capture frame
        success, img = self.cap.read()
        if not success:
            print("Failed to grab frame")
            self.running = False
            return

        if not self.model.game_over:
            # Update game state
            self.model.update_game_state()

            # Hand detection
            self.detector.findHands(img, draw=False)
            lmList = self.detector.findPosition(img, draw=False)
            
             # Convert image for Pygame
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = np.rot90(img)
            camera_frame_surface = pygame.surfarray.make_surface(img)
            camera_frame_surface = pygame.transform.scale(camera_frame_surface, (self.view.screen_width, self.view.screen_height))

            # Draw Camera Frame
            self.view.draw_frame(camera_frame_surface)

            if lmList:
                index_finger_tip = lmList[8][1], lmList[8][2]
                # Adjust x-coordinate due to flipping
                index_finger_tip = (CAMERA_WIDTH - index_finger_tip[0], index_finger_tip[1])
                # Draw halo around finger tip
                self.view.draw_halo(index_finger_tip)
                # Check for collisions
                self.model.check_collisions(index_finger_tip)
            
            # Update and draw circles
            self.model.update_circles()
            self.view.draw_circles(self.model.circles)

            # Draw score and time
            time_left = GAME_DURATION - (time.time() - self.model.start_time)
            self.view.draw_text(self.model.score, time_left)
        else:
            # Draw game over screen
            self.view.draw_game_over(self.model.score)

        # Update display
        pygame.display.update()

    def run(self):
        while self.running:
            self.process_events()
            self.update()

        # Clean up
        self.cap.release()
        pygame.quit()

# Run the game
if __name__ == "__main__":
    # Initialize Pygame screen
    # screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT))
    full_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Full-screen Pygame
    pygame.display.set_caption("Hand Tracking Game")
    controller = Controller(full_screen)
    controller.run()
