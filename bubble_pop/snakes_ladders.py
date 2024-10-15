import pygame

# Model class
class GameModel:
    def __init__(self):
        self.ladders = [pygame.Rect(100, 400, 50, 100), pygame.Rect(200, 200, 50, 100)]
        self.floors = [pygame.Rect(0, 500, 600, 20), pygame.Rect(0, 300, 600, 20), pygame.Rect(0, 100, 600, 20)]
        self.snakes = [pygame.Rect(300, 350, 50, 150)]
        self.man = pygame.Rect(250, 450, 30, 30)

    def move_ladders_snakes_floors(self, dy):
        """Move ladders, snakes, and floors by dy"""
        for ladder in self.ladders:
            ladder.y += dy
        for floor in self.floors:
            floor.y += dy
        for snake in self.snakes:
            snake.y += dy

    def reset_snake(self):
        """Reset snake's position to its original place"""
        self.snakes[0].y = 350


# View class
class GameView:
    def __init__(self, screen):
        self.screen = screen

    def draw(self, model):
        self.screen.fill((255, 255, 255))  # Clear screen with white
        pygame.draw.rect(self.screen, (0, 255, 0), model.man)       # Man - green
        for ladder in model.ladders:
            pygame.draw.rect(self.screen, (0, 0, 255), ladder)      # Ladders - blue
        for floor in model.floors:
            pygame.draw.rect(self.screen, (139, 69, 19), floor)     # Floors - brown
        for snake in model.snakes:
            pygame.draw.rect(self.screen, (255, 0, 0), snake)       # Snakes - red
        pygame.display.flip()  # Update display


# Controller class
class GameController:
    def __init__(self, model):
        self.model = model

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:
            self.model.move_ladders_snakes_floors(50)  # Move ladders and floors down
        elif keys[pygame.K_s]:
            self.model.move_ladders_snakes_floors(-50)  # Move ladders and floors up
            self.model.reset_snake()  # Reset snake position


# Main Game Loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Snakes and Ladders")

    clock = pygame.time.Clock()

    # Initialize Model, View, Controller
    model = GameModel()
    view = GameView(screen)
    controller = GameController(model)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Controller: Handle input
        controller.handle_input()

        # View: Draw the game
        view.draw(model)

        clock.tick(30)  # 30 frames per second

    pygame.quit()


if __name__ == "__main__":
    main()
