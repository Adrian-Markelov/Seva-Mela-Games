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

ACTIVATION_RADIUS = 50  # Radius for finger activation
GAME_DURATION = 60      # Game lasts for 20 seconds

# Fonts
FONT = pygame.font.SysFont('Pacifico', 70)
LARGE_FONT = pygame.font.SysFont('Pacifico', 200)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)
DARK_BLUE = (0, 76, 153)
LIGHT_BLUE = (102, 178, 255)
ORANGE = (255, 165, 0)


# MVC Components
class Model:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.max_circles = 40
        self.min_circles = 10
        self.circle_speed_max = 3
        self.circle_speed_sel_max = 45
        self.score = 50
        self.prob_good = .51
        self.good_foods = ['apple', 'lemon', 'carrot', 'sprouts', 'watermelon', 'banana']
        self.bad_foods = ['fries', 'hamburger', 'onion', 'pizza', 'garlic', 'chicken']
        self.circles = self.create_circles(10)  # Start with 5 to 9 circles

    def create_circles(self, num_circles):
        circles = []
        for _ in range(num_circles):
            state = 'bad'
            if rand.random() < self.prob_good:
                state = 'good'
            icon = ""
            if state == 'good':
                icon = self.good_foods[rand.randint(0, len(self.good_foods)-1)]
            else:
                icon = self.bad_foods[rand.randint(0, len(self.bad_foods)-1)]
            speed_range = np.concatenate((np.arange(-self.circle_speed_max, 0), np.arange(1, self.circle_speed_max+1))).tolist()
            circle = {
                'position': (
                    rand.randint(0, CAMERA_WIDTH),
                    rand.randint(0, CAMERA_HEIGHT)
                ),
                'speed': (
                    rand.choice(speed_range),
                    rand.choice(speed_range)
                ),
                'state': state,
                'icon': icon
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
        # With some probability, randomly drop a random circle each collision
        for i, circle in enumerate(self.circles):
            dist = math.hypot(
                circle['position'][0] - finger_pos[0],
                circle['position'][1] - finger_pos[1]
            )
            if dist < ACTIVATION_RADIUS:
                circles_to_remove.append(i)
                self.score += 3 if circle['state'] == 'good' else -20
        add_remove_range = 3
        for index in reversed(circles_to_remove):
            self.circles.pop(index)
            # Add new circles
            new_circles = self.create_circles(rand.randint(1, add_remove_range))
            self.circles.extend(new_circles)
        
        # If collision happened randomly drop circles
        if circles_to_remove:
            rand_drop_idxs = np.unique(np.random.randint(0, len(self.circles)-1, size=rand.randint(1, add_remove_range))).tolist()
            rand_drop_idxs.sort(reverse=True)
            for rand_drop_idx in rand_drop_idxs:
                self.circles.pop(rand_drop_idx)
    
    def check_circles_count(self):
        if len(self.circles) < self.min_circles:
            new_circles = self.create_circles(self.min_circles - len(self.circles))
            self.circles.extend(new_circles)
        elif len(self.circles) > self.max_circles:
            self.circles = self.circles[:self.max_circles]
    
    def check_good_count(self):
        good_count = sum(1 for circle in self.circles if circle['state'] == 'good')

        if good_count == 0:
            new_circles = self.create_circles(6)
            self.circles.extend(new_circles)

class View:
    def __init__(self, screen, model):
        self.screen = screen
        self.model = model
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()  # Get full screen size
        # Scaling factor
        self.scale_x = self.screen_width / CAMERA_WIDTH
        self.scale_y = self.screen_height / CAMERA_HEIGHT

        self.point_image = pygame.image.load('./bubble_pop/assets/hand_black.png')
        self.point_image = pygame.transform.scale(self.point_image, (2*ACTIVATION_RADIUS, 2*ACTIVATION_RADIUS))

        self.background_img = pygame.image.load('./bubble_pop/assets/grass_sky.jpg')
        self.background_img = pygame.transform.scale(self.background_img, self.screen.get_size())

        self.title_img = pygame.image.load('./bubble_pop/assets/title_orange_2.png')
        self.game_over_img = pygame.image.load('./bubble_pop/assets/game_over_orange.png')

        self.bad_food_imgs = dict()
        self.good_food_imgs = dict()
        for bad_asset_name in self.model.bad_foods:
            bad_food_img = pygame.image.load(f'./bubble_pop/assets/{bad_asset_name}.png')
            bad_food_img = pygame.transform.scale(bad_food_img, (2*ACTIVATION_RADIUS, 2*ACTIVATION_RADIUS))
            self.bad_food_imgs[bad_asset_name] = (bad_food_img, bad_food_img.get_rect())
        for good_asset_name in self.model.good_foods:
            good_food_img = pygame.image.load(f'./bubble_pop/assets/{good_asset_name}.png')
            good_food_img = pygame.transform.scale(good_food_img, (2*ACTIVATION_RADIUS, 2*ACTIVATION_RADIUS))
            self.good_food_imgs[good_asset_name] = (good_food_img, good_food_img.get_rect())

    
    def scale_point(self, point):
        return (int(point[0] * self.scale_x), int(point[1] * self.scale_y))

    def draw_frame(self, frame_surface):
        self.screen.blit(frame_surface, (0, 0))
    
    def draw_background(self):
        # self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_img, (0, 0))

    def draw_circles(self, circles):
        for circle in circles:
            if circle['state'] == 'good':
                good_food_img, good_food_rect = self.good_food_imgs[circle['icon']]
                good_food_rect.x, good_food_rect.y = self.scale_point(circle['position'])
                self.screen.blit(good_food_img, good_food_rect)
            elif circle['state'] == 'bad':
                bad_food_img, bad_food_rect = self.bad_food_imgs[circle['icon']]
                bad_food_rect.x, bad_food_rect.y = self.scale_point(circle['position'])
                self.screen.blit(bad_food_img, bad_food_rect)

    def draw_halo(self, finger_pos):
        self.screen.blit(self.point_image, self.scale_point(finger_pos))
        # pygame.draw.circle(
        #     self.screen,
        #     (255, 255, 0),  # Yellow
        #     self.scale_point(finger_pos),
        #     ACTIVATION_RADIUS,
        #     2
        # )

    def draw_text(self, score, time_left):
        score_text = FONT.render(f"Score: {score}", True, ORANGE)
        time_text = FONT.render(f"Time left: {int(time_left)}", True, ORANGE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(time_text, (10, 80))

    def draw_game_over(self, score):
        # text_surface = LARGE_FONT.render("Game Over", True, (255, 0, 0))
        # title_rect = self.game_over_img.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 200))
        game_over_rect = self.game_over_img.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 200))
        self.screen.blit(self.game_over_img, game_over_rect)

        score_surface = FONT.render(f"Your Score: {score}", True, ORANGE)
        if score > 0:
            score_surface = FONT.render(f"Congratulations You Survived!!!! Your Score: {score}", True, ORANGE)
        else:
            score_surface = FONT.render(f"Sorry You LOSE!!!! Your Score: {score}", True, ORANGE)
        score_rect = score_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(score_surface, score_rect)

        restart_surface = FONT.render("Press R to Restart or S for Splash Screen", True, ORANGE)
        restart_rect = restart_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        self.screen.blit(restart_surface, restart_rect)
    
    def draw_splash(self):
        # text_surface = LARGE_FONT.render("Panic Poppers", True, ORANGE)
        # text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 200))
        title_rect = self.title_img.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 200))
        self.screen.blit(self.title_img, title_rect)

        restart_surface = FONT.render("Press SPACE to start the game", True, ORANGE)
        restart_rect = restart_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(restart_surface, restart_rect)

