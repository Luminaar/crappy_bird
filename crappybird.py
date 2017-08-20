import sys
import pygame
from pgzero.animation import Animation
from random import randint


class Const():
    GRAVITY = 4

    WIDTH = 800
    HEIGHT = 600

    WALL_W = 70
    WALL_H = 500

    WALL_DURATION = 5

    RED = (200, 0, 0)
    GREEN = (0, 200, 0)
    BLUE = (0, 0, 200)
    SKY = (90, 201, 252)

    FONT = pygame.font.SysFont('notosans', 30)
    INFO_LABEL = FONT.render('R - reset  Q - quit', 1, BLUE)



class Game():

    @classmethod
    def start(cls):
        cls.counter = 0
        cls.triggered = False


        cls.background = Actor('background')

        alien = Alien('alien')
        alien.center = 200, Const.HEIGHT/2

        cls.alien = alien

        walls = [Actor('top',
                       (Const.WIDTH - Const.WALL_W,
                        0 - Const.WALL_H + 100)),
                 Actor('bottom',
                       (Const.WIDTH - Const.WALL_W,
                        Const.HEIGHT - 250))]

        cls.walls = walls

        cls.trigger = Rect((Const.WIDTH, 0),
                           (Const.WALL_W, Const.HEIGHT))

        ground = Rect((0, Const.HEIGHT),
                      (Const.WIDTH, 100))
        cls.ground = ground

        cls.reset()


    @classmethod
    def reset(cls):
        walls = cls.walls
        trigger = cls.trigger

        offset = randint(100, 300)
        gap = randint(210, 250)

        top_x = walls[0].topleft[0]
        bottom_x = walls[1].topleft[0]

        top_y = 0 - Const.WALL_H + offset
        bottom_y = top_y + Const.WALL_H + gap

        walls[0].topleft = (top_x, top_y)
        walls[1].topleft = (bottom_x, bottom_y)

        cls.wall_animations = []
        cls.trigger_anim = None

        trigger.x = Const.WIDTH
        walls[0].x = Const.WIDTH
        walls[1].x = Const.WIDTH

        cls.triggered = False
        trigger_anim = Animation(trigger,
                                 duration=Const.WALL_DURATION,
                                 x=0 - Const.WALL_W,
                                 y=trigger.y)

        top_wall_anim = Animation(walls[0],
                                  duration=Const.WALL_DURATION,
                                  x=0 - Const.WALL_W,
                                  y=walls[0].y)

        bottom_wall_anim = Animation(walls[1],
                                     duration=Const.WALL_DURATION,
                                     x=0 - Const.WALL_W,
                                     y=walls[1].y,
                                     on_finished=Game.reset)

        cls.wall_animations.append(top_wall_anim)
        cls.wall_animations.append(bottom_wall_anim)
        cls.trigger_anim = trigger_anim


class Alien(Actor):

    def __init__(self, *args, **kwargs):

        self.alive = True
        super().__init__(*args, **kwargs)


    def kill(self):
        def animate_fall():
            animate(self,
                    pos=(self.x, Const.HEIGHT+100),
                    duration=0.5,
                    tween='accelerate')


        self.alive = False
        self.image = 'alien_hurt'

        for anim in Game.wall_animations:
            anim.stop()

        Game.trigger_anim.stop()

        death_anim = animate(self,
                             pos=(self.x, self.y-100),
                             duration=0.3,
                             tween='decelerate',
                             on_finished=animate_fall)


def collides(act, rects):
    """Check if actor 'act' collides with any of the 'rects'. Rects can
    be a sequence of rects or a single rect."""

    if isinstance(rects, Rect):
        if rects.colliderect(act):
            return True
    else:
        for rect in rects:
            if rect.colliderect(act):
                return True

    return False


# Event handlers
def draw():
    """Handle all drawing. This function is executed on each tick (60
    times each second by default)."""

    Game.background.draw()
    Game.walls[0].draw()
    Game.walls[1].draw()
    Game.alien.draw()

    counter_text = Const.FONT.render(str(Game.counter), 1, Const.BLUE)
    screen.blit(counter_text, (10,10))
    screen.blit(Const.INFO_LABEL, (Const.WIDTH - 260, Const.HEIGHT - 40))


def on_key_down(key):
    """Handle key down events."""
    jump_dist = 100

    alien = Game.alien
    if key == keys.SPACE and alien.alive:
        alien.image = 'alien_fly'
        Animation(alien,
                  pos=(alien.x, alien.y-jump_dist),
                  duration=0.3,
                  tween='decelerate',
                  on_finished=lambda: setattr(alien,
                                              'image',
                                              'alien'))

    elif key == keys.R:
        Game.start()

    elif key == keys.Q:
        sys.exit(0)


def update():
    """This function is executed on each tick (60 times each second by
    default)."""

    alien = Game.alien
    walls = Game.walls

    if alien.alive:
        alien.y += Const.GRAVITY

        if collides(alien, Game.trigger) and not Game.triggered:
            Game.counter += 1
            Game.triggered = True

        if collides(alien, Game.ground):
            alien.kill()

        if collides(alien, walls):
            alien.kill()


Game.start()
