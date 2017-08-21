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
    GREY = (250, 250, 250)

    FONT = pygame.font.SysFont('notosans', 30)
    INFO_LABEL = FONT.render('R - reset  Q - quit', 1, GREY)


class Wall():

    def __init__(self, name, *actors):
        self.name = name
        self.actors = []
        self.animations = []

        self.trigger = Rect((actors[0].x, 0),
                            (Const.WALL_W, Const.HEIGHT))
        self.triggered = False

        for actor in actors:
            self.actors.append(actor)


    def draw(self):
        for actor in self.actors:
            actor.draw()


    def animate(self, tween='linear', duration=1, on_finished=None, **targets):
        """Set animations for all actors in the group. All actors will
        have the same animation."""

        for actor in self.actors:
            anim = Animation(actor,
                             tween,
                             duration,
                             **targets)

            self.animations.append(anim)

        trigger_anim = Animation(self.trigger,
                                 tween,
                                 duration,
                                 on_finished=on_finished,
                                 **targets)

        self.animations.append(trigger_anim)


    def stop_animations(self):
        """Stop all animations."""

        for anim in self.animations:
            try:
                anim.stop()
            except ValueError:
                pass

        self.animations = []


    def collides(self, actor):
        """Return True if 'actor' collides with any actors in this
        group."""

        for a in self.actors:
            if a.colliderect(actor):
                return True
        return False


    def collides_trigger(self, actor):
        """Check collision with the trigger. Don't allow multiple
        collisions."""

        if self.trigger.colliderect(actor):
            self.triggered = True
            return True

        return False


    def reset_trigger(self):
        self.triggered = False


    def reset(self, x=Const.WIDTH):
        """Reset wall trigger and put it in the initial position at 'x'
        coordinate."""

        offset = randint(100, 300)
        gap = randint(210, 250)

        top_y = 0 - Const.WALL_H + offset
        bottom_y = top_y + Const.WALL_H + gap

        self.actors[0].topleft = (x, top_y)
        self.actors[1].topleft = (x, bottom_y)
        self.trigger.x = x

        self.reset_trigger()
        self.animate(duration=Const.WALL_DURATION,
                     x=0 - Const.WALL_W,
                     on_finished=self.reset)


class Game():

    @classmethod
    def start(cls):
        cls.counter = 0
        cls.triggered = False


        cls.background = Actor('background', topleft=(0, 0))
        cls.scroll = Actor('scroll', topleft=(0, 0))
        cls.scroll_2 = Actor('scroll', topleft=(Const.WIDTH, 0))
        cls.foreground = Actor('foreground', topleft=(0, 0))
        cls.foreground_2 = Actor('foreground', topleft=(Const.WIDTH, 0))


        def animate_bg(actor, duration):
            actor.topleft = (Const.WIDTH,0)
            Game.bg_anims.append(animate(actor,
                                 duration=duration,
                                 topleft=(-Const.WIDTH, 0),
                                 on_finished=lambda: animate_bg(actor, duration)))

        cls.bg_anims = [
            animate(cls.scroll,
                    duration=30,
                    topleft=(-Const.WIDTH, 0),
                    on_finished=lambda: animate_bg(cls.scroll, 60)),
            animate(cls.scroll_2,
                    duration=60,
                    topleft=(-Const.WIDTH, 0),
                    on_finished=lambda: animate_bg(cls.scroll_2, 60)),

            animate(cls.foreground,
                    duration=15,
                    topleft=(-Const.WIDTH, 0),
                    on_finished=lambda: animate_bg(cls.foreground, 30)),
            animate(cls.foreground_2,
                    duration=30,
                    topleft=(-Const.WIDTH,0),
                    on_finished=lambda: animate_bg(cls.foreground_2, 30)),
        ]



        alien = Alien('alien')
        alien.center = 200, Const.HEIGHT/2

        cls.alien = alien

        first_wall = Wall('first_wall',
                          Actor('top',
                                topleft=(Const.WIDTH,
                                         0 - Const.WALL_H + 100)),
                          Actor('bottom',
                                topleft=(Const.WIDTH,
                                         Const.HEIGHT - 250)))
        first_wall.animate(duration=Const.WALL_DURATION,
                           on_finished=first_wall.reset,
                           x=(0-Const.WALL_W))


        second_wall = Wall('second_wall',
                           Actor('top',
                                 topleft=(Const.WIDTH + Const.WIDTH/2,
                                          0 - Const.WALL_H + 100)),
                           Actor('bottom',
                                 topleft=(Const.WIDTH + Const.WIDTH/2,
                                          Const.HEIGHT - 250)))
        second_wall.animate(duration=Const.WALL_DURATION * 1.5,
                            on_finished=second_wall.reset,
                            x=(0-Const.WALL_W))

        cls.walls = [first_wall, second_wall]

        cls.trigger = Rect((Const.WIDTH, 0),
                           (Const.WALL_W, Const.HEIGHT))

        ground = Rect((0, Const.HEIGHT),
                      (Const.WIDTH, 100))
        cls.ground = ground


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

        for wall in Game.walls:
            wall.stop_animations()

        for anim in Game.bg_anims:
            try:
                anim.stop()
            except ValueError:
                pass


        death_anim = animate(self,
                             pos=(self.x, self.y-100),
                             duration=0.3,
                             tween='decelerate',
                             on_finished=animate_fall)


# Event handlers
def draw():
    """Handle all drawing. This function is executed on each tick (60
    times each second by default)."""

    Game.background.draw()
    Game.scroll.draw()
    Game.scroll_2.draw()
    Game.foreground.draw()
    Game.foreground_2.draw()
    Game.walls[0].draw()
    Game.walls[1].draw()
    Game.alien.draw()

    counter_text = Const.FONT.render(str(Game.counter), 1, Const.GREY)
    screen.blit(counter_text, (10,10))
    screen.blit(Const.INFO_LABEL, (Const.WIDTH - 260, Const.HEIGHT - 40))


def on_key_down(key):
    """Handle key down events."""
    jump_dist = 100

    alien = Game.alien
    if key == keys.SPACE and alien.alive:

        def finished():
            if not alien.alive:
                alien.image = 'alien_hurt'
            else:
                alien.image = 'alien'

        alien.image = 'alien_fly'
        Animation(alien,
                  pos=(alien.x, alien.y-jump_dist),
                  duration=0.3,
                  tween='decelerate',
                  on_finished=finished)

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

        if Game.ground.colliderect(alien):
            alien.kill()

        for wall in walls:
            if wall.collides(alien):
                alien.kill()
            if not wall.triggered and wall.collides_trigger(alien):
                Game.counter += 1


Game.start()
