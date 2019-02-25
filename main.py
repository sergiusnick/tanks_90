import pygame


RESPAWN_PERIOD, SPEED = 1000, 10
run, move_tank = True, False
time_of_last_shooting, fires = 0, []


pygame.init()
screen = pygame.display.set_mode((1000, 900))
screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])


pygame.mixer.init()
background_sound = pygame.mixer.Sound('sound/background_music.wav')
background_sound.set_volume(0.1)
background_sound.play(-1)


shoot_clock = pygame.time.Clock()
clock = pygame.time.Clock()
clock.tick()
pygame.display.flip()


class Player:
    def __init__(self, pos, img_n, go):
        self.img_n, self.resp_pos, self.x, self.y, self.go = img_n, pos, pos[0], pos[1], go
        self.time_of_last_death, self.time_of_last_shooting, self.alive = 0, 0, True
        self.player_image = pygame.image.load(self.img_n + self.go + '.png').convert_alpha()

        screen.blit(self.player_image, self.player_image.get_rect(center=(self.x, self.y)))
        self.paint()

    def move(self, nx, ny):
        if 880 >= self.x + nx >= 20 and 880 >= self.y + ny >= 20 and self.alive:
            self.x += nx
            self.y += ny
            self.paint()

    def paint(self):
        screen.blit(self.player_image, self.player_image.get_rect(center=(self.x, self.y)))

    def img(self, name):
        if self.alive:
            self.go = name.split('_')[-1][0:-4]
        self.player_image = pygame.image.load(name).convert_alpha()

    def fire(self):
        if self.alive:
            BULLET_SPEED = 15
            SHOOT_PERIOD = 600
            z = pygame.mixer.Sound('sound/shoot.wav')
            z.set_volume(0.1)
            z.play()
            if not pygame.time.get_ticks() - self.time_of_last_shooting >= SHOOT_PERIOD:
                return
            if self.go == 'up':
                nx, ny = 0, -BULLET_SPEED
            elif self.go == 'down':
                nx, ny = 0, BULLET_SPEED
            elif self.go == 'left':
                nx, ny = -BULLET_SPEED, 0
            elif self.go == 'right':
                nx, ny = BULLET_SPEED, 0

            ball = Bullet(self.x, self.y, nx, ny)
            fires.append(ball)
            self.time_of_last_shooting = pygame.time.get_ticks()


    def die(self):
        if self.alive:
            self.alive = False
            self.time_of_last_death = pygame.time.get_ticks()
            z = pygame.mixer.Sound('sound/hit.wav')
            z.set_volume(0.1)
            z.play()
            self.respawn()

    def respawn(self):
        time_from_death = pygame.time.get_ticks() - self.time_of_last_death
        if time_from_death >= RESPAWN_PERIOD:
            self.alive = True
            self.x, self.y = self.resp_pos
            self.img(self.img_n + self.go + '.png')
            return
        # set frame
        frame_num = time_from_death // (RESPAWN_PERIOD // 7)
        if frame_num == 0:
            frame_num = 1
        self.img('img/bang/kill' + str(frame_num) + '.png')


class Bullet:
    def __init__(self, x, y, nx, ny):
        OFFSET = -3  # aligns bullet
        self.flew = False
        self.x, self.y, self.nx, self.ny = x + OFFSET, y + OFFSET, nx, ny
        self.fire_image = pygame.image.load('img/bullet.png').convert_alpha()

    def growth(self):
        self.x += self.nx
        self.y += self.ny
        if 900 >= self.x >= 0 and 900 >= self.y >= 0:
            screen.blit(self.fire_image, [self.x, self.y])
        else:
            self.clear()

    def clear(self):
        fires.pop(0)


player_f = Player((450, 250), 'img/first_', 'down')
player_s = Player((450, 450), 'img/second_', 'up')
pygame.time.set_timer(1, 500)
while run:
    screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                player_f.fire()

            if event.key == pygame.K_QUOTE:
                player_s.fire()

        elif event.type == 2:
            pygame.time.set_timer(1, 0)
            pygame.time.set_timer(2, 1000)

    for fire in fires:
        fire.growth()

        # check kills
        size_x, size_y = player_s.player_image.get_size()
        killed_enemy = player_s.x - size_x // 2 <= fire.x \
                       <= player_s.x + size_x // 2 and \
                       player_s.y - size_y // 2 <= fire.y <= player_s.y + size_y // 2

        size_x, size_y = player_f.player_image.get_size()
        killed_player = player_f.x - size_x // 2 <= fire.x \
                        <= player_f.x + size_x // 2 and \
                        player_f.y - size_y // 2 <= fire.y <= player_f.y + size_y // 2

        # check: did the fire flew from tank
        if not fire.flew and (killed_player or killed_enemy):
            continue
        else:
            fire.flew = True

        if killed_enemy:
            index = fires.index(fire)
            fires.pop(index)
            player_s.die()
        if killed_player:
            index = fires.index(fire)
            fires.pop(index)
            player_f.die()


    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_s.img('img/second_left.png')
        player_s.move(-SPEED, 0)

    elif keys[pygame.K_RIGHT]:
        player_s.img('img/second_right.png')
        player_s.move(SPEED, 0)

    elif keys[pygame.K_UP]:
        player_s.img('img/second_up.png')
        player_s.move(0, -SPEED)

    elif keys[pygame.K_DOWN]:
        player_s.img('img/second_down.png')
        player_s.move(0, SPEED)

    if keys[pygame.K_a]:
        player_f.img('img/first_left.png')
        player_f.move(-SPEED, 0)

    elif keys[pygame.K_d]:
        player_f.img('img/first_right.png')
        player_f.move(SPEED, 0)

    elif keys[pygame.K_w]:
        player_f.img('img/first_up.png')
        player_f.move(0, -SPEED)

    elif keys[pygame.K_s]:
        player_f.img('img/first_down.png')
        player_f.move(0, SPEED)


    if not player_s.alive:
        player_s.respawn()
    if not player_f.alive:
        player_f.respawn()

    player_f.paint()
    player_s.paint()
    pygame.display.flip()


pygame.quit()
