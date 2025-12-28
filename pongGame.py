import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 120
BALL_SIZE = 20
PADDLE_SPEED = 8
BALL_SPEED = 7

# Exciting color palette with neon vibes
COLORS = {
    'bg': (8, 8, 25),             # Deep space blue
    'primary': (57, 255, 20),     # Electric lime
    'secondary': (255, 20, 147),  # Hot pink
    'accent': (0, 191, 255),      # Electric blue
    'gold': (255, 215, 0),        # Gold
    'purple': (138, 43, 226),     # Purple
    'orange': (255, 165, 0),      # Orange
    'white': (255, 255, 255),
    'gray': (128, 128, 128),
    'red': (255, 69, 0),          # Red-orange
    'cyan': (0, 255, 255),        # Cyan
}

class AnimatedBackground:
    def __init__(self):
        self.stars = []
        self.grid_lines = []
        self.time = 0
        self.create_stars()
        self.create_grid()
    
    def create_stars(self):
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2),
                'brightness': random.randint(100, 255),
                'size': random.randint(1, 3)
            })
    
    def create_grid(self):
        for i in range(0, SCREEN_WIDTH, 50):
            self.grid_lines.append({'x': i, 'vertical': True})
        for i in range(0, SCREEN_HEIGHT, 50):
            self.grid_lines.append({'y': i, 'vertical': False})
    
    def update(self):
        self.time += 0.02
        for star in self.stars:
            star['brightness'] = int(127 + 127 * math.sin(self.time + star['x'] * 0.01))
    
    def draw(self, screen):
        # Draw animated grid
        for line in self.grid_lines:
            alpha = int(30 + 20 * math.sin(self.time))
            if line['vertical']:
                pygame.draw.line(screen, (*COLORS['accent'], alpha), 
                               (line['x'], 0), (line['x'], SCREEN_HEIGHT), 1)
            else:
                pygame.draw.line(screen, (*COLORS['accent'], alpha), 
                               (0, line['y']), (SCREEN_WIDTH, line['y']), 1)
        
        # Draw twinkling stars
        for star in self.stars:
            color = (*COLORS['white'], star['brightness'])
            star_surface = pygame.Surface((star['size'] * 2, star['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, color, (star['size'], star['size']), star['size'])
            screen.blit(star_surface, (star['x'], star['y']))

class Paddle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.color = color
        self.speed = PADDLE_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.glow_intensity = 0
        self.hit_effect = 0
        self.energy_particles = []
        
    def move_up(self):
        if self.y > 0:
            self.y -= self.speed
            self.rect.y = self.y
            self.create_movement_particles()
    
    def move_down(self):
        if self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            self.rect.y = self.y
            self.create_movement_particles()
    
    def create_movement_particles(self):
        for _ in range(3):
            self.energy_particles.append({
                'x': self.x + self.width // 2,
                'y': self.y + random.randint(0, self.height),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'life': 20,
                'size': random.randint(2, 4)
            })
    
    def hit_effect_trigger(self):
        self.hit_effect = 30
        self.glow_intensity = 100
        # Create explosion particles
        for _ in range(25):
            self.energy_particles.append({
                'x': self.x + self.width // 2,
                'y': self.y + self.height // 2,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'life': 40,
                'size': random.randint(3, 6)
            })
    
    def update(self):
        if self.hit_effect > 0:
            self.hit_effect -= 1
        if self.glow_intensity > 0:
            self.glow_intensity -= 2
        
        # Update energy particles
        for particle in self.energy_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['size'] = max(1, particle['size'] - 0.1)
            if particle['life'] <= 0:
                self.energy_particles.remove(particle)
    
    def draw(self, screen):
        # Draw energy particles
        for particle in self.energy_particles:
            alpha = int(255 * particle['life'] / 40)
            size = int(particle['size'])
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color[:3], alpha), (size, size), size)
            screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        # Draw multiple glow layers
        for i in range(5):
            glow_size = 8 + i * 4
            alpha = max(0, self.glow_intensity - i * 20)
            glow_rect = pygame.Rect(self.x - glow_size//2, self.y - glow_size//2, 
                                  self.width + glow_size, self.height + glow_size)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.color[:3], alpha), 
                           (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        # Draw paddle with hit effect
        paddle_color = self.color
        if self.hit_effect > 0:
            # Flash effect
            flash_intensity = self.hit_effect / 30
            paddle_color = (
                min(255, int(self.color[0] + 100 * flash_intensity)),
                min(255, int(self.color[1] + 100 * flash_intensity)),
                min(255, int(self.color[2] + 100 * flash_intensity))
            )
        
        pygame.draw.rect(screen, paddle_color, self.rect, border_radius=8)
        
        # Draw energy core
        core_y = self.y + self.height // 2
        for i in range(3):
            core_alpha = 150 - i * 50
            core_size = 3 - i
            core_surface = pygame.Surface((core_size * 2, core_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(core_surface, (*paddle_color, core_alpha), (core_size, core_size), core_size)
            screen.blit(core_surface, (self.x + self.width//2 - core_size, core_y - core_size))

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BALL_SIZE
        self.speed_x = BALL_SPEED
        self.speed_y = BALL_SPEED
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.trail = []
        self.energy_level = 0
        self.rainbow_mode = False
        self.rainbow_time = 0
        self.impact_particles = []
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x - self.size//2
        self.rect.y = self.y - self.size//2
        
        # Add to trail with energy info
        self.trail.append((self.x, self.y, self.energy_level))
        if len(self.trail) > 15:
            self.trail.pop(0)
        
        # Update rainbow effect
        if self.rainbow_mode:
            self.rainbow_time += 0.1
        
        # Bounce off top and bottom walls with particles
        if self.y <= self.size//2 or self.y >= SCREEN_HEIGHT - self.size//2:
            self.speed_y = -self.speed_y
            self.create_wall_particles()
    
    def create_wall_particles(self):
        for _ in range(15):
            self.impact_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': random.uniform(-4, 4),
                'vy': random.uniform(-4, 4),
                'life': 30,
                'color': COLORS['orange']
            })
    
    def bounce_paddle(self, paddle):
        # Calculate bounce angle based on where ball hits paddle
        hit_pos = (self.y - paddle.y) / paddle.height
        angle = (hit_pos - 0.5) * math.pi/3  # Max 60 degrees
        
        speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        self.speed_x = speed * math.cos(angle) * (-1 if self.speed_x > 0 else 1)
        self.speed_y = speed * math.sin(angle)
        
        # Increase speed and energy
        self.speed_x *= 1.05
        self.speed_y *= 1.05
        self.energy_level = min(100, self.energy_level + 10)
        
        # Activate rainbow mode at high energy
        if self.energy_level > 50:
            self.rainbow_mode = True
        
        # Cap maximum speed
        max_speed = 12
        if abs(self.speed_x) > max_speed:
            self.speed_x = max_speed * (1 if self.speed_x > 0 else -1)
        if abs(self.speed_y) > max_speed:
            self.speed_y = max_speed * (1 if self.speed_y > 0 else -1)
        
        # Trigger paddle hit effect
        paddle.hit_effect_trigger()
    
    def update(self):
        # Update impact particles
        for particle in self.impact_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.impact_particles.remove(particle)
        
        # Decay energy slowly
        if self.energy_level > 0:
            self.energy_level -= 0.5
        if self.energy_level <= 30:
            self.rainbow_mode = False
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed_x = BALL_SPEED * (1 if self.speed_x > 0 else -1)
        self.speed_y = BALL_SPEED * (1 if self.speed_y > 0 else -1)
        self.trail = []
        self.energy_level = 0
        self.rainbow_mode = False
        self.impact_particles = []
    
    def get_ball_color(self):
        if self.rainbow_mode:
            # Rainbow effect
            r = int(127 + 127 * math.sin(self.rainbow_time))
            g = int(127 + 127 * math.sin(self.rainbow_time + 2))
            b = int(127 + 127 * math.sin(self.rainbow_time + 4))
            return (r, g, b)
        else:
            # Energy-based color
            energy_ratio = self.energy_level / 100
            if energy_ratio < 0.3:
                return COLORS['primary']
            elif energy_ratio < 0.6:
                return COLORS['orange']
            else:
                return COLORS['red']
    
    def draw(self, screen):
        # Draw impact particles
        for particle in self.impact_particles:
            alpha = int(255 * particle['life'] / 30)
            size = max(1, int(particle['life'] / 10))
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle['color'], alpha), (size, size), size)
            screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        ball_color = self.get_ball_color()
        
        # Draw dynamic trail
        for i, (trail_x, trail_y, energy) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail) * 0.6)
            size = int(self.size * (i + 1) / len(self.trail) * 0.8)
            trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Trail color based on energy at that point
            if energy > 50:
                trail_color = COLORS['red']
            elif energy > 20:
                trail_color = COLORS['orange']
            else:
                trail_color = ball_color
            
            pygame.draw.circle(trail_surface, (*trail_color, alpha), (size, size), size)
            screen.blit(trail_surface, (trail_x - size, trail_y - size))
        
        # Draw multi-layer glow
        for i in range(6):
            glow_size = self.size + i * 8
            alpha = max(0, 100 - i * 15)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*ball_color, alpha), (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
        
        # Draw main ball
        pygame.draw.circle(screen, ball_color, (int(self.x), int(self.y)), self.size // 2)
        
        # Draw energy core
        if self.energy_level > 0:
            core_size = int(self.size // 4 * (self.energy_level / 100))
            core_color = (255, 255, 255) if self.rainbow_mode else ball_color
            pygame.draw.circle(screen, core_color, (int(self.x), int(self.y)), core_size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("⚡ NEON PONG EXTREME ⚡")
        self.clock = pygame.time.Clock()
        
        # Create animated background
        self.background = AnimatedBackground()
        
        # Create paddles with exciting colors
        self.player1 = Paddle(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, COLORS['secondary'])
        self.player2 = Paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, COLORS['accent'])
        
        # Create ball
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Scores
        self.score1 = 0
        self.score2 = 0
        
        # Fonts
        self.font_huge = pygame.font.Font(None, 120)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.paused = False
        self.winner = None
        self.celebration_particles = []
        self.time = 0
        self.screen_shake = 0
        
        # UI animations
        self.title_bounce = 0
        self.score_pulse = [0, 0]
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.winner:
                    self.reset_game()
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if not self.paused and not self.winner:
            # Player 1 controls (W/S)
            if keys[pygame.K_w]:
                self.player1.move_up()
            if keys[pygame.K_s]:
                self.player1.move_down()
            
            # Player 2 controls (Up/Down arrows)
            if keys[pygame.K_UP]:
                self.player2.move_up()
            if keys[pygame.K_DOWN]:
                self.player2.move_down()
        
        return True
    
    def update(self):
        self.time += 0.016
        self.background.update()
        self.player1.update()
        self.player2.update()
        self.ball.update()
        
        # Update UI animations
        self.title_bounce = math.sin(self.time * 3) * 5
        self.score_pulse[0] = max(0, self.score_pulse[0] - 2)
        self.score_pulse[1] = max(0, self.score_pulse[1] - 2)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        if self.paused or self.winner:
            return
        
        # Move ball
        self.ball.move()
        
        # Check paddle collisions
        if self.ball.rect.colliderect(self.player1.rect) and self.ball.speed_x < 0:
            self.ball.bounce_paddle(self.player1)
            self.score_pulse[0] = 20
            self.screen_shake = 5
        
        if self.ball.rect.colliderect(self.player2.rect) and self.ball.speed_x > 0:
            self.ball.bounce_paddle(self.player2)
            self.score_pulse[1] = 20
            self.screen_shake = 5
        
        # Check scoring
        if self.ball.x < 0:
            self.score2 += 1
            self.ball.reset()
            self.create_score_celebration(False)
            self.score_pulse[1] = 50
        elif self.ball.x > SCREEN_WIDTH:
            self.score1 += 1
            self.ball.reset()
            self.create_score_celebration(True)
            self.score_pulse[0] = 50
        
        # Check win condition
        if self.score1 >= 10:
            self.winner = "PLAYER 1"
            self.create_victory_celebration()
        elif self.score2 >= 10:
            self.winner = "PLAYER 2"
            self.create_victory_celebration()
        
        # Update celebration particles
        self.update_celebration_particles()
    
    def create_score_celebration(self, player1_scored):
        x = 100 if player1_scored else SCREEN_WIDTH - 100
        color = COLORS['secondary'] if player1_scored else COLORS['accent']
        
        for _ in range(50):
            self.celebration_particles.append({
                'x': x,
                'y': SCREEN_HEIGHT // 2,
                'vx': random.uniform(-8, 8),
                'vy': random.uniform(-8, 8),
                'life': 60,
                'color': color,
                'size': random.randint(3, 8)
            })
    
    def create_victory_celebration(self):
        for _ in range(200):
            self.celebration_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'life': 120,
                'color': random.choice([COLORS['gold'], COLORS['primary'], COLORS['secondary'], COLORS['accent']]),
                'size': random.randint(4, 12)
            })
    
    def update_celebration_particles(self):
        for particle in self.celebration_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.celebration_particles.remove(particle)
    
    def draw_animated_center_line(self):
        # Draw pulsing center line
        pulse = math.sin(self.time * 4) * 0.3 + 0.7
        dash_height = int(40 * pulse)
        dash_gap = 25
        y = 0
        
        while y < SCREEN_HEIGHT:
            alpha = int(255 * pulse)
            line_surface = pygame.Surface((8, dash_height), pygame.SRCALPHA)
            pygame.draw.rect(line_surface, (*COLORS['primary'], alpha), (0, 0, 8, dash_height), border_radius=4)
            self.screen.blit(line_surface, (SCREEN_WIDTH // 2 - 4, y))
            y += dash_height + dash_gap
    
    def draw_celebration_particles(self):
        for particle in self.celebration_particles:
            alpha = int(255 * particle['life'] / 120)
            size = int(particle['size'] * particle['life'] / 120)
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle['color'][:3], alpha), (size, size), size)
            self.screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
    
    def draw_exciting_ui(self):
        # Apply screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Draw animated title
        title_y = 20 + self.title_bounce
        title_colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
        title_text = "⚡ NEON PONG EXTREME ⚡"
        
        for i, char in enumerate(title_text):
            char_color = title_colors[i % len(title_colors)]
            char_surface = self.font_medium.render(char, True, char_color)
            char_y = title_y + math.sin(self.time * 5 + i * 0.3) * 3
            self.screen.blit(char_surface, (SCREEN_WIDTH // 2 - 200 + i * 20 + shake_x, char_y + shake_y))
        
        # Draw pulsing scores with glow
        score1_scale = 1 + self.score_pulse[0] * 0.02
        score2_scale = 1 + self.score_pulse[1] * 0.02
        
        # Score 1
        score1_size = int(72 * score1_scale)
        score1_font = pygame.font.Font(None, score1_size)
        score1_text = score1_font.render(str(self.score1), True, COLORS['secondary'])
        
        # Multi-layer glow for scores
        for i in range(5):
            glow_alpha = max(0, self.score_pulse[0] * 5 - i * 10)
            if glow_alpha > 0:
                glow_surface = score1_font.render(str(self.score1), True, (*COLORS['secondary'][:3], glow_alpha))
                offset = i * 2
                self.screen.blit(glow_surface, (SCREEN_WIDTH // 4 - offset + shake_x, 100 - offset + shake_y))
        
        self.screen.blit(score1_text, (SCREEN_WIDTH // 4 + shake_x, 100 + shake_y))
        
        # Score 2
        score2_size = int(72 * score2_scale)
        score2_font = pygame.font.Font(None, score2_size)
        score2_text = score2_font.render(str(self.score2), True, COLORS['accent'])
        
        for i in range(5):
            glow_alpha = max(0, self.score_pulse[1] * 5 - i * 10)
            if glow_alpha > 0:
                glow_surface = score2_font.render(str(self.score2), True, (*COLORS['accent'][:3], glow_alpha))
                offset = i * 2
                self.screen.blit(glow_surface, (3 * SCREEN_WIDTH // 4 - offset + shake_x, 100 - offset + shake_y))
        
        self.screen.blit(score2_text, (3 * SCREEN_WIDTH // 4 + shake_x, 100 + shake_y))
        
        # Draw energy bars
        energy_width = 200
        energy_height = 8
        
        # Player 1 energy (based on recent activity)
        p1_energy = min(100, self.score_pulse[0] * 5)
        pygame.draw.rect(self.screen, COLORS['gray'], (50, 200, energy_width, energy_height))
        pygame.draw.rect(self.screen, COLORS['secondary'], (50, 200, int(energy_width * p1_energy / 100), energy_height))
        
        # Player 2 energy
        p2_energy = min(100, self.score_pulse[1] * 5)
        pygame.draw.rect(self.screen, COLORS['gray'], (SCREEN_WIDTH - 250, 200, energy_width, energy_height))
        pygame.draw.rect(self.screen, COLORS['accent'], (SCREEN_WIDTH - 250, 200, int(energy_width * p2_energy / 100), energy_height))
        
        # Draw ball energy indicator
        ball_energy_y = 250
        ball_energy_width = int(300 * self.ball.energy_level / 100)
        if ball_energy_width > 0:
            ball_energy_color = COLORS['red'] if self.ball.rainbow_mode else COLORS['orange']
            pygame.draw.rect(self.screen, ball_energy_color, 
                           (SCREEN_WIDTH // 2 - 150, ball_energy_y, ball_energy_width, 6))
            
            energy_text = self.font_small.render(f"BALL ENERGY: {int(self.ball.energy_level)}%", True, ball_energy_color)
            self.screen.blit(energy_text, (SCREEN_WIDTH // 2 - 80, ball_energy_y + 15))
        
        # Draw exciting player labels
        p1_label = self.font_small.render("🔥 PLAYER 1 [W/S] 🔥", True, COLORS['secondary'])
        p2_label = self.font_small.render("⚡ PLAYER 2 [↑/↓] ⚡", True, COLORS['accent'])
        
        self.screen.blit(p1_label, (30, SCREEN_HEIGHT - 40))
        self.screen.blit(p2_label, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))
        
        # Draw game state messages
        if self.paused:
            pause_text = self.font_large.render("⏸️ GAME PAUSED ⏸️", True, COLORS['gold'])
            resume_text = self.font_medium.render("Press SPACE to resume the action!", True, COLORS['white'])
            
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            
            # Add pulsing effect
            pulse_alpha = int(127 + 127 * math.sin(self.time * 6))
            pause_surface = pygame.Surface(pause_text.get_size(), pygame.SRCALPHA)
            pause_surface.fill((*COLORS['gold'], pulse_alpha))
            self.screen.blit(pause_surface, pause_rect)
            self.screen.blit(pause_text, pause_rect)
            self.screen.blit(resume_text, resume_rect)
        
        if self.winner:
            # Animated winner text
            winner_bounce = math.sin(self.time * 8) * 10
            winner_text = self.font_huge.render(f"🏆 {self.winner} WINS! 🏆", True, COLORS['gold'])
            restart_text = self.font_large.render("Press R to restart the battle!", True, COLORS['primary'])
            
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + winner_bounce))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            
            # Rainbow effect for winner text
            rainbow_surface = pygame.Surface(winner_text.get_size(), pygame.SRCALPHA)
            r = int(127 + 127 * math.sin(self.time * 3))
            g = int(127 + 127 * math.sin(self.time * 3 + 2))
            b = int(127 + 127 * math.sin(self.time * 3 + 4))
            rainbow_surface.fill((r, g, b, 200))
            self.screen.blit(rainbow_surface, winner_rect)
            self.screen.blit(winner_text, winner_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.score1 = 0
        self.score2 = 0
        self.winner = None
        self.ball.reset()
        self.celebration_particles = []
        self.score_pulse = [0, 0]
        self.screen_shake = 0
        self.player1.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.player2.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.player1.rect.y = self.player1.y
        self.player2.rect.y = self.player2.y
        self.player1.hit_effect = 0
        self.player2.hit_effect = 0
        self.player1.energy_particles = []
        self.player2.energy_particles = []
    
    def draw(self):
        # Clear screen with animated background
        self.screen.fill(COLORS['bg'])
        
        # Draw animated background
        self.background.draw(self.screen)
        
        # Draw animated center line
        self.draw_animated_center_line()
        
        # Draw celebration particles
        self.draw_celebration_particles()
        
        # Draw game objects
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw exciting UI
        self.draw_exciting_ui()
        
        # Add scanline effect for retro feel
        for i in range(0, SCREEN_HEIGHT, 4):
            alpha = 20
            scanline_surface = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
            scanline_surface.fill((255, 255, 255, alpha))
            self.screen.blit(scanline_surface, (0, i))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()