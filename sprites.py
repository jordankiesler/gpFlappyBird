import enum
import math
import pygame as pg

import settings as st


# Base sprite class
class MovableSprite(pg.sprite.Sprite):
    def __init__(self, *groups):
        """
        Constructor method
        :param groups: sprite groups
        """
        super().__init__(*groups)
        self.rect = None

    def moveto(self, x=0, y=0):
        """
        Move a sprite to a given place
        in the simulation
        :param x: x-location of sprite
        :param y: y-location of sprite
        :return:
        """
        self.rect.x = x
        self.rect.y = y

    def moveBy(self, dy=0, dx=0):
        """
        Move sprite by a delta x and delta y
        value from where it currently is
        :param dy: Amount of y to move in
        :param dx: Amount of x to move in
        :return:
        """
        self.rect.move_ip(dx, dy)


# Base plane (drone) class
class Plane(MovableSprite):
    def __init__(self, game, image: pg.Surface, x, y):
        """
        Constructor method
        :param game: Actual simulation
        :param image: Picture of sprite
        :param x: x location of sprite
        :param y: y location of sprite
        """
        self._layer = 3                 # required for pygame.sprite.LayeredUpdates: set before adding it to the group
        super().__init__(game.allSprites, game.planes)
        self.game = game
        self.image = image
        self.originImage = self.image               # Used for rotating the plane
        self.rect = image.get_rect(x=x, y=y)        # Rectangle defining the sprite's space
        self.yVelocity = 0                          # y-velocity of sprite (i.e. left and right movement)
        self.distanceScore = 0
        self.targetScore = 0
        self.totalScore = self.distanceScore + (st.WEIGHT_TARGETS * self.targetScore)
        self.angle = 0

    def update(self, *args):
        """
        Updates sprite after every frame (CGP-directed moves, death, etc.)
        :param args: Arbitrary list of arguments
        :return: none
        """
        # Die if plane flies outside the screen
        if self.rect.top > st.SCREEN_HEIGHT or self.rect.bottom < 0:
            st.allPlanes[-1].append(self.totalScore)
            self.kill()
            return

        # Die if plane hits a radar
        if pg.sprite.spritecollideany(self, self.game.radars):
            # If the plane makes a distance score over 1000, more heavily weight it to select from those parents
            # This only works for the base population of 30 with a MU of 7, otherwise weights are constant
            if st.MU_WEIGHTS is not None and self.distanceScore > 1000:
                if len(st.MU_WEIGHTS) == 7:
                    st.MU_WEIGHTS = [10, 20, 30, 55, 80, 90, 100]
            st.allPlanes[-1].append(self.totalScore)
            self.kill()
            return

        # Assumed that if the plane can make it that far, it can traverse the radar infinitely, so kill and restart
        # If the plane makes it all the way, even more heavily weight it to choose from the distance parents
        if self.distanceScore >= st.PLANE_MAX_DISTANCE_ALLOWED:
            if st.MU_WEIGHTS is not None and len(st.MU_WEIGHTS) == 7:
                st.MU_WEIGHTS = [7, 14, 21, 45, 69, 93, 100]
            st.allPlanes[-1].append(self.totalScore)
            st.all4ks[-1].append([self.totalScore, self.targetScore])
            self.kill()
            return
        self.yVelocity = self.yVelocity     # Update velocity, if need be
        self.rect.y += self.yVelocity       # Update location based on yVelocity

        # Rotate the drone according to direction it's flying
        angle = 40 - (self.yVelocity + 4) / 8 * 80
        self.angle = min(30, max(angle, -30))
        self.image = pg.transform.rotate(self.originImage, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.totalScore = self.distanceScore + (st.WEIGHT_TARGETS * self.targetScore)

    # Turn plane left by setting y-speed as appropriate
    def turnLeft(self):
        self.yVelocity = st.PLANE_Y_SPEED

    # Turn plane right by setting y-speed as appropriate
    def turnRight(self):
        self.yVelocity = -st.PLANE_Y_SPEED

    # Make plane go straight by setting a 0 y velocity
    def goStraight(self):
        self.yVelocity = 0

    # Shoot a bullet - generates a bullet object that automatically moves
    def shoot(self):
        Bullet(self.game, self.game.bulletImage, self.rect.x, self.rect.y, self.angle, self)

    # Used as a getter to get the y velocity of the plane
    @property
    def vel_y(self):
        return self.yVelocity


class AIPlane(Plane):
    def __init__(self, game, image: pg.Surface, x, y, brain):
        """
        Constructor method
        :param game: pygame simulation
        :param image: sprite image
        :param x: x location of sprite
        :param y: y location of sprite
        :param brain: Individual object (i.e., CGP genotype)
        """
        super().__init__(game, image, x, y)
        self.brain = brain

    # Method to kill the sprite and set it's final score values
    def kill(self):
        super().kill()
        self.brain.totalFitness = self.totalScore
        self.brain.distanceFitness = self.distanceScore
        self.brain.targetFitness = self.targetScore

    def eval(self, v, h, g, vr, hr):
        """
        Evaluates the CGP and returns its final outputs
        Inputs are all inputs from state information of drone
        :param v: width from nearest right radar
        :param h: height from nearest right radar
        :param g: gap between a pair of radars
        :param vr: width from nearest target
        :param hr: height from nearest target
        :return: tuple of outputs (in this case, 2)
        """
        return self.brain.eval(v, h, g, vr, hr)


# Enum to set whether a radar beam is top or bottom (left or right)
class RadarType(enum.Enum):
    TOP = 0
    BOTTOM = 1


class Radar(MovableSprite):
    def __init__(self, game, image, centerx, length, type_):
        """
        Constructor method
        :param game: Actual simulation
        :param image: Image of sprite
        :param centerx: Center of radar beam (x direction)
        :param length: Length of radar team
        :param type_: Enum type (top or bottom)
        """
        self._layer = 2
        super().__init__(game.allSprites, game.radars)
        self._game = game
        self.type = type_
        # crop the image to the specified length
        self.image = pg.Surface((image.get_width(), length))
        if type_ == RadarType.TOP:
            self.image.blit(image, (0, 0), (0, image.get_height() - length, image.get_width(), length))
        else:
            self.image.blit(image, (0, 0), (0, 0, image.get_width(), length))
        # position and region
        self.rect = self.image.get_rect(centerx=centerx)
        if type_ == RadarType.TOP:
            self.rect.top = 0
        else:
            self.rect.bottom = st.SCREEN_HEIGHT
        self.gap = 0
        self.length = length


class Target(MovableSprite):

    def __init__(self, game, image: pg.Surface, x, y):
        """
        Constructor method
        :param game: pygame simulation
        :param image: sprite image
        :param x: x location of sprite
        :param y: y location of sprite
        """
        self._layer = 1
        super().__init__(game.allSprites, game.targets)
        self._game = game
        self.image = image
        self.rect = image.get_rect(x=x, y=y)

    # Kills the sprite
    def kill(self):
        super().kill()


class Bullet(MovableSprite):

    def __init__(self, game, image: pg.Surface, x, y, angle, plane):
        """
        Constructor method
        :param game: pygame simulation
        :param image: sprite image
        :param x: x location of sprite
        :param y: y location of sprite
        :param angle: Angle of bullet
        :param plane: Which plane object shot the bullet
        """
        self._layer = 1
        super().__init__(game.allSprites, game.bullets)
        self._game = game
        self.image = image
        self.origin_image = self.image
        self.rect = self.image.get_rect(x=x, y=y)
        self.angle = angle
        self.plane = plane

    def moveBy(self, dx=0, dy=0):
        """
        Takes dx value and desired angle and tells bullet
        how quickly to move in the x and y directions using trigonometry
        :param dx: Speed for bullet to move in x direction
        :param dy: Speed for bullet to move in y direction
        :return: none
        """
        self.rect.move_ip(dx, dx * math.tan(math.degrees(self.angle)))


class Background(pg.sprite.Sprite):
    def __init__(self, game, image):
        """
        Creates background for simulation
        :param game: Actual simulation
        :param image: Background image
        """
        self._layer = 0
        super().__init__(game.allSprites)
        self.image = image
        self.rect = self.image.get_rect()
