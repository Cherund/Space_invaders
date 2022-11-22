import pygame
from laser import Laser


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, constraint, speed):
        super().__init__()
        self.image = pygame.image.load('graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = speed
        self.max_x_constraint = constraint
        self.laser_ready = True
        self.laser_time = 0
        self.laser_cooldown = 500
        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.05)

        self.lasers = pygame.sprite.Group()

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and self.rect.right < self.max_x_constraint:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE]:
            if self.laser_ready:
                self.shoot()
                self.laser_ready = False
                self.laser_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.laser_time >= self.laser_cooldown:
                self.laser_ready = True

    def shoot(self):
        self.lasers.add(Laser(self.rect.center, -self.speed, self.rect.bottom))
        self.laser_sound.play()

    def update(self):
        self.get_input()
        self.lasers.update()
