from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pygame.display.set_caption('Vampire Survivor')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # player health
        self.max_health = 100
        self.health = 100
        self.damage_per_hit = 15

        # invincibility timer
        self.invincibility_duration = 800
        self.last_damage_time = -800

        # health bar
        font_path = join("..", "fonts", "RoamersScreamDemoRegular-BLDR5.ttf")
        self.health_font = pygame.font.Font(font_path, 30)

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 50

        # audio
        self.shoot_sound = pygame.mixer.Sound(
            join("..", "audio", "shoot.wav")
        )
        self.shoot_sound.set_volume(0.4)

        self.impact_sound = pygame.mixer.Sound(
            join("..", "audio", "impact.ogg")
        )

        self.music = pygame.mixer.Sound(
            join("..", "audio", "music.wav")
        )
        self.music.play(loops=-1)

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(
            join('..', 'images', 'gun', 'bullet.png')
        ).convert_alpha()

        folders = list(
            walk(join("..", "images", "enemies"))
        )[0][1]

        self.enemy_frames = {}

        for folder in folders:
            for folder_path, _, file_names in walk(
                join("..", "images", "enemies", folder)
            ):
                self.enemy_frames[folder] = []

                for file_name in sorted(
                    file_names,
                    key=lambda name: int(name.split('.')[0])
                ):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and self.can_shoot:
            self.shoot_sound.play()

            pos = (
                self.gun.rect.center
                + self.gun.player_direction * 50
            )

            Bullet(
                self.bullet_surf,
                pos,
                self.gun.player_direction,
                (self.all_sprites, self.bullet_sprites)
            )

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                hit_enemies = pygame.sprite.spritecollide(
                    bullet,
                    self.enemy_sprites,
                    False,
                    pygame.sprite.collide_mask
                )

                if hit_enemies:
                    self.impact_sound.play()

                    for enemy in hit_enemies:
                        if enemy.death_time == 0:
                            enemy.destory()

                    bullet.kill()

    def player_collision(self):
        current_time = pygame.time.get_ticks()

        # Check invincibility
        if current_time - self.last_damage_time < self.invincibility_duration:
            return

        # Find enemies touching the player
        hit_enemies = pygame.sprite.spritecollide(
            self.player,
            self.enemy_sprites,
            False,
            pygame.sprite.collide_mask
        )

        # Only count living enemies
        hit_enemies = [
            enemy for enemy in hit_enemies
            if enemy.death_time == 0
        ]

        if hit_enemies:
            self.health -= self.damage_per_hit
            self.health = max(0, self.health)

            self.last_damage_time = current_time

            print("Player health:", self.health)

            if self.health <= 0:
                self.running = False

    def draw_health_bar(self):
        x = 25
        y = 25
        width = 260
        height = 28

        # Background
        pygame.draw.rect(
            self.display_surface,
            (45, 45, 45),
            (x, y, width, height),
            border_radius=6
        )

        # Determine health color
        health_percent = self.health / self.max_health

        if health_percent > 0.6:
            health_color = (50, 220, 80)
        elif health_percent > 0.3:
            health_color = (255, 200, 40)
        else:
            health_color = (230, 45, 45)

        # Actual health
        health_width = int(width * health_percent)

        if health_width > 0:
            pygame.draw.rect(
                self.display_surface,
                health_color,
                (x, y, health_width, height),
                border_radius=6
            )

        # Border
        pygame.draw.rect(
            self.display_surface,
            (255, 255, 255),
            (x, y, width, height),
            2,
            border_radius=6
        )

        # Health text
        health_text = self.health_font.render(
            f"HP: {self.health}/{self.max_health}",
            True,
            (255, 255, 255)
        )

        self.display_surface.blit(
            health_text,
            (x, y + height + 8)
        )

        # Invincibility indicator
        current_time = pygame.time.get_ticks()

        if current_time - self.last_damage_time < self.invincibility_duration:
            inv_text = self.health_font.render(
                "INVINCIBLE!",
                True,
                (255, 220, 80)
            )

            self.display_surface.blit(
                inv_text,
                (x + width + 20, y)
            )

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()

            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        game_map = load_pygame(
            join("..", "data", "maps", "world2.tmx")
        )

        for x, y, image in game_map.get_layer_by_name('Ground').tiles():
            Sprite(
                (x * TILE_SIZE, y * TILE_SIZE),
                image,
                self.all_sprites
            )

        for obj in game_map.get_layer_by_name('Objects'):
            CollisionSprite(
                (obj.x, obj.y),
                obj.image,
                (self.all_sprites, self.collision_sprites)
            )

        for obj in game_map.get_layer_by_name('Collisions'):
            CollisionSprite(
                (obj.x, obj.y),
                pygame.Surface((obj.width, obj.height)),
                self.collision_sprites
            )

        for obj in game_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites
                )

                self.gun = Gun(self.player, self.all_sprites)

            else:
                self.spawn_positions.append((obj.x, obj.y))

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick(60) / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.enemy_event:
                    Enemy(
                        choice(self.spawn_positions),
                        choice(list(self.enemy_frames.values())),
                        (self.all_sprites, self.enemy_sprites),
                        self.player,
                        self.collision_sprites
                    )

            # update
            self.gun_timer()
            self.input()

            self.all_sprites.update(dt)

            self.bullet_collision()
            self.player_collision()

            # draw
            self.display_surface.fill('black')

            self.all_sprites.draw(self.player.rect.center)

            # Draw health bar AFTER world rendering
            self.draw_health_bar()

            pygame.display.update()

        pygame.quit()
if __name__ == '__main__':
    game = Game()
    game.run()
