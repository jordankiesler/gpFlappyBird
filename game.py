import random
import os.path
import os

import cgp
from sprites import *
import settings as st


class Game:
    def __init__(self):
        # This set of parameters is all just getting the simulation set up
        os.environ['SDL_VIDEO_WINDOW_POS'] = '200,300'
        pg.mixer.pre_init()
        pg.mixer.init()
        pg.init()
        self._screen = pg.display.set_mode((st.SCREEN_WIDTH, st.SCREEN_HEIGHT))
        pg.display.set_caption(st.TITLE)
        self._clock = pg.time.Clock()
        self._is_paused = False
        self._fps = st.FPS

        # Instantiate the variables that hold the simulation images
        self.planeImage = None
        self.radarImages = None
        self.targetImage = None
        self.bulletImage = None
        self.backgroundImage = None

        # Set up sprite groups for all the sprites
        self.allSprites = pg.sprite.LayeredUpdates()
        self.planes = pg.sprite.Group()
        self.radars = pg.sprite.Group()
        self.targets = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.loadImages()                           # Load the images for the sprites

        self.running = True                         # True for entirety of simulation
        self.playing = False                        # True while at least one plane is alive - trips start of new gen
        self.frontRadar = None                      # Instantiate variable for the radar in the most front
        self.frontTarget = None                     # Instantiate variable for the target in the most front
        self.numTargets = 0                         # Instantiate a variable to keep track of total targets generated

        # CGP settings / data for endless data analysis
        self.numPlanes = sum(st.MU) + st.LAMBDA     # Set the number of planes to mu plus lambda
        self.maxTotalScoreSoFar = 0                 # max distanceScore so far in all the rounds since the game started
        self.maxDistanceScoreSoFar = 0              # max distance score in all the rounds since the game started
        self.maxTargetScoreSoFar = 0                # max target distanceScore in all the rounds since the game started
        self.maxTotalScore = 0                      # max score of all the planes in this round (generation)
        self.maxDistanceScore = 0                   # Max Score for distance only of best overall plane in generation
        self.maxTargetScore = 0                     # Max dScore for targets only of best overall plane in generation
        self.bestPlaneScores = [0, 0, 0]            # Keeps track of all numbers for a single plane that's the best

        self.allPlanesTotal = []                    # Lists that hold the final value of every plane for every gen
        self.allPlanesDistance = []
        self.allPlanesTarget = []

        self.maxTotalList = []                      # Lists to hold the winners of each generation and total
        self.maxDistanceList = []
        self.maxTargetList = []

        self.maxTotalSoFarList = []                 # Lists to hold the winner thus far from every gen after each gen
        self.maxDistanceSoFarList = []
        self.maxTargetSoFarList = []

        self.bestPlaneScoresList = []               # List to hold the composite score of the best plane in each gen

        self.pop = cgp.createPopulation(self.numPlanes)    # Create the initial population
        # List to hold average num of active nodes per generation, starting with the first
        self.avgNumActiveNodes = [cgp.calculateAvgActiveNodes(self.pop)]
        self.currentGeneration = 0                         # Set the current generation to zero

    def reset(self):
        """
        Resets simulation after each generation
        :return: None
        """

        # If VERBOSE setting is set to true, print this after each generation
        if st.VERBOSE:
            print(f'------Generation: {self.currentGeneration}. Max total score so far: {self.maxTotalScoreSoFar}-----')

        # Collect relevant final values for the lists
        self.bestPlaneScoresList.append(self.bestPlaneScores)
        self.maxTotalList.append(self.maxTotalScore)
        self.maxTotalSoFarList.append(self.maxTotalScoreSoFar)
        self.maxDistanceList.append(self.maxDistanceScore)
        self.maxDistanceSoFarList.append(self.maxDistanceScoreSoFar)
        self.maxTargetList.append(self.maxTargetScore)
        self.maxTargetSoFarList.append(self.maxTargetScoreSoFar)

        st.allPlanes.append([])
        st.all4ks.append([])

        # Reset relevant values
        self.maxTotalScore = 0
        self.maxDistanceScore = 0
        self.maxTargetScore = 0
        self.numTargets = 0
        self.bestPlaneScores = []
        self.currentGeneration += 1

        # Empty all the current sprites if any
        for s in self.allSprites:
            s.kill()

        # Spawn planes - all start in the exact same place for consistency
        x = 50
        y = st.SCREEN_HEIGHT / 3
        for i in range(self.numPlanes):
            AIPlane(self, self.planeImage, x, y, self.pop[i])

        # Spawn the radars
        self.spawnRadar(80)  # the first pipe with x as the baseline
        while self.frontRadar.rect.x < st.SCREEN_WIDTH:
            self.spawnRadar()
        # Create the background
        Background(self, self.backgroundImage)

    def loadImages(self):
        """
        Load the sprite images
        :return: none
        """
        def _load_one_image(file_name):
            return pg.image.load(os.path.join(st.IMG_DIR, file_name)).convert_alpha()

        self.planeImage = _load_one_image('airplane.png')
        self.radarImages = [_load_one_image(name) for name in ['radarTop.png', 'radarBottom.png']]
        self.backgroundImage = _load_one_image('background2.png')
        self.targetImage = _load_one_image('triangle.png')
        self.bulletImage = _load_one_image('bullet.png')

    def spawnRadar(self, frontX=None):
        """
        Create a new pair of radars in the front.
        :param frontX: X-coordinate of the currently most front radar
        """
        # If no frontX  is set, set it to the front most radar's x-value
        if frontX is None:
            frontX = self.frontRadar.rect.x
        # Randomly set the space between this radar and the next radar within the allotted range
        radarSpace = random.randint(st.MIN_RADAR_SPACE, st.MAX_RADAR_SPACE)
        centerx = frontX + radarSpace
        d_gap = st.MAX_RADAR_GAP - st.MIN_RADAR_GAP             # Get size of allowable radar gap
        d_space = st.MAX_RADAR_SPACE - st.MIN_RADAR_SPACE       # Get size of allowable radar space

        # If the radar space is larger than the mean space, then choose a radar gap randomly from the size
        if radarSpace > (st.MIN_RADAR_SPACE + st.MAX_RADAR_SPACE) / 2:
            gap = random.randint(st.MIN_RADAR_GAP, st.MAX_RADAR_GAP)
        # If the radar space is on the smaller side, then do some math to choose it so it's not too small
        else:
            gap = random.randint(int(st.MAX_RADAR_GAP - d_gap * (radarSpace - st.MIN_RADAR_SPACE) / d_space),
                                 st.MAX_RADAR_GAP) + 8

        # if radar space is too small, then the top_length should be similar to the previous one
        if radarSpace - st.MIN_RADAR_GAP < d_space // 3:
            top_length = self.frontRadar.length + random.randint(-50, 50)
        else:
            top_length = random.randint(st.MIN_RADAR_LENGTH, st.SCREEN_HEIGHT - gap - st.MIN_RADAR_LENGTH)
        if self.frontRadar is not None:
            gap += abs(top_length - self.frontRadar.length) // 10
        bottom_length = st.SCREEN_HEIGHT - gap - top_length

        # Create the darads and set the appropriate variables
        topRadar = Radar(self, self.radarImages[0], centerx, top_length, RadarType.TOP)
        bottomRadar = Radar(self, self.radarImages[1], centerx, bottom_length, RadarType.BOTTOM)
        self.frontRadar = topRadar
        topRadar.gap = gap
        bottomRadar.gap = gap

    def run(self):
        """
        Overall function that runs the simulation
        and calls all the necessary upkeep functions
        :return: none
        """
        self.playing = True
        # While the simulation is running, do all the required updating
        while self.playing:
            self.handleEvents()
            self.update()
            self.draw()
            self._clock.tick(self._fps)
        if not self.running:
            return              # This is the conclusion of one generation
        # if current distanceScore is very low, then we use a large mutation rate -
        # This was largely unused for this project for consistency in data, but can
        # be used/tweaked to create an adjustable learning rate for a more finely tuned model
        pb = st.MUT_PB
        # if self.maxDistanceScoreSoFar < 100:
        #     pb = st.MUT_PB * 10
        # elif self.maxDistanceScoreSoFar < 1000:
        #     pb = st.MUT_PB * 5
        # elif self.maxDistanceScore < 3000:
        #     pb = st.MUT_PB * 2
        self.pop = cgp.evolve(self.pop, pb, st.MU, st.LAMBDA, st.MU_WEIGHTS)
        self.avgNumActiveNodes.append(cgp.calculateAvgActiveNodes(self.pop))

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
                self.drawText("Paused", x=st.SCREEN_WIDTH // 2 - 50, y=st.SCREEN_HEIGHT // 2 - 10,
                              color=st.WHITE, size=2 * st.FONT_SIZE)
                pg.display.update()
                pg.time.wait(50)

    def handleEvents(self):
        """
        Handle keystroke events by user and actions by drones
        """
        for event in pg.event.get():
            # If user exits simulation, close it down
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pg.KEYDOWN:
                pressed = pg.key.get_pressed()
                ctrl_held = pressed[pg.K_LCTRL] or pressed[pg.K_RCTRL]
                if ctrl_held:
                    if event.key == pg.K_p:         # ctrl + p: pause the game
                        self._is_paused = True
                        self.pause()
                    elif event.key == pg.K_1:       # ctrl + 1 (2, 3): change the frame rate
                        self._fps = st.FPS
                    elif event.key == pg.K_2:
                        self._fps = 0.1 * st.FPS
                    elif event.key == pg.K_3:
                        self._fps = 0.5 * st.FPS

        # Run method that checks if plane needs to turn or shoot
        for plane in self.planes:
            self.tryAction(plane)

    def getFrontBottomRadar(self, plane):
        """
        Get the most front radar before the plane (the right (bottom) one)
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
            return Target(self, self.targetImage, random.randint(st.SCREEN_WIDTH, st.SCREEN_WIDTH * 1.2), random.randint(100, 400))

    def tryAction(self, plane):
        """
        See if any action needs to be taken for the plane based on the CGP
        """
        # compute the initial inputs
        frontBottomRadar = self.getFrontBottomRadar(plane)
        frontTarget = self.getFrontTarget(plane)

        # Five initial inputs that get fed to the CGP
        h = frontBottomRadar.rect.x - plane.rect.x
        v = frontBottomRadar.rect.y - plane.rect.y
        g = frontBottomRadar.gap
        hr = frontTarget.rect.x - plane.rect.x
        vr = frontTarget.rect.y - plane.rect.y

        # What plane should do depending on the output
        turningOutput, shootingOutput = plane.eval(v, h, g, vr, hr)
        if turningOutput > 0:
            plane.turnLeft()
        if turningOutput < 0:
            plane.turnRight()
        if turningOutput == 0:
            plane.goStraight()
        if shootingOutput > 0:
            plane.shoot()

    def update(self):
        """
        Update the state (position, life, etc.) of all sprites and the game
        """
        self.allSprites.update()
        # if all planes died, then game over
        if not self.planes:
            self.playing = False
            return

        leadingPlane = max(self.planes, key=lambda b: b.rect.x)
        # Move planes/bullets forward for start of game until they reach a third of screen width
        if leadingPlane.rect.x < st.SCREEN_WIDTH / 3:
            for plane in self.planes:
                plane.moveBy(dx=st.PLANE_X_SPEED)
            for bullet in self.bullets:
                bullet.moveBy(dx=3)
        # Move the radar/targets backwards such that planes seem to fly
        else:
            for radar in self.radars:
                radar.moveBy(dx=-st.PLANE_X_SPEED)
                if radar.rect.x < -50:
                    radar.kill()
            for target in self.targets:
                target.moveBy(dx=-st.PLANE_X_SPEED)
                if target.rect.x < -50:
                    target.kill()
            for bullet in self.bullets:
                bullet.moveBy(dx=3)
                # If bullet goes off the screen, end it and punish the plane who shot it
                if bullet.rect.x > st.SCREEN_WIDTH or st.SCREEN_HEIGHT < bullet.rect.y < -10:
                    # Punishes planes who shoot bullets and miss
                    bullet.plane.targetScore -= 0.5
                    bullet.kill()
        # count the distanceScore: one point per frame
        for plane in self.planes:
            plane.distanceScore += 1

        # Check to see if any bullets hit a target - reward those that did with plus points and kill target/bullet
        for bullet in self.bullets:
            # To leave target alive to be shot indefinitely, change spritecollide to spritecollideany, delete the
            # dokill option, and uncomment bullet.kill()
            if pg.sprite.spritecollide(bullet, self.targets, dokill=True):
                bullet.plane.targetScore += 4
                # bullet.kill()

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

        # spawn a new radar if necessary; spawns a new target for every new radar spawned
        while self.frontRadar.rect.x < st.SCREEN_WIDTH:
            self.spawnRadar()
            Target(self, self.targetImage, random.randint(st.SCREEN_WIDTH, st.SCREEN_WIDTH * 1.2), random.randint(100, 400))
            self.numTargets += 1

    def draw(self):
        """
        Draws everything onto the pygame canvas -
        scoring, sprites, etc.
        :return: none
        """
        self.allSprites.draw(self._screen)
        # Different options of what to show - I wanted to see the current distance so I knew when the planes got to
        # 4000 points, since often the best plane died sooner - if you want to see the other one, just uncomment
        # self.drawText('Distance Score: {}'.format(self.bestPlaneScores[1]), 10, 10)
        self.drawText('Distance Score: {}'.format(self.maxDistanceScore), 10, 10)
        self.drawText('Target Score: {}'.format(self.bestPlaneScores[2]), 10 + st.FONT_SIZE + 2, 10)
        self.drawText('Total Score: {}'.format(self.bestPlaneScores[0]), 10 + 2 * (st.FONT_SIZE + 2), 10)
        self.drawText('Max Total Score so far: {}'.format(self.maxTotalScoreSoFar), 10 + 3 * (st.FONT_SIZE + 2), 10)
        self.drawText('Generation: {}'.format(self.currentGeneration), 10 + 4 * (st.FONT_SIZE + 2), 10)
        numAlive = len(self.planes)
        self.drawText('Alive: {} / {}'.format(numAlive, self.numPlanes), 10 + 5 * (st.FONT_SIZE + 2), 10)
        # Rotate the screen so it flies up instead of sideways (easiest way to do it rather than try to flip
        # around all the variables
        self._screen.blit(pg.transform.rotate(self._screen, 90), (0, 0))
        pg.display.flip()
        pg.display.update()

    # Pygame mechanics for rendering the font, and right side up, too
    def drawText(self, text, x, y, color=st.WHITE, font=st.FONT_NAME, size=st.FONT_SIZE):
        font = pg.font.SysFont(font, size)
        text_surface = font.render(text, True, color)
        self._screen.blit(pg.transform.rotate(text_surface, -90), (x, y))
