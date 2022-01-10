"""
Sprites used in the game: the plane and the pipe.
"""
import enum
import math

import pygame as pg

import settings as st


class MovableSprite(pg.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = None

    def moveto(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y

    def moveBy(self, dy=0, dx=0):
        self.rect.move_ip(dx, dy)


class Plane(MovableSprite):
    def __init__(self, game, image: pg.Surface, x, y):
        self._layer = 3  # required for pygame.sprite.LayeredUpdates: set before adding it to the group!
        super().__init__(game.allSprites, game.planes)
        self.game = game
        self.image = image
        self.originImage = self.image
        self.rect = image.get_rect(x=x, y=y)
        self.yVelocity = 0
        self.distanceScore = 0
        self.targetScore = 0
        self.totalScore = self.distanceScore + (st.WEIGHT_TARGETS * self.targetScore)
        self.angle = 0

    def update(self, *args):
        # check whether the plane flies outside the boundary
        # whether it hits a pipe
        if self.rect.top > st.SCREEN_HEIGHT or self.rect.bottom < 0:
            st.allPlanes[-1].append(self.totalScore)
            # st.allPlanesDistance[-1].append(self.distanceScore)
            self.kill()
            return
        if pg.sprite.spritecollideany(self, self.game.radars):
            # If the plane makes a distance score over 1000, more heavily weight it to select from those parents
            if st.MU_WEIGHTS is not None and self.distanceScore > 1000:
                if len(st.MU_WEIGHTS) == 7:
                    st.MU_WEIGHTS = [10, 20, 30, 55, 80, 90, 100]
            st.allPlanes[-1].append(self.totalScore)
            # st.allPlanesDistance[-1].append(self.distanceScore)
            self.kill()
            return
        # Assumed that if the plane can make it that far, it can traverse the radar infinitely, so kill and restart
        # If the plane makes it all the way, even more heavily weight it to choose from the distance parents
        if self.distanceScore >= st.PLANE_MAX_DISTANCE_ALLOWED:
            if st.MU_WEIGHTS is not None and len(st.MU_WEIGHTS) == 7:
                st.MU_WEIGHTS = [7, 14, 21, 45, 69, 93, 100]
            st.allPlanes[-1].append(self.totalScore)
            st.all4ks[-1].append([self.totalScore, self.targetScore])
            # st.allPlanesDistance[-1].append(self.distanceScore)
            self.kill()
            return
        self.yVelocity = self.yVelocity
        self.rect.y += self.yVelocity
        # rotate the plane according to how it is moving: [-4, 4] -> 40 degree
        angle = 40 - (self.yVelocity + 4) / 8 * 80
        self.angle = min(30, max(angle, -30))
        self.image = pg.transform.rotate(self.originImage, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.totalScore = self.distanceScore + (st.WEIGHT_TARGETS * self.targetScore)
        # self.totalScore = self.distanceScore + max(0, 50 * self.targetScore)

    def turnLeft(self):
        self.yVelocity = st.PLANE_Y_SPEED

    def turnRight(self):
        self.yVelocity = -st.PLANE_Y_SPEED

    def goStraight(self):
        self.yVelocity = 0

    def shoot(self):
        Bullet(self.game, self.game.bulletImage, self.rect.x, self.rect.y, self.angle, self)

    @property
    def vel_y(self):
        return self.yVelocity


class AIPlane(Plane):
    def __init__(self, game, image: pg.Surface, x, y, brain):
        super().__init__(game, image, x, y)
        self.brain = brain

    def kill(self):
        super().kill()
        self.brain.totalFitness = self.totalScore
        self.brain.distanceFitness = self.distanceScore
        self.brain.targetFitness = self.targetScore

    def eval(self, v, h, g, vr, hr):
        # Now has two outputs
        return self.brain.eval(v, h, g, vr, hr)


class RadarType(enum.Enum):
    TOP = 0
    BOTTOM = 1


class Radar(MovableSprite):
    def __init__(self, game, image, centerx, length, type_):
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
        self._layer = 1
        super().__init__(game.allSprites, game.targets)
        self._game = game
        self.image = image
        self.rect = image.get_rect(x=x, y=y)

    def kill(self):
        super().kill()


# TODO: ANGLES!
class Bullet(MovableSprite):

    def __init__(self, game, image: pg.Surface, x, y, angle, plane):
        self._layer = 1
        super().__init__(game.allSprites, game.bullets)
        self._game = game
        self.image = image
        self.origin_image = self.image
        self.rect = self.image.get_rect(x=x, y=y)
        self.angle = angle
        self.plane = plane
        # self.image = pg.transform.rotate(self.originImage, self.angle)

    def moveBy(self, dx=0, dy=0):
        self.rect.move_ip(dx, dx * math.tan(math.degrees(self.angle)))


class Background(pg.sprite.Sprite):
    """
    Seamless background class.
    """
    def __init__(self, game, image):
        self._layer = 0
        super().__init__(game.allSprites)
        # if the width of the given image < screen width, then repeat it until we get a wide enough one
        if image.get_width() < st.SCREEN_WIDTH:
            w = image.get_width()
            repeats = st.SCREEN_WIDTH // w + 1
            self.image = pg.Surface((w * repeats, image.get_height()))
            for i in range(repeats):
                self.image.blit(image, (i * w, 0))
        else:
            self.image = image
        self.rect = self.image.get_rect()