class Controller:
    def __init__(self, screen):
        self.start_time = time.time()
        self.model = Model()
        self.view = View(screen, self.model)
        self.detector = htm.HandDetector(detectionCon=0.7)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.running = True
        self.game_state = "SPLASH"

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if self.game_state == "OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.game_state = "GAME"
                        self.model.reset_game()
                        self.start_time = time.time()
                    if event.key == pygame.K_s:
                        self.game_state = "SPLASH"
            if self.game_state == "SPLASH":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_state = "GAME"
                        self.model.reset_game()
                        self.start_time = time.time()
    
    def update_game_state(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= GAME_DURATION or self.model.score <= 0:
            self.game_state = "OVER"
    
    def update_circle_speed(self, game_time):
        increase_every_secs = 4
        speed_scaler = 2
        new_speed = 2 + int((game_time//increase_every_secs)*speed_scaler)
        if new_speed <= self.model.circle_speed_sel_max:
            self.model.circle_speed_max = new_speed
        # print(f"game_time: {game_time}, circle_speed_max: {self.model.circle_speed_max}")

    def update(self):
        self.view.draw_background()

        if self.game_state == "GAME":
            # Capture frame
            success, img = self.cap.read()
            if not success:
                print("Failed to grab frame")
                self.running = False
                return

            # Update game state
            self.update_game_state()

            # Hand detection
            self.detector.findHands(img, draw=False)
            lmList = self.detector.findPosition(img, draw=False)
            
             # Convert image for Pygame
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = np.rot90(img)
            camera_frame_surface = pygame.surfarray.make_surface(img)
            camera_view_shape = (250,150)
            camera_frame_surface = pygame.transform.scale(camera_frame_surface, camera_view_shape)
            self.view.screen.blit(camera_frame_surface, (self.view.screen_width - camera_view_shape[0] - 10, self.view.screen_height - camera_view_shape[1] - 10))

            # # Draw Camera Frame
            # self.view.draw_frame(camera_frame_surface)

            if lmList:
                index_finger_tip = lmList[8][1], lmList[8][2]
                # Adjust x-coordinate due to flipping
                index_finger_tip = (CAMERA_WIDTH - index_finger_tip[0], index_finger_tip[1])
                # Draw halo around finger tip
                self.view.draw_halo(index_finger_tip)
                # Check for collisions
                self.model.check_collisions(index_finger_tip)
            
            self.model.check_circles_count()
            self.model.check_good_count()

            # Update and draw circles
            self.model.update_circles()
            self.view.draw_circles(self.model.circles)

            game_time = (time.time() - self.start_time)
            time_left = GAME_DURATION - game_time
            self.update_circle_speed(game_time)
            # if game_time%5 == 0:
            #     self.model.score -= 5

            # Draw score and time            
            self.view.draw_text(self.model.score, time_left)
        elif self.game_state == "OVER":
            # Draw game over screen
            self.view.draw_game_over(self.model.score)
        elif self.game_state == "SPLASH":
            self.view.draw_splash()

        # Update display
        # pygame.display.update()
        pygame.display.flip()


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
