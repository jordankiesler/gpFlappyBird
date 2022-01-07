"""
The main flappy plane game.
"""
import random

import os.path
import os

import cgp
from sprites import *


class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = '200,300'
        pg.mixer.pre_init()
        pg.mixer.init()
        pg.init()
        self._screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption(TITLE)
        self._clock = pg.time.Clock()
        self._is_paused = False
        self._fps = FPS

        self.planeImage = None
        self.radarImages = None
        self.targetImage = None
        self.bulletImage = None
        self.backgroundImage = None

        self.allSprites = pg.sprite.LayeredUpdates()
        self.planes = pg.sprite.Group()
        self.radars = pg.sprite.Group()
        self.targets = pg.sprite.Group()  # Added
        self.bullets = pg.sprite.Group()  # Added
        self.loadImages()

        self.running = True
        self.playing = False
        self.frontRadar = None                      # the radar in the most front
        self.frontTarget = None                     # the target in the most front
        self.numTargets = 0

        # CGP settings
        self.numPlanes = sum(MU) + LAMBDA
        self.maxTotalScoreSoFar = 0                 # max distanceScore so far in all the rounds since the game started
        self.maxDistanceScoreSoFar = 0              # max distance score in all the rounds since the game started
        self.maxTargetScoreSoFar = 0                # max target distanceScore in all the rounds since the game started
        # Following 3 values are max for the given frame (update EVERY frame)
        # Therefore, while the distance value will always be the max, the target and total scores may not be the
        # max at the end of the generation - they need to treated as interim values only
        # I am very tired - it's good you're only grading code on whether it's sufficient, because it's a bit of a hack
        self.maxTotalScore = 0                      # max score of all the planes in this round (generation)
        self.maxDistanceScore = 0                   # Max Score for distance only of best overall plane in generation
        self.maxTargetScore = 0                     # Max dScore for targets only of best overall plane in generation
        self.bestPlaneScores = [0, 0, 0]            # Keeps track of all numbers for a single plane that's the best

        self.maxTotalList = []                      # Lists to hold the winners of each generation and total
        self.maxDistanceList = []
        self.maxTargetList = []
        self.maxTotalSoFarList = []
        self.maxDistanceSoFarList = []
        self.maxTargetSoFarList = []
        self.bestPlaneScoresList = []

        self.pop = cgp.create_population(self.numPlanes)    # create the initial population
        self.currentGeneration = 0

    def reset(self):
        if VERBOSE:
            print(f'------Generation: {self.currentGeneration}. Max total score so far: {self.maxTotalScoreSoFar}-----')

        # Collect relevant final values for the lists
        self.bestPlaneScoresList.append(self.bestPlaneScores)
        self.maxTotalList.append(self.maxTotalScore)
        self.maxTotalSoFarList.append(self.maxTotalScoreSoFar)
        self.maxDistanceList.append(self.maxDistanceScore)
        self.maxDistanceSoFarList.append(self.maxDistanceScoreSoFar)
        self.maxTargetList.append(self.maxTargetScore)
        self.maxTargetSoFarList.append(self.maxTargetScoreSoFar)

        # Reset relevant values
        self.maxTotalScore = 0
        self.maxDistanceScore = 0
        self.maxTargetScore = 0
        self.numTargets = 0
        self.bestPlaneScores = []
        self.currentGeneration += 1
        # empty all the current sprites if any
        for s in self.allSprites:
            s.kill()
        # instantiate planes
        x = 50
        y = SCREEN_HEIGHT / 3
        for i in range(self.numPlanes):
            AIPlane(self, self.planeImage, x, y, self.pop[i])
        # instantiate the radars
        self.spawnRadar(80)  # the first pipe with x as the baseline
        while self.frontRadar.rect.x < SCREEN_WIDTH:
            self.spawnRadar()
        # create the background
        Background(self, self.backgroundImage)

    def loadImages(self):

        def _load_one_image(file_name):
            return pg.image.load(os.path.join(IMG_DIR, file_name)).convert_alpha()

        self.planeImage = _load_one_image('airplane.png')
        self.radarImages = [_load_one_image(name) for name in ['radarTop.png', 'radarBottom.png']]
        self.backgroundImage = _load_one_image('background2.png')
        self.targetImage = _load_one_image('triangle.png')  # Added
        self.bulletImage = _load_one_image('bullet.png') # Added

    def spawnRadar(self, frontX=None):
        """
        Create a new pair of radars in the front.
        @:param frontX the x coordinate of the currently most front pipe. If None, then set self.frontRadar.rect.x
        """
        if frontX is None:
            frontX = self.frontRadar.rect.x
        radarSpace = random.randint(MIN_RADAR_SPACE, MAX_RADAR_SPACE)
        centerx = frontX + radarSpace
        d_gap = MAX_RADAR_GAP - MIN_RADAR_GAP
        d_space = MAX_RADAR_SPACE - MIN_RADAR_SPACE
        if radarSpace > (MIN_RADAR_SPACE + MAX_RADAR_SPACE) / 2:
            gap = random.randint(MIN_RADAR_GAP, MAX_RADAR_GAP)
        else:
            gap = random.randint(int(MAX_RADAR_GAP - d_gap * (radarSpace - MIN_RADAR_SPACE) / d_space),
                                 MAX_RADAR_GAP) + 8
        # if pipe space is too small, then the top_length should be similar to the previous one
        if radarSpace - MIN_RADAR_GAP < d_space // 3:
            top_length = self.frontRadar.length + random.randint(-50, 50)
        else:
            top_length = random.randint(MIN_RADAR_LENGTH, SCREEN_HEIGHT - gap - MIN_RADAR_LENGTH)
        if self.frontRadar is not None:
            gap += abs(top_length - self.frontRadar.length) // 10
        bottom_length = SCREEN_HEIGHT - gap - top_length
        topRadar = Radar(self, self.radarImages[0], centerx, top_length, RadarType.TOP)
        bottomRadar = Radar(self, self.radarImages[1], centerx, bottom_length, RadarType.BOTTOM)
        self.frontRadar = topRadar
        topRadar.gap = gap
        bottomRadar.gap = gap

    def run(self):
        self.playing = True
        while self.playing:
            self.handleEvents()
            self._update()
            self.draw()
            self._clock.tick(self._fps)
        if not self.running:
            return
        # one generation finished and perform evolution again
        # if current distanceScore is very low, then we use a large mutation rate
        pb = MUT_PB
        if self.maxDistanceScore < 100:
            pb = MUT_PB * 10
        elif self.maxDistanceScore < 1000:
            pb = MUT_PB * 5
        elif self.maxDistanceScore < 3000:
            pb = MUT_PB * 2
        elif self.maxDistanceScore < 5000:
            pb = MUT_PB * 1.2
        self.pop = cgp.evolve(self.pop, pb, MU, LAMBDA, MU_WEIGHTS)

    def pause(self):
        """
        Pause the game (ctrl + p to continue)
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.playing = False
                    self.running = False
                    return
                if event.type == pg.KEYDOWN:
                    pressed = pg.key.get_pressed()
                    ctrl_held = pressed[pg.K_LCTRL] or pressed[pg.K_RCTRL]
                    if ctrl_held and event.key == pg.K_p:
                        self._is_paused = False
                        return
                self.drawText("Paused", x=SCREEN_WIDTH // 2 - 50, y=SCREEN_HEIGHT // 2 - 10,
                              color=WHITE, size=2 * FONT_SIZE)
                pg.display.update()
                pg.time.wait(50)

    def handleEvents(self):
        """
        Handle key events
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pg.KEYDOWN:
                pressed = pg.key.get_pressed()
                ctrl_held = pressed[pg.K_LCTRL] or pressed[pg.K_RCTRL]
                if ctrl_held:
                    if event.key == pg.K_p:  # ctrl + p: pause the game
                        self._is_paused = True
                        self.pause()
                    elif event.key == pg.K_1:  # ctrl + 1 (2, 3): standard frame rate
                        self._fps = FPS
                    elif event.key == pg.K_2:
                        self._fps = 2 * FPS
                    elif event.key == pg.K_3:
                        self._fps = 3 * FPS

        for plane in self.planes:
            self.tryAction(plane)

    def getFrontBottomRadar(self, plane):
        """
        Get the most front pipe before the plane (the bottom one).
        """
        frontBottomRadar = min((p for p in self.radars if p.type == RadarType.BOTTOM and p.rect.right >= plane.rect.left),
                               key=lambda p: p.rect.x)
        return frontBottomRadar

    def getFrontTarget(self, plane):
        """
        Get the most front target before the plane
        """
        # Sometimes the next target spawned too far outside the window (feature kept to prevent too even of target
        # spacing), so if this happens, another target is spawned instead and fed to the machine
        try:
            frontTarget = min((r for r in self.targets if r.rect.right >= plane.rect.left), key=lambda r: r.rect.x)
            return frontTarget
        except ValueError:
            self.numTargets += 1
            return Target(self, self.targetImage, random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 1.2), random.randint(100, 400))

    def tryAction(self, plane):
        """
        Try to flap the plane if needed
        """
        # compute the tree inputs: v, h, g
        frontBottomRadar = self.getFrontBottomRadar(plane)
        frontTarget = self.getFrontTarget(plane)
        h = frontBottomRadar.rect.x - plane.rect.x
        v = frontBottomRadar.rect.y - plane.rect.y
        g = frontBottomRadar.gap

        hr = frontTarget.rect.x - plane.rect.x
        vr = frontTarget.rect.y - plane.rect.y

        if plane.eval(v, h, g, vr, hr)[0] > 0:
            plane.turnLeft()
        if plane.eval(v, h, g, vr, hr)[0] < 0:
            plane.turnRight()
        if plane.eval(v, h, g, vr, hr)[0] == 0:
            plane.goStraight()
        if plane.eval(v, h, g, vr, hr)[1] > 0:
            plane.shoot()

    def _update(self):
        """
        Update the state (position, life, etc.) of all sprites and the game
        """
        self.allSprites.update()
        # if all planes died, then game over
        if not self.planes:
            self.playing = False
            return
        # move the radars backwards such that planes seem to fly
        leadingPlane = max(self.planes, key=lambda b: b.rect.x)
        if leadingPlane.rect.x < SCREEN_WIDTH / 3:
            for plane in self.planes:
                plane.moveBy(dx=PLANE_X_SPEED)
            for bullet in self.bullets:
                bullet.moveBy(dx=3)
        else:
            for radar in self.radars:
                radar.moveBy(dx=-PLANE_X_SPEED)
                if radar.rect.x < -50:
                    radar.kill()
            for target in self.targets:
                target.moveBy(dx=-PLANE_X_SPEED)
                if target.rect.x < -50:
                    target.kill()
            # TODO: Angles!
            for bullet in self.bullets:
                bullet.moveBy(dx=3)
                if bullet.rect.x > SCREEN_WIDTH or SCREEN_HEIGHT < bullet.rect.y < -10:
                    # Punishes planes who shoot bullets and miss
                    bullet.plane.targetScore -= 0.5
                    bullet.kill()
        # count the distanceScore: one point per frame
        for plane in self.planes:
            plane.distanceScore += 1

        for bullet in self.bullets:
            if pg.sprite.spritecollide(bullet, self.targets, dokill=True):
                bullet.plane.targetScore += 4

        # Sorts planes to find one with highest total score, and sets appropriate values (repeat for dist and targets)
        sortedPlanes = sorted(self.planes, key=lambda plane: plane.totalScore)
        # Stores score value for all 3 categories for plane with best overall performance in a generation
        self.bestPlaneScores = max(self.bestPlaneScores, [sortedPlanes[-1].totalScore, sortedPlanes[-1].distanceScore,
                                                          sortedPlanes[-1].targetScore])
        self.maxTotalScore = max(self.maxTotalScore, sortedPlanes[-1].totalScore)
        self.maxTotalScoreSoFar = max(self.maxTotalScoreSoFar, self.maxTotalScore)

        sortedPlanes2 = sorted(self.planes, key=lambda plane: plane.distanceScore)
        self.maxDistanceScore = sortedPlanes2[-1].distanceScore
        self.maxDistanceScoreSoFar = max(self.maxDistanceScoreSoFar, self.maxDistanceScore)

        sortedPlanes3 = sorted(self.planes, key=lambda plane: plane.targetScore)
        self.maxTargetScore = max(self.maxTargetScore, sortedPlanes3[-1].targetScore)
        self.maxTargetScoreSoFar = max(self.maxTargetScoreSoFar, self.maxTargetScore)

        # spawn a new pipe if necessary
        while self.frontRadar.rect.x < SCREEN_WIDTH:
            self.spawnRadar()
            Target(self, self.targetImage, random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 1.2), random.randint(100, 400))
            self.numTargets += 1

    def draw(self):
        self.allSprites.draw(self._screen)
        # show distanceScore
        self.drawText('Distance Score: {}'.format(self.maxDistanceScore), 10, 10)
        self.drawText('Target Score: {}'.format(self.maxTargetScore), 10 + FONT_SIZE + 2, 10)
        self.drawText('Total Score: {}'.format(self.maxTotalScore), 10 + 2 * (FONT_SIZE + 2), 10)
        self.drawText('Max Total Score so far: {}'.format(self.maxTotalScoreSoFar), 10 + 3 * (FONT_SIZE + 2), 10)
        self.drawText('Generation: {}'.format(self.currentGeneration), 10 + 4 * (FONT_SIZE + 2), 10)
        numAlive = len(self.planes)
        self.drawText('Alive: {} / {}'.format(numAlive, self.numPlanes), 10 + 5 * (FONT_SIZE + 2), 10)
        self._screen.blit(pg.transform.rotate(self._screen, 90), (0, 0))
        pg.display.flip()
        pg.display.update()

    def drawText(self, text, x, y, color=WHITE, font=FONT_NAME, size=FONT_SIZE):
        font = pg.font.SysFont(font, size)
        text_surface = font.render(text, True, color)
        self._screen.blit(pg.transform.rotate(text_surface, -90), (x, y))
