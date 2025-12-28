import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Modern color palette
COLORS = {
    'background': (18, 18, 18),      # Dark background
    'grid': (35, 35, 35),            # Subtle grid lines
    'snake_head': (76, 175, 80),     # Green head
    'snake_body': (56, 142, 60),     # Darker green body
    'food': (244, 67, 54),           # Red food
    'text': (255, 255, 255),         # White text
    'accent': (103, 58, 183),        # Purple accent
    'game_over': (255, 82, 82),      # Light red for game over
    'shadow': (0, 0, 0, 100)         # Semi-transparent shadow
}

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
        
    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
            
        # Check self collision
        if new_head in self.positions:
            return False
            
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True
    
    def change_direction(self, direction):
        # Prevent moving in opposite direction
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def eat_food(self):
        self.grow = True

class Food:
    def __init__(self, snake_positions):
        self.position = self.generate_position(snake_positions)
        self.pulse = 0
        
    def generate_position(self, snake_positions):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), 
                   random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_positions:
                return pos
    
    def update(self):
        self.pulse += 0.2

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Modern Snake Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.reset_game()
        
    def reset_game(self):
        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.score = 0
        self.game_over = False
        self.paused = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction((1, 0))
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        if not self.snake.move():
            self.game_over = True
            return
        
        # Check food collision
        if self.snake.positions[0] == self.food.position:
            self.snake.eat_food()
            self.score += 10
            self.food = Food(self.snake.positions)
        
        self.food.update()
    
    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, COLORS['grid'], (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, COLORS['grid'], (0, y), (WINDOW_WIDTH, y))
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_snake(self):
        for i, pos in enumerate(self.snake.positions):
            x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
            rect = pygame.Rect(x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
            
            if i == 0:  # Head
                # Draw shadow
                shadow_rect = pygame.Rect(x + 4, y + 4, GRID_SIZE - 4, GRID_SIZE - 4)
                shadow_surface = pygame.Surface((GRID_SIZE - 4, GRID_SIZE - 4), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surface, COLORS['shadow'], shadow_surface.get_rect(), border_radius=8)
                self.screen.blit(shadow_surface, shadow_rect)
                
                # Draw head with gradient effect
                self.draw_rounded_rect(self.screen, COLORS['snake_head'], rect, 8)
                
                # Draw eyes
                eye_size = 3
                eye_offset = 6
                if self.snake.direction == (1, 0):  # Right
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + GRID_SIZE - eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset), eye_size)
                elif self.snake.direction == (-1, 0):  # Left
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + eye_offset, y + GRID_SIZE - eye_offset), eye_size)
                elif self.snake.direction == (0, -1):  # Up
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + GRID_SIZE - eye_offset, y + eye_offset), eye_size)
                else:  # Down
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + eye_offset, y + GRID_SIZE - eye_offset), eye_size)
                    pygame.draw.circle(self.screen, COLORS['background'], 
                                     (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset), eye_size)
            else:  # Body
                # Fade effect for body segments
                fade_factor = max(0.3, 1 - (i * 0.05))
                body_color = tuple(int(c * fade_factor) for c in COLORS['snake_body'])
                self.draw_rounded_rect(self.screen, body_color, rect, 6)
    
    def draw_food(self):
        x, y = self.food.position[0] * GRID_SIZE, self.food.position[1] * GRID_SIZE
        
        # Pulsing effect
        pulse_size = int(2 + math.sin(self.food.pulse) * 2)
        rect = pygame.Rect(x + pulse_size, y + pulse_size, 
                          GRID_SIZE - pulse_size * 2, GRID_SIZE - pulse_size * 2)
        
        # Draw shadow
        shadow_rect = pygame.Rect(x + 4, y + 4, GRID_SIZE - 4, GRID_SIZE - 4)
        shadow_surface = pygame.Surface((GRID_SIZE - 4, GRID_SIZE - 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, COLORS['shadow'], shadow_surface.get_rect())
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw food
        pygame.draw.ellipse(self.screen, COLORS['food'], rect)
        
        # Add shine effect
        shine_rect = pygame.Rect(x + pulse_size + 4, y + pulse_size + 4, 
                               max(1, (GRID_SIZE - pulse_size * 2) // 3), 
                               max(1, (GRID_SIZE - pulse_size * 2) // 3))
        pygame.draw.ellipse(self.screen, (255, 255, 255, 150), shine_rect)
    
    def draw_ui(self):
        # Score display
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLORS['text'])
        self.screen.blit(score_text, (20, 20))
        
        # Instructions
        if not self.game_over:
            instruction_text = self.font_small.render("SPACE to pause | Arrow keys to move", True, COLORS['text'])
            self.screen.blit(instruction_text, (20, WINDOW_HEIGHT - 40))
        
        # Game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.font_large.render("GAME OVER", True, COLORS['game_over'])
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Final score
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLORS['text'])
            final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(final_score_text, final_score_rect)
            
            # Restart instruction
            restart_text = self.font_small.render("Press SPACE or R to restart", True, COLORS['accent'])
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)
        
        # Pause screen
        elif self.paused:
            pause_text = self.font_large.render("PAUSED", True, COLORS['accent'])
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
    
    def draw(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        self.draw_snake()
        self.draw_food()
        self.draw_ui()
        pygame.display.flip()
    
    def run(self):
        running = True  
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # Control game speed
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()