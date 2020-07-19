import pygame
from os import path
import player_module
import mob, boss, boss_2, boss_3, boss_minion
import bullet, mob_bullet, powerup, explosions
import menu, animations, cars, purgatory
import text, math, random, constants
import mob_01_left, mob_01_right, mob_02_left, mob_02_right
import mob_03_left,mob_03_right,mob_04_left, mob_04_right
import tank, helicopter, summary, laser, civilian

# Level 1 Background Art from Kenny.nl game asset store
# Level 2 Background Art from Adam Saltsman --> Check out his work: https://adamatomic.itch.io/
# Level 3 Background Art from Mariusz Szulc --> Follow him on Behance: https://www.behance.net/MariuszSzulc
# Boss art from MillionthVector --> his blog: http://millionthvector.blogspot.de
# Action Chiptunes by Juhani Junkala
# Additional resources: www.bfxr.net | opengameart.org
# Portal art animations by Green Grape --> https://green-grape.itch.io/pixelportal
# Enemy jet sprites and player sprite drawn by Mark Simpson, aka Prinz Eugn --> https://www.gamedev.net/forums/topic/495808-free-airplane-sprite-pack/
# Tank sprite --> 2D Game Art for free: http://2dgameartforfree.blogspot.com/
# Helicopter sprite drawn by King Tyranno --> https://www.deviantart.com/king-tyranno/art/Attack-Helicopter-Desert-Camo-471229655
# All other sprites and images drawn by me.

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption('BombsAway2!')
clock = pygame.time.Clock()

