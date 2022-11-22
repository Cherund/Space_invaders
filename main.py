import pygame
import sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser


class Game:

    def __init__(self):
        # Player
        self.speed = 5
        self.player = pygame.sprite.GroupSingle(Player((screen_width/2, screen_height-10), screen_width, self.speed))
        self.shape = obstacle.shape

        # health and score
        self.lives = 3
        self.live_surface = pygame.transform.rotozoom(pygame.image.load('graphics/player.png').convert_alpha(), 0, 0.7)
        self.live_x_start_pos = screen_width - (self.live_surface.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font('font/Pixeled.ttf', 15)


        # Obstacle
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=screen_width/15, y_start=480)

        # Alien
        self.aliens = pygame.sprite.Group()
        self.aliens_lasers = pygame.sprite.Group()
        self.alien_setup(6, 8)
        self.alien_direction = 1

        # Extra
        self.extra_alien = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(500, 1000)

        # Audio
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.1)
        music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.05)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.15)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, 'red', x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance=60, y_distance=50, x_offset=60, y_offset=60):
        for row in range(rows):
            for col in range(cols):
                x = col*x_distance + x_offset
                y = row*y_distance + y_offset
                if row == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)
                self.aliens.add(alien_sprite)

    def aliens_position_check(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.left <= 0:
                self.alien_direction = 1
                self.aliens_move_down()
            elif alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.aliens_move_down()

    def aliens_move_down(self, distance=1):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def aliens_shoot(self):
        if self.aliens:
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 5, screen_height)
            self.aliens_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra_alien.add(Extra(choice(['right', 'left']), screen_width))
            self.extra_spawn_time = randint(500, 1000)

    def collision_check(self):
        # player laser
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:

                # obstacle collision
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collision
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                # extra alien collision
                if pygame.sprite.spritecollide(laser, self.extra_alien, True):
                    self.score += 500
                    laser.kill()
                    self.explosion_sound.play()


        # alien lasers
        if self.aliens_lasers:
            for laser in self.aliens_lasers:

                # obstacle collision
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # player collision
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.explosion_sound.play()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)

                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + live * (self.live_surface.get_size()[0] + 10)
            screen.blit(self.live_surface, (x, 8))

    def display_score(self):
        score_surface = self.font.render(f'Score: {self.score}', False, 'white')
        score_rectangle = score_surface.get_rect(topleft=(10, -5))
        screen.blit(score_surface, score_rectangle)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You Won!', False, 'white')
            victory_rect = victory_surf.get_rect(center=(screen_width/2, screen_height/2))
            screen.blit(victory_surf, victory_rect)

    def run(self):
        self.player.update()
        self.extra_alien.update()
        self.aliens_lasers.update()

        self.aliens.update(self.alien_direction)
        self.aliens_position_check()
        self.extra_alien_timer()
        self.collision_check()

        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)

        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.aliens_lasers.draw(screen)
        self.extra_alien.draw(screen)

        self.display_lives()
        self.display_score()
        self.victory_message()


if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()

    ALIEN_LASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIEN_LASER, 1000)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIEN_LASER:
                game.aliens_shoot()

        screen.fill('black')
        game.run()

        pygame.display.flip()
        clock.tick(60)
