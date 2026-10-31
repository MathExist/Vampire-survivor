
from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        ground_sprites = [
            sprite for sprite in self
            if hasattr(sprite, 'ground')
        ]

        object_sprites = [
            sprite for sprite in self
            if not hasattr(sprite, 'ground')
        ]

        # Draw ground first
        for sprite in ground_sprites:
            self.display_surface.blit(
                sprite.image,
                sprite.rect.topleft + self.offset
            )

        # Draw objects in depth order
        for sprite in sorted(
            object_sprites,
            key=lambda sprite: sprite.rect.bottom
        ):
            self.display_surface.blit(
                sprite.image,
                sprite.rect.topleft + self.offset
            )
