import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BIRD_SIZE = 25
PIPE_WIDTH = 70
PIPE_GAP = 180
PIPE_SPEED = 4
GRAVITY = 0.6
JUMP_FORCE = -9
FPS = 60

# Ultra-modern color palette
COLORS = {
    'bg_start': (20, 20, 40),  # Deep purple
    'bg_end': (80, 40, 120),   # Purple gradient
    'accent': (255, 100, 255),  # Neon pink
    'accent2': (100, 255, 255), # Neon cyan
    'bird_main': (255, 255, 255),  # White
    'bird_glow': (255, 100, 255),  # Pink glow
    'bird_eye': (0, 255, 200),     # Cyan eye
    'pipe_main': (40, 40, 80),     # Dark purple
    'pipe_glow': (150, 100, 255),  # Purple glow
    'ground': (30, 30, 60),        # Dark ground
    'text': (255, 255, 255),       # White text
    'text_glow': (255, 100, 255),  # Pink glow
    'particle': (255, 200, 100),   # Golden particles
    'trail': (100, 200, 255),      # Blue trail
}

class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x + random.uniform(-2, 2)
        self.velocity_y = velocity_y + random.uniform(-2, 2)
        self.life = 1.0
        self.size = random.uniform(2, 6)
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.life -= 0.02
        self.velocity_y += 0.1  # Gravity on particles
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * self.life)
            color = (*self.color, alpha)
            size = int(self.size * self.life)
            if size > 0:
                # Create surface with per-pixel alpha
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                screen.blit(particle_surf, (self.x - size, self.y - size))

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.size = BIRD_SIZE
        self.rotation = 0
        self.animation_time = 0
        self.trail_points = []
        self.particles = []
        self.glow_size = 0
        
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update rotation based on velocity
        self.rotation = max(-45, min(45, self.velocity * 4))
        
        # Animation for wing flapping
        self.animation_time += 0.4
        
        # Add trail point
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > 15:
            self.trail_points.pop(0)
            
        # Update glow effect
        self.glow_size = 30 + math.sin(self.animation_time * 2) * 5
        
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
            
    def jump(self):
        self.velocity = JUMP_FORCE
        # Create jump particles
        for _ in range(8):
            self.particles.append(Particle(
                self.x + random.uniform(-10, 10),
                self.y + random.uniform(-10, 10),
                COLORS['accent2'],
                random.uniform(-3, 3),
                random.uniform(-5, -2)
            ))
        
    def draw(self, screen):
        # Draw trail
        if len(self.trail_points) > 1:
            for i, point in enumerate(self.trail_points):
                alpha = int(255 * (i / len(self.trail_points)) * 0.5)
                size = int(self.size * (i / len(self.trail_points)) * 0.8)
                if size > 0:
                    trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (*COLORS['trail'], alpha), (size, size), size)
                    screen.blit(trail_surf, (point[0] - size, point[1] - size))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
            
        # Draw glow effect
        glow_surf = pygame.Surface((self.glow_size * 2, self.glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['bird_glow'], 30), 
                         (self.glow_size, self.glow_size), self.glow_size)
        screen.blit(glow_surf, (self.x - self.glow_size, self.y - self.glow_size))
        
        # Create bird surface with rotation
        bird_surface = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        center = self.size * 1.5
        
        # Wing animation
        wing_flap = math.sin(self.animation_time) * 0.3
        wing_size = self.size * 0.8
        
        # Draw wings (behind bird)
        wing_points = [
            (center - wing_size, center + wing_flap * 10),
            (center - wing_size * 1.5, center - wing_size * 0.5 + wing_flap * 10),
            (center - wing_size * 0.3, center - wing_size * 0.8 + wing_flap * 10),
            (center + wing_size * 0.3, center - wing_size * 0.3 + wing_flap * 10)
        ]
        pygame.draw.polygon(bird_surface, COLORS['accent'], wing_points)
        
        # Draw bird body (main circle)
        pygame.draw.circle(bird_surface, COLORS['bird_main'], (center, center), self.size)
        
        # Draw bird outline glow
        pygame.draw.circle(bird_surface, COLORS['bird_glow'], (center, center), self.size + 3, 3)
        
        # Draw beak
        beak_points = [
            (center + self.size - 5, center - 3),
            (center + self.size + 15, center),
            (center + self.size - 5, center + 3)
        ]
        pygame.draw.polygon(bird_surface, COLORS['accent2'], beak_points)
        
        # Draw eye
        eye_size = 8
        pygame.draw.circle(bird_surface, COLORS['bird_eye'], 
                         (center + 5, center - 5), eye_size)
        pygame.draw.circle(bird_surface, (0, 0, 0), 
                         (center + 7, center - 5), eye_size - 3)
        
        # Add eye glow
        pygame.draw.circle(bird_surface, COLORS['bird_eye'], 
                         (center + 5, center - 5), eye_size + 2, 2)
        
        # Rotate and draw
        rotated_bird = pygame.transform.rotate(bird_surface, self.rotation)
        rect = rotated_bird.get_rect(center=(self.x, self.y))
        screen.blit(rotated_bird, rect)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, 
                          self.size, self.size)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - 200)
        self.width = PIPE_WIDTH
        self.passed = False
        self.glow_intensity = 0
        
    def update(self):
        self.x -= PIPE_SPEED
        self.glow_intensity = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        
    def draw(self, screen):
        # Pipe dimensions
        top_height = self.gap_y - PIPE_GAP//2
        bottom_y = self.gap_y + PIPE_GAP//2
        bottom_height = SCREEN_HEIGHT - bottom_y
        
        # Draw glow effect
        glow_width = self.width + 20
        glow_alpha = int(100 * self.glow_intensity)
        
        # Top pipe glow
        top_glow_surf = pygame.Surface((glow_width, top_height + 20), pygame.SRCALPHA)
        pygame.draw.rect(top_glow_surf, (*COLORS['pipe_glow'], glow_alpha), 
                        (0, 0, glow_width, top_height + 20))
        screen.blit(top_glow_surf, (self.x - 10, -10))
        
        # Bottom pipe glow
        bottom_glow_surf = pygame.Surface((glow_width, bottom_height + 20), pygame.SRCALPHA)
        pygame.draw.rect(bottom_glow_surf, (*COLORS['pipe_glow'], glow_alpha), 
                        (0, 0, glow_width, bottom_height + 20))
        screen.blit(bottom_glow_surf, (self.x - 10, bottom_y - 10))
        
        # Draw main pipes
        pygame.draw.rect(screen, COLORS['pipe_main'], (self.x, 0, self.width, top_height))
        pygame.draw.rect(screen, COLORS['pipe_main'], (self.x, bottom_y, self.width, bottom_height))
        
        # Draw pipe borders
        pygame.draw.rect(screen, COLORS['pipe_glow'], (self.x, 0, self.width, top_height), 3)
        pygame.draw.rect(screen, COLORS['pipe_glow'], (self.x, bottom_y, self.width, bottom_height), 3)
        
        # Draw pipe caps
        cap_height = 25
        cap_width = self.width + 10
        
        # Top cap
        top_cap_y = top_height - cap_height
        pygame.draw.rect(screen, COLORS['pipe_main'], (self.x - 5, top_cap_y, cap_width, cap_height))
        pygame.draw.rect(screen, COLORS['pipe_glow'], (self.x - 5, top_cap_y, cap_width, cap_height), 3)
        
        # Bottom cap
        pygame.draw.rect(screen, COLORS['pipe_main'], (self.x - 5, bottom_y, cap_width, cap_height))
        pygame.draw.rect(screen, COLORS['pipe_glow'], (self.x - 5, bottom_y, cap_width, cap_height), 3)
        
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - PIPE_GAP//2)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP//2, 
                                self.width, SCREEN_HEIGHT - (self.gap_y + PIPE_GAP//2))
        return [top_rect, bottom_rect]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NEON FLAPPY BIRD")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            self.font_title = pygame.font.Font(None, 64)
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_title = pygame.font.Font(None, 64)
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
            
        self.background_particles = []
        self.reset_game()
        
    def reset_game(self):
        self.bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.background_particles = []
        
        # Create background particles
        for _ in range(50):
            self.background_particles.append(Particle(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                COLORS['particle'],
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ))
        
    def draw_animated_background(self):
        """Draw animated gradient background with particles"""
        # Create gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(COLORS['bg_start'][0] * (1 - ratio) + COLORS['bg_end'][0] * ratio)
            g = int(COLORS['bg_start'][1] * (1 - ratio) + COLORS['bg_end'][1] * ratio)
            b = int(COLORS['bg_start'][2] * (1 - ratio) + COLORS['bg_end'][2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        # Update and draw background particles
        for particle in self.background_particles:
            particle.update()
            particle.draw(self.screen)
            
            # Reset particle if it's dead
            if particle.life <= 0:
                particle.x = random.randint(0, SCREEN_WIDTH)
                particle.y = random.randint(0, SCREEN_HEIGHT)
                particle.life = 1.0
                
    def draw_glowing_text(self, text, font, color, glow_color, pos):
        """Draw text with glow effect"""
        # Draw glow (multiple layers)
        for offset in range(5, 0, -1):
            glow_surf = font.render(text, True, glow_color)
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    if dx*dx + dy*dy <= offset*offset:
                        glow_surf.set_alpha(20)
                        rect = glow_surf.get_rect(center=(pos[0] + dx, pos[1] + dy))
                        self.screen.blit(glow_surf, rect)
        
        # Draw main text
        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect(center=pos)
        self.screen.blit(text_surf, rect)
        
    def draw_ui(self):
        """Draw modern UI elements"""
        if not self.game_started:
            # Animated title
            title_y = 120 + math.sin(pygame.time.get_ticks() * 0.003) * 10
            self.draw_glowing_text("NEON FLAPPY BIRD", self.font_title, 
                                 COLORS['text'], COLORS['text_glow'], 
                                 (SCREEN_WIDTH//2, title_y))
            
            # Pulsing start instruction
            alpha = int(255 * (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5)
            start_color = (*COLORS['accent2'], alpha)
            self.draw_glowing_text("PRESS SPACE TO START", self.font_medium, 
                                 start_color[:3], COLORS['accent2'], 
                                 (SCREEN_WIDTH//2, 300))
            
            self.draw_glowing_text("SPACE = FLAP WINGS", self.font_small, 
                                 COLORS['text'], COLORS['text_glow'], 
                                 (SCREEN_WIDTH//2, 350))
            
        else:
            # Animated score
            score_scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.01) * 0.1
            score_font = pygame.font.Font(None, int(48 * score_scale))
            self.draw_glowing_text(f"SCORE: {self.score}", score_font, 
                                 COLORS['text'], COLORS['text_glow'], 
                                 (SCREEN_WIDTH//2, 50))
            
        if self.game_over:
            # Animated game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((*COLORS['bg_start'], 180))
            self.screen.blit(overlay, (0, 0))
            
            # Pulsing game over text
            pulse = math.sin(pygame.time.get_ticks() * 0.008) * 0.2 + 1.0
            game_over_font = pygame.font.Font(None, int(64 * pulse))
            self.draw_glowing_text("GAME OVER", game_over_font, 
                                 COLORS['accent'], COLORS['text_glow'], 
                                 (SCREEN_WIDTH//2, 200))
            
            self.draw_glowing_text(f"FINAL SCORE: {self.score}", self.font_large, 
                                 COLORS['text'], COLORS['text_glow'], 
                                 (SCREEN_WIDTH//2, 280))
            
            # Blinking restart text
            if int(pygame.time.get_ticks() / 500) % 2:
                self.draw_glowing_text("PRESS R TO RESTART", self.font_medium, 
                                     COLORS['accent2'], COLORS['text_glow'], 
                                     (SCREEN_WIDTH//2, 350))
                
            self.draw_glowing_text("ESC TO QUIT", self.font_small, 
                                 COLORS['text'], COLORS['text_glow'], 
                                 (SCREEN_WIDTH//2, 400))
            
    def update(self):
        if not self.game_started or self.game_over:
            return
            
        # Update bird
        self.bird.update()
        
        # Check ground collision
        if self.bird.y > SCREEN_HEIGHT - 30 or self.bird.y < 0:
            self.game_over = True
            
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Remove pipes that are off screen
            if pipe.x < -pipe.width:
                self.pipes.remove(pipe)
                
            # Check scoring
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                
                # Create score particles
                for _ in range(10):
                    self.bird.particles.append(Particle(
                        self.bird.x + random.uniform(-20, 20),
                        self.bird.y + random.uniform(-20, 20),
                        COLORS['particle'],
                        random.uniform(-2, 2),
                        random.uniform(-3, 0)
                    ))
                
            # Check collisions
            bird_rect = self.bird.get_rect()
            for pipe_rect in pipe.get_rects():
                if bird_rect.colliderect(pipe_rect):
                    self.game_over = True
                    
        # Spawn new pipes
        if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 300:
            self.pipes.append(Pipe(SCREEN_WIDTH))
            
    def draw(self):
        # Draw animated background
        self.draw_animated_background()
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    elif not self.game_over:
                        self.bird.jump()
                        
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                    
                elif event.key == pygame.K_ESCAPE:
                    return False
                    
        return True
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()