# Parent level class. Sharing level characteristics are initiated here
class Level():
    def __init__(self, player):
        self.player_img = pygame.image.load('sprites/fighterJet1.png').convert()
        self.player = player
        self.score = 0
        self.tanks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.mob_bullets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.missile_group = pygame.sprite.Group()
        self.ammo_powerups = pygame.sprite.Group()
        self.bomb_powerups = pygame.sprite.Group()
        self.speed_powerups = pygame.sprite.Group()
        self.gun_powerups = pygame.sprite.Group()
        self.Start_text = pygame.sprite.Group()
        self.boss_sprite = pygame.sprite.Group()
        self.helicopters = pygame.sprite.Group()
        self.laser_group = pygame.sprite.Group()
        self.civ_group = pygame.sprite.Group()
        self.running = True
        self.highscore = 0
        self.highscore_list = []
        self.load_data()

        # Controls number of regular mob waves:
        self.max_mob_spawns = 6
        self.mob_draw_time = pygame.time.get_ticks()
        self.bombs = 1
        self.missiles = 1
        self.total_fighters_killed = 0
        self.charge = 0
        self.starting_pos = -7080
        self.spawn_powerups()
        self.total = None
        self.last_death = pygame.time.get_ticks()
        self.lives = 3
        self.bg_ticks = pygame.time.get_ticks()
        self.last_bomb = pygame.time.get_ticks()
        self.last_bomb_anim = pygame.time.get_ticks()
        self.bomb_frame = 20
        self.spawned_a_boss = 0
        self.mob_01_left_ticks = pygame.time.get_ticks()
        self.mob_01_right_ticks = pygame.time.get_ticks()
        self.mob_02_left_ticks = pygame.time.get_ticks()
        self.mob_02_right_ticks = pygame.time.get_ticks()
        self.mob_03_left_ticks = pygame.time.get_ticks()
        self.mob_03_right_ticks = pygame.time.get_ticks()
        self.mob_04_left_ticks = pygame.time.get_ticks()
        self.mob_04_right_ticks = pygame.time.get_ticks()
        self.mob_01_delay = pygame.time.get_ticks()
        self.mob_02_delay = pygame.time.get_ticks()
        self.laser_charge_time = pygame.time.get_ticks()
        # Level Summary tracking information:
        self.number_of_spawns = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
        self.total_fighters_killed = 0
        self.total_fighters = 0
        self.total_helicopters_killed = 0
        self.total_helicopters = 0
        self.total_tanks_killed = 0
        self.total_tanks = 0
        self.got_a_tank = 0
        self.new_player = 0
        self.player_input = 0
        self.number_of_tank_hits = 0
        self.tank_life = 10
        self.got_a_heli = 0
        self.number_of_heli_hits = 0
        self.heli_life = 20
        self.mob_v2_time = pygame.time.get_ticks()
        self.charge = 0
        self.civ_count = 0
        self.laser_start_pos = self.starting_pos
        self.laser_time = pygame.time.get_ticks()
        self.blink_delay = pygame.time.get_ticks()
        self.meter_emptying = pygame.time.get_ticks()
        self.laser_sound_mix = 0
        self.last_portal_anim = pygame.time.get_ticks()
        self.portal_frame = 0
        self.portal_activated = False

    def level_update(self):
        self.bullets.add(player.bullets)
        self.all_sprites.add(player.bullets)
        self.mob_bullets.add(mob.bullets_group)
        self.all_sprites.add(mob.bullets_group)
        self.laser_group.add(player.laser_sprite)
        self.mob_bullets.add(mob_01_left.bullets_group)
        self.all_sprites.add(mob_01_left.bullets_group)
        self.mob_bullets.add(mob_01_right.bullets_group)
        self.all_sprites.add(mob_01_right.bullets_group)
        self.all_sprites.update()
        self.laser_group.update()
        self.explosions()
        self.powerup_ammo()
        self.powerup_bomb()
        self.powerup_speed()
        self.powerup_gun()
        self.boss_damage()
        self.player_position()
        self.laser_kill()
        # If player presses [p] key, game will pause. Press again for unpause
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_p]:
            self.paused()

    def level_draw(self):
        self.tank_spawn()
        self.mob_draw()
        self.civ_alert()
        self.laser_meter()
        self.draw_hud()
        player_speed = player.speed_multiplier
        if player_speed == 1:
            text.draw_text(screen, str(player.numbers), 60, 770, 560, constants.BLUE, "ariel")
            screen.blit(powerup.speed_powerup_img, (688, 545))
        if self.bomb_frame < 20:
            self.bomb_animation()
        self.boss_spawn()
        self.all_sprites.draw(screen)
        self.laser_group.draw(screen)

    # load data from the highscore.txt file to get saved data
    def load_data(self):
        # finds current working directory
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, "highscore.txt"), 'r') as hs:
            for i in range(10):
                try:
                    highscore = int(hs.readline())

                except:
                    highscore = 0
                self.highscore_list.append(highscore)
                self.highscore = self.highscore_list[0]
                menu.highscore = self.highscore

    def explosions(self):
        self.exp1_sound = pygame.mixer.Sound('sounds/Explosion1.wav')
        self.exp1_sound.set_volume(0.3)
        self.exp2_sound = pygame.mixer.Sound('sounds/Explosion2.wav')
        self.exp2_sound.set_volume(0.3)
        mob_hits = pygame.sprite.groupcollide(self.mobs, self.bullets, \
        True, True, pygame.sprite.collide_circle)
        for every in mob_hits:
            self.total_fighters_killed += 1
            self.charge += 3
            if self.charge > 162:
                self.charge = 163
            self.score += 5000
            expl = explosions.Explosion(every.rect.center, 'sm')
            self.all_sprites.add(expl)
            explode = random.randrange(2)
            if explode == 1:
                self.exp1_sound.play()
            else:
                self.exp2_sound.play()

    def powerup_ammo(self):
        powerup_sound = pygame.mixer.Sound('sounds/ammo_powerup2.wav')
        powerup_sound.set_volume(0.3)
        hits = pygame.sprite.spritecollide(player, self.ammo_powerups,\
        True, pygame.sprite.collide_circle)
        for every in hits:
            player.ammo += 20
            powerup_sound.play()

    def powerup_bomb(self):
        powerup_sound = pygame.mixer.Sound('sounds/ammo_powerup1.wav')
        powerup_sound.set_volume(0.3)
        hits = pygame.sprite.spritecollide(player, self.bomb_powerups,\
        True, pygame.sprite.collide_circle)
        for every in hits:
            self.bombs += 1
            powerup_sound.play()

    def powerup_speed(self):
        powerup_sound = pygame.mixer.Sound('sounds/ammo_powerup1.wav')
        powerup_sound.set_volume(0.3)
        hits = pygame.sprite.spritecollide(player, self.speed_powerups,\
        True, pygame.sprite.collide_circle)
        for every in hits:
            player.speed_multiplier += 1
            self.afterburners = "ACTIVE  FUEL LEFT:"
            powerup_sound.play()

    def powerup_gun(self):
        powerup_sound = pygame.mixer.Sound('sounds/ammo_powerup1.wav')
        powerup_sound.set_volume(0.3)
        hits = pygame.sprite.spritecollide(player, self.gun_powerups, \
        True, pygame.sprite.collide_circle)
        for every in hits:
            player.upgrade += 1
            powerup_sound.play()

    def mob_spawn_01_left(self):
        now = pygame.time.get_ticks()
        if now - self.mob_01_left_ticks > 750 and self.number_of_spawns[0] < 7:
            self.mob = mob_01_left.Mob_01_left(-30, 400, (300, 4, 2000))
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_01_left_ticks = now
            self.number_of_spawns[0] += 1

    def mob_spawn_01_right(self):
        # right_now = pygame.time.get_ticks()
        # if right_now - self.mob_01_delay > 750:
        now = pygame.time.get_ticks()
        if now - self.mob_01_right_ticks > 750 and self.number_of_spawns[1] < 7:
            self.mob = mob_01_right.Mob_01_right(830, 400, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_01_right_ticks = now
            self.number_of_spawns[1] += 1

    def mob_spawn_02_left(self):
            now = pygame.time.get_ticks()
            if now - self.mob_02_left_ticks > 750 and self.number_of_spawns[2] < 7:
                self.mob = mob_02_left.Mob_02_left(-30, 510, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
                self.all_sprites.add(self.mob)
                self.mobs.add(self.mob)
                self.mob_02_left_ticks = now
                self.number_of_spawns[2] += 1

    def mob_spawn_02_right(self):
        # right_now = pygame.time.get_ticks()
        # if right_now - self.mob_02_delay > 750:
        now = pygame.time.get_ticks()
        if now - self.mob_02_right_ticks > 750 and self.number_of_spawns[3] < 7:
            self.mob = mob_02_right.Mob_02_right(830, 510, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_02_right_ticks = now
            self.number_of_spawns[3] += 1

    def mob_spawn_03_left(self):
        now = pygame.time.get_ticks()
        if now - self.mob_03_left_ticks > 750 and self.number_of_spawns[4] < 7:
            self.mob = mob_03_left.Mob_03_left(-30, 500, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_03_left_ticks = now
            self.number_of_spawns[4] += 1

    def mob_spawn_03_right(self):
        now = pygame.time.get_ticks()
        if now - self.mob_03_right_ticks > 750 and self.number_of_spawns[5] < 7:
            self.mob = mob_03_right.Mob_03_right(830, 500, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_03_right_ticks = now
            self.number_of_spawns[5] += 1

    def mob_spawn_04_left(self):
        now = pygame.time.get_ticks()
        if now - self.mob_04_left_ticks > 750 and self.number_of_spawns[6] < 4:
            self.mob = mob_04_left.Mob_04_left(-30, 510, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_04_left_ticks = now
            self.number_of_spawns[6] += 1

    def mob_spawn_04_right(self):
        now = pygame.time.get_ticks()
        if now - self.mob_04_right_ticks > 750 and self.number_of_spawns[7] < 4:
            self.mob = mob_04_right.Mob_04_right(830, 510, (300, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
            self.mob_04_right_ticks = now
            self.number_of_spawns[7] += 1

    def shooting_mobs (self, mob_image, x, y, speedx, speedy, speed_mod, spawn_time):
        now = pygame.time.get_ticks()
        if now - self.mob_v2_time > spawn_time:
            # speed mods: 1-slow oscillations 2-fast oscillations 3-linear movement
            moby = mob.Mob(mob_image, x, y, speedx, speedy, speed_mod, (500, 4, 2000)) #(fire_rate, bullet_speed, delay)
            self.all_sprites.add(moby)
            self.mobs.add(moby)
            self.mob_v2_time = now
            summary.total_fighters += 1

    def civilian_spawn(self, x, y, speedx, speedy, rotate):
        civ_plane = civilian.Civilian_plane(x, y, speedx, speedy, rotate) #(x, y, speedx, speedy, rotate)
        self.all_sprites.add(civ_plane)
        self.civ_group.add(civ_plane)
        self.civ_count += 1
        self.civ_time = pygame.time.get_ticks() + 500

    def civ_alert(self):
        if len(self.civ_group.sprites()) > 0:
            right_now = pygame.time.get_ticks()
            if self.civ_time > right_now:
                text.draw_text(screen, '!!Civilians Alert!!', 40, 675, 10, constants.RED, "Haettenschweiler")
            else:
                if right_now - self.civ_time > 500:
                    self.civ_time += 1000

    def laser_kill(self):
        if len(current_level.laser_group.sprites()) > 0:
            mob_hits = pygame.sprite.groupcollide(self.mobs, self.laser_group, True, False)
            for every in mob_hits:
                if self.spawned_a_boss == 0:
                    self.total_fighters_killed += 1
                self.score += 5000
                expl = explosions.Explosion(every.rect.center, 'sm')
                self.all_sprites.add(expl)
                explode = random.randrange(2)
                if explode == 1:
                    self.exp1_sound.play()
                else:
                    self.exp2_sound.play()
            tank_hits = pygame.sprite.groupcollide(self.tanks, self.laser_group, False, False)
            for every in tank_hits:
                self.tank_life -= 0.05
                # expl = explosions.Explosion((every.rect.centerx, every.rect.bottom), 'sm')
                # self.all_sprites.add(expl)

            heli_hits = pygame.sprite.groupcollide(self.helicopters, self.laser_group, False, False)
            for every in heli_hits:
                # self.total_fighters_killed += 1
                # self.score += 5000
                self.heli_life -= 0.05
                # expl = explosions.Explosion(every.rect.center, 'sm')
                # self.all_sprites.add(expl)
                # explode = random.randrange(2)
                # if explode == 1:
                #     self.exp1_sound.play()
                # else:
                #     self.exp2_sound.play()
            mob_bullet_hits = pygame.sprite.groupcollide(self.mob_bullets, self.laser_group, True, False)

            if self.spawned_a_boss == 1:
                boss_hits = pygame.sprite.groupcollide(self.boss_sprite, self.laser_group, False, False)
                for every in boss_hits:
                    self.boss.life -= 0.25

    def laser_meter(self):
        self.laser_sound = pygame.mixer.Sound('sounds/laser_beam_1.wav')
        self.laser_sound.set_volume(1)
        right_now = pygame.time.get_ticks()
        if player.firing_laser == False:
            self.laser_time = right_now
        if player.laser_ready == True and player.firing_laser == True:
            if right_now - self.laser_time > 5000:
                player.laser_ready = False
                player.firing_laser = False
                self.charge = 0

        now = pygame.time.get_ticks()
        if now - self.laser_charge_time > 1000:
            self.charge += 2
            self.laser_charge_time = now
        if self.charge > 162:
            player.laser_ready = True
            self.charge = 163
        screen.blit(animations.laser_meter_images[round(self.charge)], (10, 455))
        # Laser-ready blinking code
        if self.charge < 163:
            self.blink_delay = pygame.time.get_ticks() + 1000
        if self.charge == 163:
            just_now = pygame.time.get_ticks()
            if self.blink_delay > just_now:
                text.draw_text(screen, 'LASER CHARGED', 20, 140, 522, constants.GREEN, "Haettenschweiler")
            else:
                if just_now - self.blink_delay > 1000:
                    self.blink_delay += 2000
        # Laser firing causes meter to empty
        if player.firing_laser == True:
            if self.laser_sound_mix == 0:
                self.laser_sound.play(loops = 0)
                self.laser_sound_mix += 1
            now = pygame.time.get_ticks()
            if now - self.meter_emptying > 50:
                self.charge -= 1.8
                self.meter_emptying = now
        if player.laser_not_ready == False:
            self.laser_not_ready = right_now + 2000
        if player.laser_not_ready == True:
            if self.laser_not_ready > right_now:
                text.draw_text(screen, 'LASER NOT CHARGED', 20, 140, 522, constants.RED, "Haettenschweiler")
            else:
                player.laser_not_ready = False

    def bombsaway(self):
        self.exp1_sound = pygame.mixer.Sound('sounds/Explosion1.wav')
        self.exp1_sound.set_volume(0.3)
        self.exp2_sound = pygame.mixer.Sound('sounds/Explosion2.wav')
        self.exp2_sound.set_volume(0.3)
        mobs = current_level.mobs.sprites()
        for every in mobs:
            every.kill()
            current_level.score += 1
            expl = explosions.Explosion(every.rect.center, 'sm')
            current_level.all_sprites.add(expl)
            explode = random.randrange(2)
            if explode == 1:
                self.exp1_sound.play()
            else:
                self.exp2_sound.play()

    def bomb_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_bomb_anim > 20:
            self.last_bomb_anim = now
            screen.blit(animations.bombsaway_anim[self.bomb_frame], \
            (player.rect.centerx-(self.bomb_frame+1)*50, player.rect.centery-(self.bomb_frame+1)*float(37.5)))
            self.bomb_frame += 1

    def bomb_update(self, multiplier):
        # Updates the bombs triggered by the player
        keystate = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        if now - self.last_bomb > 200:
            if keystate[pygame.K_b] and current_level.bombs > 0:
                self.bombsaway()
                self.last_bomb = now
                self.bomb_frame = 0
                current_level.bombs -= 1
                # Change this so that the boss will lose health when bomb is triggered
                if self.spawned_a_boss == 1:
                     self.boss.life -= 20*multiplier

    def boss_damage(self):
        if self.spawned_a_boss == 1:
            hits = pygame.sprite.spritecollide(self.boss, self.bullets, True)
            for every in hits:
                self.boss.life -= 1
            if self.boss.life < 1:
                self.boss.kill()

    def health_bar(self, multiplier):
        for i in range(10):
            if i*10*multiplier < self.boss.life <= (i+1)*10*multiplier:
                image = animations.boss_health_images[(i+1)]
                image.set_colorkey(constants.WHITE)
        if self.boss.life <= 0:
            image = animations.boss_health_images[0]
        text.draw_text(screen, 'HEALTH: ', 24, 100, 7, constants.BLACK, "ariel")
        screen.blit(image, (135, 5))

    def spawn_portal(self):
        if self.portal_frame > 7:
            self.portal_frame = 0
        now = pygame.time.get_ticks()
        if now - self.last_portal_anim > 20:
            self.last_portal_anim = now
            self.portal_frame += 1
        if ((self.boss.rect.y+146)-20 <= player.rect.bottom - 50 < (self.boss.rect.y+146)+20):
            if ((self.boss.rect.x)-20 <= player.rect.centerx - 75 < (self.boss.rect.x)+20):
                self.portal_activated = True

    def paused(self):
        text.draw_text(screen, "Paused", 200, 400, 120, constants.BLUE, "ariel")
        text.draw_text(screen, "Press [p] key to UNPAUSE", 50, 400, 250, constants.BLUE, "ariel")
        text.draw_text(screen, "Press [ESC] key to EXIT GAME", 50, 400, 300, constants.BLUE, "ariel")
        # button_sprites = pygame.sprite.Group()
        # images = ['sprites/enemyBlack1.png', 'sprites/enemyBlue1.png']
        # continue_button = button.Button(images, 300, 600)
        # button_sprites.add(continue_button)
        pause = True
        # The key press code for pause is in the player_module
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pause = False
                        self.player.pause = False
                    if event.key == pygame.K_ESCAPE:
                        Level.running = False
                        pause = False
                        self.player.pause = False
            pygame.display.update()
            clock.tick(15)

    def draw_hud(self):
        text.draw_text(screen, str(total_score + self.score), 50, constants.WIDTH/2 + 10 , 10, constants.SCORE_RED, "Haettenschweiler") #(surf, text, size, x, y, color, font name)
        # text.draw_text(screen, 'AMMO: ' + str(player.ammo), 30, constants.WIDTH - 70, constants.HEIGHT - 120, constants.BLACK, "Haettenschweiler")
        text.draw_text(screen, 'BOMBS: ' + str(self.bombs), 20, 140, 497, constants.RED, "Haettenschweiler")
        text.draw_text(screen, 'Time: ' + str(round(summary.time/1000)), 20, 140, 470, constants.RED, "Haettenschweiler")
        # text.draw_text(screen, 'MISSILES: ' + str(self.missiles), 30, constants.WIDTH - 70, constants.HEIGHT - 40, constants.BLACK, "Haettenschweiler")
        text.draw_text(screen, 'LIVES: ' + str(self.lives), 30, 50, 10, constants.GREEN, "Haettenschweiler")
        text.draw_text(screen, '25%', 20, 65, 555, constants.DARK_GREEN, "Haettenschweiler")
        text.draw_text(screen, '50%', 20, 115, 555, constants.DARK_GREEN, "Haettenschweiler")
        text.draw_text(screen, '75%', 20, 162, 555, constants.DARK_GREEN, "Haettenschweiler")
        text.draw_text(screen, '100%', 20, 212, 555, constants.DARK_GREEN, "Haettenschweiler")

    def tank(self, starting_pos_1, starting_pos_2, tank_1x, tank_1y, tank_2x, tank2y):
        # As of right now, only 1 tank can be on the screen at a time.
        if self.starting_pos > starting_pos_1:
            if self.got_a_tank == 0:
                self.tank_01 = tank.Tank(tank_1x, tank_1y)
                self.tank_01_body = tank.Tank_body(tank_1x, tank_1y)
                self.all_sprites.add(self.tank_01_body)
                self.tanks.add(self.tank_01_body)
                self.all_sprites.add(self.tank_01)
                self.tanks.add(self.tank_01)
                self.got_a_tank += 1
                self.tank_life = 5
            if self.got_a_tank == 1:
                self.mob_bullets.add(tank.bullets)
                self.all_sprites.add(tank.bullets)
                hits = pygame.sprite.groupcollide(self.tanks, self.bullets, False, True)
                for every in hits:
                    self.tank_life -= 1
                if self.tank_life < 0 and len(self.tanks) > 0:
                    self.charge +=  10
                    self.score += 25000
                    self.total_tanks_killed += 1
                    expl = explosions.Explosion(self.tanks.sprites()[0].rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.tank_01.kill()
                    self.tank_01_body.kill()
                    self.tank_life -= 1

        if self.starting_pos > starting_pos_2:
            if self.got_a_tank == 1:
                self.tank_02 = tank.Tank(tank_2x, tank2y)
                self.tank_02_body = tank.Tank_body(tank_2x, tank2y)
                self.all_sprites.add(self.tank_02_body)
                self.tanks.add(self.tank_02_body)
                self.all_sprites.add(self.tank_02)
                self.tanks.add(self.tank_02)
                self.got_a_tank += 1
                self.tank_life = 5
            if self.got_a_tank == 2:
                self.mob_bullets.add(tank.bullets)
                self.all_sprites.add(tank.bullets)
                hits = pygame.sprite.groupcollide(self.tanks, self.bullets, False, True)
                for every in hits:
                    self.tank_life -= 1
                if self.tank_life < 0 and len(self.tanks) > 0:
                    self.charge += 10
                    self.score += 25000
                    self.total_tanks_killed += 1
                    expl = explosions.Explosion(self.tanks.sprites()[0].rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.tank_02.kill()
                    self.tank_02_body.kill()
                    self.tank_life -= 1

    def helicopter(self, starting_pos_1, starting_pos_2, x1, y1, speedx1, speedy1, x2, y2, speedx2, speedy2):
        if self.starting_pos > starting_pos_1:
            if self.got_a_heli == 0:
                heli_1 = helicopter.Helicopter(x1, y1, speedx1, speedy1)
                self.all_sprites.add(heli_1)
                self.helicopters.add(heli_1)
                self.got_a_heli += 1
                self.heli_life = 20
            if self.got_a_heli == 1:
                self.mob_bullets.add(helicopter.bullets)
                self.all_sprites.add(helicopter.bullets)
                hits = pygame.sprite.groupcollide(self.helicopters, self.bullets, False, True)
                for every in hits:
                    self.heli_life -= 1
                if self.heli_life < 0 and len(self.helicopters) > 0:
                    self.charge += 30
                    self.score += 100000
                    self.total_helicopters_killed += 1
                    expl = explosions.Explosion(self.helicopters.sprites()[0].rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.helicopters.sprites()[0].kill()

        if starting_pos_2 == None:
            pass
        elif self.starting_pos > starting_pos_2:
            if self.got_a_heli == 1:
                heli_2 = helicopter.Helicopter(x2, y2, speedx2, speedy2)
                self.all_sprites.add(heli_2)
                self.helicopters.add(heli_2)
                self.got_a_heli += 1
                self.heli_life = 20
            if self.got_a_heli == 2:
                self.mob_bullets.add(helicopter.bullets)
                self.all_sprites.add(helicopter.bullets)
                hits = pygame.sprite.groupcollide(self.helicopters, self.bullets, False, True)
                for every in hits:
                    self.heli_life -= 1
                if self.heli_life < 0 and len(self.helicopters) > 0:
                    self.charge += 30
                    self.score += 100000
                    self.total_helicopters_killed += 1
                    expl = explosions.Explosion(self.helicopters.sprites()[0].rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.helicopters.sprites()[0].kill()

    def general_level_summary(self):
        spawns = 0
        for i in range(8):
            spawns += current_level.number_of_spawns.get(i)
        self.total_fighters += spawns
        self.total_tanks += 2
        summary.total_fighters += self.total_fighters
        summary.total_fighters_killed += self.total_fighters_killed
        summary.total_tanks += self.total_tanks
        summary.total_tanks_killed += self.total_tanks_killed
        summary.total_helicopters += self.total_helicopters
        summary.total_helicopters_killed += self.total_helicopters_killed

    def general_new_level(self):
        self.player.kill()
        self.all_sprites.empty()
        self.mob_bullets.empty()
        self.bullets.empty()
        mob_01_left.bullets_group.empty()
        mob_01_right.bullets_group.empty()
        mob_02_left.bullets_group.empty()
        mob_02_right.bullets_group.empty()
        mob_03_left.bullets_group.empty()
        mob_03_right.bullets_group.empty()
        boss.bullets_group.empty()

# First level
class Level_01(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.background = pygame.image.load('backgrounds/rural_city_map16.png').convert()
        self.all_sprites.add(player)
        pygame.mixer.music.load('sounds/chiptunes_level_1.wav')
        pygame.mixer.music.set_volume(0.55)
        self.spawn_wave = 1
        ##############
        # Moving cars variables:
        self.cars_up_images = []
        self.cars_down_images = []
        self.cars_up_y = {}
        self.cars_down_y = {}
        self.cars_up_y[0] = [400, 600, 1000, 1500, 2000, 2500, 2800, 3400]
        self.cars_up_y[1] = [200, 500, 1200, 1400, 2200, 2400, 3000, 3800]
        self.cars_down_y[0] = [100, 400, 800, 1900, 2200, 3000, 3200, 3600]
        self.cars_down_y[1] = [750, 1000, 1350, 2400, 2600, 3200, 3550, 3800]
        self.cars_up_x = [337, 369]
        self.cars_down_x = [415, 447]
        self.car_up_images()
        self.car_down_images()

    def update(self):
        self.level_update()
        self.level_1_bomb_update()
        self.mob_bullets.add(boss.bullets_group)
        self.all_sprites.add(boss.bullets_group)
        self.down_cars_update()
        self.up_cars_update()

    def draw(self):
        self.draw_cars()
        # Draws the portal animation after defeating the boss
        self.draw_portal()
        if self.spawned_a_boss > 0 and self.boss.new_sequence > 0:
            self.level_1_health_bar()
        self.level_draw()

    def car_up_images(self):
        for i in range(8):
            self.carname = 'new_car{}'.format(i)
            self.carname = cars.Moving_cars_up()
            self.image = self.carname.image
            self.cars_up_images.append(self.image)

    def car_down_images(self):
        for i in range(8):
            self.carname = 'new_car{}'.format(i)
            self.carname = cars.Moving_cars_down()
            self.image = self.carname.image
            self.cars_down_images.append(self.image)

    def up_cars_update(self):
        for lst in self.cars_up_y:
            for car in range(len(self.cars_up_y[lst])):
                if self.total == 0:
                    self.cars_up_y[lst][car] -= 1
                    if self.cars_up_y[lst][car] < -30:
                        self.cars_up_y[lst][car] += 3840
                else:
                    self.cars_up_y[lst][car] += 1
                    if self.cars_up_y[lst][car] > 3840:
                        self.cars_up_y[lst][car] -= 3870

    def down_cars_update(self):
        for lst in self.cars_down_y:
            for car in range(len(self.cars_down_y[lst])):
                if self.total == 0:
                    self.cars_down_y[lst][car] += 1
                    if self.cars_down_y[lst][car] > 3840:
                        self.cars_down_y[lst][car] -= 3870
                else:
                    self.cars_down_y[lst][car] += 3
                    if self.cars_down_y[lst][car] > 3840:
                        self.cars_down_y[lst][car] -= 3870

    def draw_cars(self):
        for lst in range(len(self.cars_up_y)):
            for i in range(len(self.cars_up_y[lst])):
                screen.blit(current_level.cars_up_images[i], (self.cars_up_x[lst], self.cars_up_y[lst][i]))
        for lst in range(len(self.cars_down_y)):
            for i in range(len(self.cars_down_y[lst])):
                screen.blit(current_level.cars_down_images[i], (self.cars_down_x[lst], self.cars_down_y[lst][i]))

    def spawn_powerups(self):
        for i in range(1):
            new_power1 = powerup.Powerup(-2500, 1)
            self.all_sprites.add(new_power1)
            self.bomb_powerups.add(new_power1)
        for i in range(1):
            new_power2 = powerup.Powerup(-3500, 2)
            self.all_sprites.add(new_power2)
            self.speed_powerups.add(new_power2)
        for i in range(1):
            new_power3 = powerup.Powerup(-1500, 3)
            self.all_sprites.add(new_power3)
            self.gun_powerups.add(new_power3)

    def mob_draw(self):
        if self.starting_pos > -6000 and self.civ_count < 1:
            self.civilian_spawn(-30, 300, 2, 0, -90)
        if self.starting_pos > -6800:
            self.mob_spawn_02_right()
        if -5700 > self.starting_pos > -6000:
            self.shooting_mobs(0, -30, 100, 4, 1, 3, 1000)
        if self.starting_pos > -5200:
            self.mob_spawn_03_left()
        if self.starting_pos > -4500:
            self.mob_spawn_01_right()
        if -3200 > self.starting_pos > -3600:
            self.shooting_mobs(1, 830, 100, -3, 0, 2, 1000)
        if self.starting_pos > -3200:
            self.mob_spawn_01_left()
        if -2200 > self.starting_pos > -2400:
            self.shooting_mobs(0, -30, 100, 3, 0, 1, 750)
        if self.starting_pos > -1800:
            self.mob_spawn_02_right()

    def tank_spawn(self):
        self.tank(-4200, -1800, 300, -50, 600, -50)

    def level_1_bomb_update(self):
        self.bomb_update(1)

    def boss_spawn(self):
        if current_level.total == 0 and len(current_level.mobs) == 0 and self.spawned_a_boss == 0:
            self.boss = boss.Boss(322, -250, 0, 1)
            self.all_sprites.add(self.boss)
            self.boss_sprite.add(self.boss)
            self.spawned_a_boss = 1

    def level_1_health_bar(self):
        self.health_bar(1)

    def player_position(self):
        tank.player_position = [player.rect.centerx, player.rect.centery]
        helicopter.player_position = [player.rect.centerx, player.rect.centery]

    def draw_portal(self):
        if self.portal_activated == False and self.spawned_a_boss == 1:
            if len(self.boss_sprite) == 0:
                screen.blit(animations.portal_anim[current_level.portal_frame], (self.boss.rect.x, self.boss.rect.y + 146))

    def level_summary(self):
        self.general_level_summary()

    def new_level(self):
        self.general_new_level()
        purgatory.level_1_summary()

# Second level
class Level_02(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.all_sprites.add(player)
        # background tileset creations from https://twitter.com/gallet_city
        self.background = pygame.image.load('backgrounds/gallet_background.png').convert()
        self.background = pygame.transform.scale(self.background, (1200, 11520))
        pygame.mixer.music.load('sounds/chiptunes_level_2.wav')
        pygame.mixer.music.set_volume(0.55)

    def update(self):
        self.level_update()
        if player.upgrade == 0:
            player.upgrade += 1
        self.level_2_bomb_update()
        self.mob_bullets.add(boss_2.bullets)
        self.all_sprites.add(boss_2.bullets)

    def draw(self):
        self.heli_spawn()
        # Draws the portal animation after defeating the boss
        self.draw_portal()
        if self.spawned_a_boss > 0:
            self.level_2_health_bar()
        self.level_draw()

    def spawn_powerups(self):
        for i in range(1):
            new_power1 = powerup.Powerup(-1500, 1)
            self.all_sprites.add(new_power1)
            self.bomb_powerups.add(new_power1)
        for i in range(1):
            new_power2 = powerup.Powerup(-2500, 2)
            self.all_sprites.add(new_power2)
            self.speed_powerups.add(new_power2)
        for i in range(1):
            new_power3 = powerup.Powerup(-2000, 3)
            self.all_sprites.add(new_power3)
            self.gun_powerups.add(new_power3)

    def mob_draw(self):
        if self.starting_pos > -7000:
            self.mob_spawn_03_right()
        if -5700 > self.starting_pos > -6000:
            self.shooting_mobs(0, -30, 100, 4, 1, 3, 1000)
        if self.starting_pos > -5700 and self.civ_count < 1:
            self.civilian_spawn(700, -100, 0, 6, -180)
        if self.starting_pos > -5500:
            self.mob_spawn_01_right()
        if -3200 > self.starting_pos > -4000:
            self.shooting_mobs(1, 830, 100, -3, 0, 2, 1000)
        if self.starting_pos > 4400:
            self.mob_spawn_01_left()
        if self.starting_pos > -3200:
            self.mob_spawn_03_left()
        if -2200 > self.starting_pos > -2400:
            self.shooting_mobs(0, -30, 100, 2, 0, 1, 1000)
        if self.starting_pos > -2500:
            self.mob_spawn_02_right()
        if self.starting_pos > -2000 and self.civ_count < 2:
            self.civilian_spawn(830, 300, -2, 0, 90)
        if self.starting_pos > -1800:
            self.mob_spawn_03_right()
        if self.starting_pos > -1000:
            self.mob_spawn_04_left()
        if -1200 > self.starting_pos > -800:
            self.shooting_mobs(0, -30, 100, 2, 0, 1, 1000)

    def tank_spawn(self):
        self.tank(-3200, -1800, 300, -50, 700, -50)

    def heli_spawn(self):
        self.helicopter(-4500, None, -50, 100, 1, 0, None, None, None, None)

    def level_2_bomb_update(self):
        self.bomb_update(2)

    def boss_spawn(self):
        if current_level.total == 0 and len(current_level.mobs) == 0 and self.spawned_a_boss == 0:
            self.boss = boss_2.Boss_2()
            self.all_sprites.add(self.boss)
            self.boss_sprite.add(self.boss)
            self.spawned_a_boss = 1

    def level_2_health_bar(self):
        self.health_bar(2)

    def player_position(self):
        tank.player_position = [player.rect.centerx, player.rect.centery]
        helicopter.player_position = [player.rect.centerx, player.rect.centery]
        boss_2.player_position = [player.rect.centerx, player.rect.centery]

    def draw_portal(self):
        if self.portal_activated == False and self.spawned_a_boss == 1:
            if len(self.boss_sprite) == 0:
                screen.blit(animations.portal_anim[current_level.portal_frame], (self.boss.rect.x, self.boss.rect.y + 146))

    def level_summary(self):
        self.total_helicopters += 1
        self.general_level_summary()

    def new_level(self):
        self.general_new_level()
        purgatory.level_2_summary()

# Third level
class Level_03(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.all_sprites.add(player)
        # background tileset creations from https://twitter.com/gallet_city
        self.background = pygame.image.load('backgrounds/level_3_bg.jpg').convert()
        pygame.mixer.music.load('sounds/chiptunes_level_3.wav')
        pygame.mixer.music.set_volume(0.55)

    def update(self):
        self.level_update()
        self.mob_bullets.add(boss_3.bullets)
        self.all_sprites.add(boss_3.bullets)
        self.mobs.add(boss_3.minions)
        self.all_sprites.add(boss_3.minions)
        self.mob_bullets.add(boss_minion.bullets)
        self.all_sprites.add(boss_minion.bullets)
        self.level_3_bomb_update()
        if player.upgrade == 0:
            player.upgrade += 2

    def draw(self):
        self.heli_spawn()
        if self.spawned_a_boss > 0 and self.boss.new_sequence > 0:
            self.level_3_health_bar()
        self.level_draw()

    def spawn_powerups(self):
        for i in range(1):
            new_power1 = powerup.Powerup(-1500, 1)
            self.all_sprites.add(new_power1)
            self.bomb_powerups.add(new_power1)
        for i in range(1):
            new_power2 = powerup.Powerup(-2500, 2)
            self.all_sprites.add(new_power2)
            self.speed_powerups.add(new_power2)
        for i in range(1):
            new_power3 = powerup.Powerup(-2000, 3)
            self.all_sprites.add(new_power3)
            self.gun_powerups.add(new_power3)

    def mob_draw(self):
        if -6200 > self.starting_pos > -7000:
            self.shooting_mobs(0, -30, 200, 3, -1, 3, 1000)
        if self.starting_pos > -6000:
            self.mob_spawn_04_right()
        if -4700 > self.starting_pos > -5500:
            self.shooting_mobs(1, 830, 100, -3, 0, 2, 1000)
        if self.starting_pos > -4500:
            self.mob_spawn_01_left()
            self.mob_spawn_01_right()
        if -2500 > self.starting_pos > -4000:
            self.shooting_mobs(2, 830, 500, -2, 4, 2, 2500)
        if self.starting_pos > -3000:
            self.mob_spawn_04_left()
        if self.starting_pos > -2250:
            self.mob_spawn_02_left()
            self.mob_spawn_02_right()
        if -500 > self.starting_pos > -1500:
            self.shooting_mobs(0, -30, 100, -3, 0, 3, 1000)
            self.shooting_mobs(2, 830, 350, 4, 1, 2, 1500)

    def tank_spawn(self):
        self.tank(-3200, -1800, 400, -50, 500, -50)

    def heli_spawn(self):
        self.helicopter(-4000, -1500, -50, 100, 1, 0, 850, 100, -1, 0)

    def level_3_bomb_update(self):
        self.bomb_update(3)

    def boss_spawn(self):
        if current_level.total == 0 and len(current_level.mobs) == 0 and self.spawned_a_boss == 0:
            self.boss = boss_3.Boss_3()
            self.all_sprites.add(self.boss)
            self.boss_sprite.add(self.boss)
            self.spawned_a_boss = 1

    def level_3_health_bar(self):
        self.health_bar(3)

    def player_position(self):
        tank.player_position = [player.rect.centerx, player.rect.centery]
        helicopter.player_position = [player.rect.centerx, player.rect.centery]
        boss_3.player_position = [player.rect.centerx, player.rect.centery]

    def level_summary(self):
        self.total_helicopters += 2
        self.general_level_summary()

    def new_level(self):
        self.general_new_level()
        purgatory.level_3_summary()

####################################################################
# Below are the loops that run the game.

menu.menu_start()
menu_timer = pygame.time.get_ticks()
player = player_module.Player()
current_level = Level_01(player)
current_level_no = 1
total_score = 0
clock = pygame.time.Clock()
# game loop
#Variables used inside gameloop:
Level.running = True
#Starts background music, will loop.
pygame.mixer.music.play(loops = -1)

while Level.running:

    clock.tick(constants.FPS)
    summary.time = pygame.time.get_ticks() - menu_timer
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Level.running = False

    # This section controls player lives:
    if animations.first_death == 0 or animations.first_death == 2:
        bullet_hits = pygame.sprite.spritecollide(player, current_level.mob_bullets, True, pygame.sprite.collide_circle)
        for every in bullet_hits:
            # Makes sure the laser gets deleted when the player dies
            if len(current_level.laser_group.sprites()) > 0:
                player.laser_ready = False
                player.firing_laser = False
                current_level.charge = 0
            player.update()
            player.kill()
            expl = explosions.Explosion(every.rect.center, 'sm')
            current_level.all_sprites.add(expl)
            explode = random.randrange(2)
            if explode == 1:
                current_level.exp1_sound.play()
            else:
                current_level.exp2_sound.play()
            player = player_module.Player()
            current_level.all_sprites.add(player)
            animations.first_death += 1
            current_level.lives -= 1
            if current_level.lives < 1:
                # dead()
                if total_score > current_level.highscore_list[9]:
                    total_score += current_level.score
                    current_level.highscore_list[9] = total_score
                    current_level.highscore_list.sort(reverse = True)
                    with open(path.join(current_level.dir, "highscore.txt"), 'w') as hs:
                        for i in range(10):
                            hs.write(str(current_level.highscore_list[i]) + "\n")
                if total_score == 0:
                    total_score += current_level.score
                menu.total_score += total_score
                current_level.level_summary()
                menu.loser_loser()
                Level.running = False

        mob_01_hits = pygame.sprite.spritecollide(player, current_level.mobs, True, pygame.sprite.collide_circle)
        for every in mob_01_hits:
            # Makes sure the laser gets deleted when the player dies
            if len(current_level.laser_group.sprites()) > 0:
                player.laser_ready = False
                player.firing_laser = False
                current_level.charge = 0
            player.update()
            player.kill()
            expl = explosions.Explosion(every.rect.center, 'sm')
            current_level.all_sprites.add(expl)
            explode = random.randrange(2)
            if explode == 1:
                current_level.exp1_sound.play()
            else:
                current_level.exp2_sound.play()
            player = player_module.Player()
            current_level.all_sprites.add(player)
            animations.first_death += 1
            current_level.lives -= 1
            if current_level.lives < 1:
                # dead()
                if total_score > current_level.highscore_list[9]:
                    total_score += current_level.score
                    current_level.highscore_list[9] = total_score
                    current_level.highscore_list.sort(reverse = True)
                    with open(path.join(current_level.dir, "highscore.txt"), 'w') as hs:
                        for i in range(10):
                            hs.write(str(current_level.highscore_list[i]) + "\n")
                if total_score == 0:
                    total_score += current_level.score
                menu.total_score += total_score
                current_level.level_summary()
                menu.loser_loser()
                Level.running = False

    civilian_crash = pygame.sprite.spritecollide(player, current_level.civ_group, True, pygame.sprite.collide_circle)
    civilian_hits = pygame.sprite.groupcollide(current_level.civ_group, current_level.bullets, True, pygame.sprite.collide_circle)
    for every in civilian_crash:
        expl = explosions.Explosion(every.rect.center, 'sm')
        current_level.all_sprites.add(expl)
        explode = random.randrange(2)
        if explode == 1:
            current_level.exp1_sound.play()
        else:
            current_level.exp2_sound.play()
        total_score -= 100000
    for every in civilian_hits:
        expl = explosions.Explosion(every.rect.center, 'sm')
        current_level.all_sprites.add(expl)
        explode = random.randrange(2)
        if explode == 1:
            current_level.exp1_sound.play()
        else:
            current_level.exp2_sound.play()
        total_score -= 100000

    if current_level.spawned_a_boss == 1:
        if len(current_level.boss_sprite) == 0 and current_level_no == 3:
            current_level.level_summary()
            # You won the game!!
            if total_score > current_level.highscore_list[9]:
                total_score += current_level.score
                current_level.highscore_list[9] = total_score
                current_level.highscore_list.sort(reverse = True)
                with open(path.join(current_level.dir, "highscore.txt"), 'w') as hs:
                    for i in range(10):
                        hs.write(str(current_level.highscore_list[i]) + "\n")
            menu.total_score += total_score
            menu.winner_winner()
            Level.running = False

        if len(current_level.boss_sprite) == 0 and current_level_no == 2:
            current_level.spawn_portal()
            if current_level.portal_activated:
                current_level.level_summary()
                total_score += current_level.score
                current_level.new_level()
                current_level_no += 1
                player = player_module.Player()
                current_level = Level_03(player)
                current_level.all_sprites.add(current_level.player)
                pygame.mixer.music.play(loops = -1)

        if len(current_level.boss_sprite) == 0 and current_level_no == 1:
            current_level.spawn_portal()
            if current_level.portal_activated:
                current_level.level_summary()
                total_score += current_level.score
                current_level.new_level()
                current_level_no += 1
                player = player_module.Player()
                current_level = Level_02(player)
                current_level.all_sprites.add(current_level.player)
                pygame.mixer.music.play(loops = -1)

    current_level.update()
    current_level.starting_pos += 2
    current_level.total = current_level.starting_pos
    if current_level.total > current_level.starting_pos*-1:
        current_level.total = 0

    # Draw
    screen.fill(constants.BLACK)
    # Moving Background
    screen.blit(current_level.background, (0, current_level.total))
    current_level.draw()

    pygame.display.flip()

pygame.quit()
