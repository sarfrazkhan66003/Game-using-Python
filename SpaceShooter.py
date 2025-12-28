import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Modern color palette
DARK_BG = (8, 12, 20)
ACCENT_BLUE = (0, 150, 255)
NEON_CYAN = (0, 255, 255)
NEON_GREEN = (0, 255, 100)
NEON_PINK = (255, 0, 150)
NEON_PURPLE = (150, 0, 255)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
ORANGE = (255, 150, 0)
GRAY = (100, 100, 100)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.brightness = random.randint(50, 200)
        self.size = random.randint(1, 3)
    
    def update(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT)
    
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y, color, size=4):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.color = color
        self.size = size
        self.life = 40
        self.max_life = 40
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, (self.life / self.max_life) * self.size)
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = max(1, int(self.size))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 35
        self.speed = 4  # Reduced from 8
        self.bullets = []
        self.last_shot = 0
        self.shot_delay = 200  # milliseconds
        self.health = 100
        self.max_health = 100
        self.engine_particles = []
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Smoother movement
        if keys[pygame.K_UP] and self.y > 50:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height - 50:
            self.y += self.speed
        if keys[pygame.K_LEFT] and self.x > 50:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width - 50:
            self.x += self.speed
            
        # Shooting
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shot_delay:
                # Double bullets from wings
                self.bullets.append(Bullet(self.x + self.width, self.y + 8, 12, NEON_CYAN))
                self.bullets.append(Bullet(self.x + self.width, self.y + self.height - 8, 12, NEON_CYAN))
                self.last_shot = current_time
        
        # Engine particles
        if random.random() < 0.3:
            self.engine_particles.append(Particle(self.x - 5, self.y + self.height//2, ACCENT_BLUE, 3))
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x > SCREEN_WIDTH:
                self.bullets.remove(bullet)
        
        # Update engine particles
        for particle in self.engine_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.engine_particles.remove(particle)
    
    def draw(self, screen):
        # Draw engine particles first
        for particle in self.engine_particles:
            particle.draw(screen)
        
        # Main fuselage (realistic plane body)
        pygame.draw.ellipse(screen, GRAY, (self.x + 10, self.y + 12, self.width - 20, 12))
        
        # Cockpit
        pygame.draw.ellipse(screen, ACCENT_BLUE, (self.x + 45, self.y + 8, 25, 20))
        
        # Wings
        wing_points = [
            (self.x + 20, self.y + 15),
            (self.x + 60, self.y + 5),
            (self.x + 60, self.y + 30),
            (self.x + 20, self.y + 20)
        ]
        pygame.draw.polygon(screen, NEON_CYAN, wing_points)
        
        # Tail
        tail_points = [
            (self.x, self.y + 17),
            (self.x + 15, self.y + 10),
            (self.x + 15, self.y + 25)
        ]
        pygame.draw.polygon(screen, GRAY, tail_points)
        
        # Engine exhausts
        pygame.draw.circle(screen, ORANGE, (self.x + 5, self.y + 17), 3)
        
        # Nose cone
        pygame.draw.polygon(screen, WHITE, [
            (self.x + 70, self.y + 17),
            (self.x + 80, self.y + 17),
            (self.x + 75, self.y + 12),
            (self.x + 75, self.y + 22)
        ])
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 8, self.width - 20, self.height - 16)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.speed = random.uniform(1.5, 3.5)  # Slower
        self.color = random.choice([NEON_PURPLE, RED, NEON_PINK])
        self.health = 30
        self.engine_particles = []
        
    def update(self):
        self.x -= self.speed
        
        # Enemy engine particles
        if random.random() < 0.2:
            self.engine_particles.append(Particle(self.x + self.width, self.y + self.height//2, self.color, 2))
        
        # Update engine particles
        for particle in self.engine_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.engine_particles.remove(particle)
        
    def draw(self, screen):
        # Draw engine particles first
        for particle in self.engine_particles:
            particle.draw(screen)
        
        # Enemy plane body
        pygame.draw.ellipse(screen, GRAY, (self.x + 10, self.y + 10, self.width - 20, 10))
        
        # Enemy wings
        wing_points = [
            (self.x + 15, self.y + 12),
            (self.x + 45, self.y + 5),
            (self.x + 45, self.y + 25),
            (self.x + 15, self.y + 18)
        ]
        pygame.draw.polygon(screen, self.color, wing_points)
        
        # Enemy tail
        tail_points = [
            (self.x + 50, self.y + 15),
            (self.x + 60, self.y + 10),
            (self.x + 60, self.y + 20)
        ]
        pygame.draw.polygon(screen, GRAY, tail_points)
        
        # Enemy nose
        pygame.draw.polygon(screen, WHITE, [
            (self.x, self.y + 15),
            (self.x + 10, self.y + 12),
            (self.x + 10, self.y + 18)
        ])
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 8, self.width - 10, self.height - 16)

class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 12
        self.height = 4
        
    def update(self):
        self.x += self.speed
        
    def draw(self, screen):
        # Glowing bullet effect
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, WHITE, (self.x + 2, self.y + 1, self.width - 4, self.height - 2))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🚀 SKY DOMINATION - Modern Air Combat")
        self.clock = pygame.time.Clock()
        self.player = Player(100, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.particles = []
        self.stars = [Star() for _ in range(150)]
        self.score = 0
        self.level = 1
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 64)
        self.title_font = pygame.font.Font(None, 48)
        self.enemy_spawn_timer = 0
        self.game_over = False
        self.running = True
        self.game_started = False
        self.menu_selection = 0
        
    def draw_menu(self):
        # Animated background
        self.screen.fill(DARK_BG)
        
        # Stars
        for star in self.stars:
            star.update()
            star.draw(self.screen)
        
        # Title with glow effect
        title_text = self.title_font.render("🚀 SKY DOMINATION", True, NEON_CYAN)
        title_glow = self.title_font.render("🚀 SKY DOMINATION", True, ACCENT_BLUE)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        glow_rect = title_glow.get_rect(center=(SCREEN_WIDTH//2 + 2, 202))
        
        self.screen.blit(title_glow, glow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Modern Air Combat Experience", True, GOLD)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        menu_options = ["START MISSION", "QUIT"]
        for i, option in enumerate(menu_options):
            color = NEON_GREEN if i == self.menu_selection else WHITE
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 50))
            
            if i == self.menu_selection:
                # Selection highlight
                pygame.draw.rect(self.screen, ACCENT_BLUE, 
                               (text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20), 2)
            
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "🎮 Arrow Keys: Move Aircraft",
            "🔥 Spacebar: Fire Weapons",
            "💪 Survive and Dominate the Skies!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, NEON_CYAN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 500 + i * 30))
            self.screen.blit(text, text_rect)
    
    def spawn_enemy(self):
        if len(self.enemies) < 6 + self.level:  # More enemies as level increases
            y = random.randint(80, SCREEN_HEIGHT - 100)
            self.enemies.append(Enemy(SCREEN_WIDTH, y))
    
    def create_explosion(self, x, y, color):
        for _ in range(25):
            self.particles.append(Particle(x, y, color, random.uniform(3, 8)))
    
    def handle_collisions(self):
        # Player bullets vs enemies
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 100
                    self.create_explosion(enemy.x, enemy.y, enemy.color)
                    
                    # Level up every 1000 points
                    if self.score % 1000 == 0:
                        self.level += 1
                    break
        
        # Enemies vs player
        for enemy in self.enemies[:]:
            if enemy.get_rect().colliderect(self.player.get_rect()):
                self.enemies.remove(enemy)
                self.player.health -= 25
                self.create_explosion(self.player.x, self.player.y, RED)
                if self.player.health <= 0:
                    self.game_over = True
    
    def draw_hud(self):
        # Modern HUD panel
        hud_height = 80
        
        # Top HUD background with gradient effect
        for i in range(hud_height):
            alpha = int(100 * (1 - i / hud_height))
            color = (*DARK_BG, alpha)
            pygame.draw.line(self.screen, DARK_BG, (0, i), (SCREEN_WIDTH, i))
        
        # HUD border
        pygame.draw.line(self.screen, NEON_CYAN, (0, hud_height), (SCREEN_WIDTH, hud_height), 2)
        
        # Score display with icon
        score_text = self.font.render(f"💰 SCORE: {self.score:,}", True, GOLD)
        self.screen.blit(score_text, (30, 20))
        
        # Level display
        level_text = self.font.render(f"⚡ LEVEL: {self.level}", True, NEON_GREEN)
        self.screen.blit(level_text, (300, 20))
        
        # Health bar (modern design)
        health_x, health_y = 30, 50
        health_width, health_height = 250, 15
        health_ratio = max(0, self.player.health / self.player.max_health)
        
        # Health bar background
        pygame.draw.rect(self.screen, (40, 40, 40), (health_x, health_y, health_width, health_height))
        
        # Health bar fill with color coding
        if health_ratio > 0.6:
            health_color = NEON_GREEN
        elif health_ratio > 0.3:
            health_color = ORANGE
        else:
            health_color = RED
        
        pygame.draw.rect(self.screen, health_color, (health_x, health_y, health_width * health_ratio, health_height))
        
        # Health bar border
        pygame.draw.rect(self.screen, WHITE, (health_x, health_y, health_width, health_height), 2)
        
        # Health text
        health_text = self.font.render(f"❤️ HEALTH: {max(0, self.player.health)}%", True, WHITE)
        self.screen.blit(health_text, (health_x + health_width + 20, health_y - 5))
        
        # Enemy counter
        enemy_text = self.font.render(f"🎯 ENEMIES: {len(self.enemies)}", True, NEON_PINK)
        self.screen.blit(enemy_text, (SCREEN_WIDTH - 200, 20))
    
    def draw_game_over(self):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(DARK_BG)
        self.screen.blit(overlay, (0, 0))
        
        # Game over panel
        panel_width, panel_height = 600, 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Panel background
        pygame.draw.rect(self.screen, DARK_BG, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, NEON_CYAN, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Game over title
        game_over_text = self.big_font.render("MISSION FAILED", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, panel_y + 80))
        self.screen.blit(game_over_text, text_rect)
        
        # Stats
        stats = [
            f"Final Score: {self.score:,}",
            f"Level Reached: {self.level}",
            f"Enemies Defeated: {self.score // 100}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, GOLD)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, panel_y + 150 + i * 40))
            self.screen.blit(text, text_rect)
        
        # Instructions
        restart_text = self.font.render("Press R to Restart Mission", True, NEON_GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, panel_y + 300))
        self.screen.blit(restart_text, restart_rect)
        
        quit_text = self.font.render("Press Q to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, panel_y + 340))
        self.screen.blit(quit_text, quit_rect)
    
    def reset_game(self):
        self.player = Player(100, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.particles = []
        self.score = 0
        self.level = 1
        self.enemy_spawn_timer = 0
        self.game_over = False
        self.game_started = True
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.game_started:
                        if event.key == pygame.K_UP:
                            self.menu_selection = (self.menu_selection - 1) % 2
                        elif event.key == pygame.K_DOWN:
                            self.menu_selection = (self.menu_selection + 1) % 2
                        elif event.key == pygame.K_RETURN:
                            if self.menu_selection == 0:
                                self.reset_game()
                            else:
                                self.running = False
                    elif self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            self.running = False
            
            if not self.game_started:
                self.draw_menu()
            else:
                # Game background
                self.screen.fill(DARK_BG)
                
                # Moving stars
                for star in self.stars:
                    star.update()
                    star.draw(self.screen)
                
                if not self.game_over:
                    # Update game objects
                    self.player.update()
                    
                    # Spawn enemies (increases with level)
                    spawn_rate = max(30, 90 - self.level * 5)
                    self.enemy_spawn_timer += 1
                    if self.enemy_spawn_timer > spawn_rate:
                        self.spawn_enemy()
                        self.enemy_spawn_timer = 0
                    
                    # Update enemies
                    for enemy in self.enemies[:]:
                        enemy.update()
                        if enemy.x < -enemy.width:
                            self.enemies.remove(enemy)
                    
                    # Update particles
                    for particle in self.particles[:]:
                        particle.update()
                        if particle.life <= 0:
                            self.particles.remove(particle)
                    
                    # Handle collisions
                    self.handle_collisions()
                    
                    # Draw game objects
                    self.player.draw(self.screen)
                    for enemy in self.enemies:
                        enemy.draw(self.screen)
                    for particle in self.particles:
                        particle.draw(self.screen)
                    
                    # Draw HUD
                    self.draw_hud()
                else:
                    self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()