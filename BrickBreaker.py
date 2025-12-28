import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (128, 128, 128)
GOLD = (255, 215, 0)

# Brick colors for different rows
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 15
        self.speed = 8
        self.color = GOLD
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        # Draw paddle with gradient effect
        for i in range(self.height):
            color_factor = 1 - (i / self.height) * 0.3
            color = tuple(int(c * color_factor) for c in self.color)
            pygame.draw.rect(screen, color, 
                           (self.x, self.y + i, self.width, 1))
        
        # Draw border
        pygame.draw.rect(screen, WHITE, 
                        (self.x, self.y, self.width, self.height), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 6
        self.vx = random.choice([-1, 1]) * self.speed * 0.7
        self.vy = -self.speed
        self.color = WHITE
        self.trail = []
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Add trail effect
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Wall collision
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.vx = -self.vx
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        
        if self.y - self.radius <= 0:
            self.vy = -self.vy
            self.y = self.radius
            
    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.5)
            radius = int(self.radius * (i / len(self.trail)))
            if radius > 0:
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (int(pos[0]), int(pos[1])), radius)
        
        # Draw ball with glow effect
        for i in range(3):
            color = tuple(max(0, c - i * 50) for c in self.color)
            pygame.draw.circle(screen, color, 
                             (int(self.x), int(self.y)), self.radius + i)
        
        # Draw core
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Brick:
    def __init__(self, x, y, color, points=10):
        self.x = x
        self.y = y
        self.width = 75
        self.height = 30
        self.color = color
        self.points = points
        self.destroyed = False
        
    def draw(self, screen):
        if not self.destroyed:
            # Draw brick with 3D effect
            # Main brick
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, self.width, self.height))
            
            # Highlight
            highlight_color = tuple(min(255, c + 50) for c in self.color)
            pygame.draw.rect(screen, highlight_color, 
                           (self.x, self.y, self.width, 5))
            pygame.draw.rect(screen, highlight_color, 
                           (self.x, self.y, 5, self.height))
            
            # Shadow
            shadow_color = tuple(max(0, c - 50) for c in self.color)
            pygame.draw.rect(screen, shadow_color, 
                           (self.x, self.y + self.height - 5, self.width, 5))
            pygame.draw.rect(screen, shadow_color, 
                           (self.x + self.width - 5, self.y, 5, self.height))
            
            # Border
            pygame.draw.rect(screen, WHITE, 
                           (self.x, self.y, self.width, self.height), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🧱 BRICK BREAKER EXTREME 🧱")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.paddle = Paddle(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.bricks = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False
        
        # Create bricks
        brick_rows = 8
        brick_cols = 10
        brick_width = 75
        brick_height = 30
        margin = 5
        
        start_x = (SCREEN_WIDTH - (brick_cols * brick_width + (brick_cols - 1) * margin)) // 2
        start_y = 50
        
        for row in range(brick_rows):
            for col in range(brick_cols):
                x = start_x + col * (brick_width + margin)
                y = start_y + row * (brick_height + margin)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                points = (brick_rows - row) * 10  # Higher rows worth more points
                brick = Brick(x, y, color, points)
                self.bricks.append(brick)
    
    def handle_collisions(self):
        # Ball-paddle collision
        if self.ball.get_rect().colliderect(self.paddle.get_rect()) and self.ball.vy > 0:
            # Calculate hit position on paddle
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
            hit_pos = max(0, min(1, hit_pos))  # Clamp to [0, 1]
            
            # Adjust ball angle based on hit position
            angle = (hit_pos - 0.5) * math.pi * 0.8  # Max 72 degrees
            speed = math.sqrt(self.ball.vx**2 + self.ball.vy**2)
            
            self.ball.vx = speed * math.sin(angle)
            self.ball.vy = -abs(speed * math.cos(angle))  # Always go up
            
            # Add some randomness
            self.ball.vx += random.uniform(-0.5, 0.5)
        
        # Ball-brick collision
        for brick in self.bricks[:]:
            if not brick.destroyed and self.ball.get_rect().colliderect(brick.get_rect()):
                brick.destroyed = True
                self.score += brick.points
                
                # Create particles
                for _ in range(10):
                    particle = Particle(brick.x + brick.width // 2, 
                                       brick.y + brick.height // 2, 
                                       brick.color)
                    self.particles.append(particle)
                
                # Simple collision response
                ball_center_x = self.ball.x
                ball_center_y = self.ball.y
                brick_center_x = brick.x + brick.width // 2
                brick_center_y = brick.y + brick.height // 2
                
                # Determine collision side
                dx = ball_center_x - brick_center_x
                dy = ball_center_y - brick_center_y
                
                if abs(dx) / brick.width > abs(dy) / brick.height:
                    self.ball.vx = -self.ball.vx
                else:
                    self.ball.vy = -self.ball.vy
                
                break
        
        # Remove destroyed bricks
        self.bricks = [brick for brick in self.bricks if not brick.destroyed]
        
        # Check win condition
        if not self.bricks:
            self.won = True
            self.game_over = True
        
        # Check if ball fell below paddle
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # Reset ball position
                self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def update(self):
        if not self.game_over:
            self.paddle.update()
            self.ball.update()
            self.handle_collisions()
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            r = int(10 * (1 - color_factor))
            g = int(20 * (1 - color_factor))
            b = int(40 + 20 * color_factor)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Stars
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Instructions
        if not self.game_over:
            inst_text = self.small_font.render("Use LEFT/RIGHT arrows to move paddle", True, LIGHT_GRAY)
            self.screen.blit(inst_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.won:
            title = self.big_font.render("🎉 YOU WON! 🎉", True, GOLD)
            subtitle = self.font.render("Congratulations!", True, WHITE)
        else:
            title = self.big_font.render("GAME OVER", True, RED)
            subtitle = self.font.render("Better luck next time!", True, WHITE)
        
        final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
        
        # Center text
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(final_score, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        self.draw_background()
        
        # Draw game objects
        for brick in self.bricks:
            brick.draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        running = False
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()