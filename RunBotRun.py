import pygame
from random import randint, choice

class RunBotRun():
    def __init__(self):
        pygame.init()
        self.wallcolors = [(204, 173, 0),(64, 224, 208),(255, 105, 180),(46, 204, 16),(138, 43, 226),(0, 191, 255),(220, 20, 60)]
        self.screenw = 1024
        self.screenh = 768
        self.gamefieldy = 728 #end coordinate for actual game field
        self.loadimages()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screenw, self.screenh))
        self.font = pygame.font.SysFont("Courier New", 30, True)
        pygame.display.set_caption("RunBotRun")

        self.startup()

    def loadimages(self):
        self.images = {}
        for pic in ["coin", "door", "monster", "robot"]:
            self.images[pic] = pygame.image.load(pic + ".png")
        self.robotw = self.images["robot"].get_width()
        self.roboth = self.images["robot"].get_height() #robot dimensions are widely used in other functions so I'm choosing to store them in variables

    def gethitbox(self, location, object): #Gets the hitbox of an image from the images list
        return pygame.Rect(location[0], location[1], self.images[object].get_width(), self.images[object].get_height())

    def startup(self): #Displays the startup screen
        self.screen.fill((0,0,0))
        text = self.font.render("Welcome to the game.",True, (0,0,0), (255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 75))
        text = self.font.render("Collect all the coins to unlock the door.",True, (255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 125))
        text = self.font.render("Don't let the monster catch you!", True, (255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 175))
        text = self.font.render("Enter to start the game. Arrows to move. Esc to quit.", True, (255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 700))
        self.screen.blit(self.images["robot"], (500, self.screenw/2 - self.robotw /2))
        pygame.display.flip()
        self.altloop()

    def altloop(self): #Loop for start and end screens
        while True:
            self.alteventhandle()

    def alteventhandle(self): #Event handler for alt loop
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.startgame()
                    self.mainloop()
                if event.key == pygame.K_ESCAPE:
                    exit()
            if event.type == pygame.QUIT:
                exit()

    def startgame(self): #Initializes game, calls the level generator
        self.background = [255, 255, 255]
        self.colorindex = 0
        self.lives = 3
        self.level = 1
        
        doorh, doorw = self.images["door"].get_width(), self.images["door"].get_height()  #The door is always in the same place
        self.door = self.gethitbox((self.screenw - doorw, self.screenh/2 - doorh/2), "door")
        self.doorhitbox = pygame.Rect(self.door.x - 20, self.door.y - 20, self.door.width + 40, self.door.height + 40) #Adding a nice buffer of air around the door
        
        self.s = 2 #robot movement speed

        self.pressedkey = {}
        self.controls = [
        (pygame.K_LEFT, -self.s, 0),
        (pygame.K_RIGHT, self.s, 0),
        (pygame.K_UP, 0, -self.s),
        (pygame.K_DOWN, 0, self.s)
        ]

        self.newlevel()

    def newlevel(self): #Generates a new level
        self.robox = 10
        self.roboy = self.gamefieldy - self.roboth 
        forbiddenhitboxes = [self.doorhitbox, self.gethitbox((self.robox, self.roboy), "robot")]
        self.walls = self.spawnwalls(self.level, forbiddenhitboxes)
        forbiddenhitboxes.extend(self.walls)
        self.coins = self.spawncoins(self.level, forbiddenhitboxes)
        self.initialcoins = self.coins.copy() #For resetting upon failure
        monsterx, monstery = self.screenw/2 - self.images["monster"].get_width()/2, self.gamefieldy/2 - self.images["monster"].get_height()/2
        self.monster = self.gethitbox((monsterx, monstery), "monster")

    def spawnwalls (self, level, hitboxes): #Spawns one wall per level and ensures they're all neatly spaced out
        walldimensions = 5, 60
        walls = []
        wallhitbox = [] #list of wall buffer zones
        while len(walls) < level: 
            pos = choice(["hor", "vert"]) #randomly decide whether a wall is vertical or horizontal
            if pos == "hor":
                wallw = walldimensions[1]
                wallh = walldimensions[0]
            elif pos == "vert":
                wallw = walldimensions[0]
                wallh = walldimensions[1]

            wall = pygame.Rect(randint(self.robotw, self.screenw - self.robotw - 11), randint(wallw, self.gamefieldy - self.roboth), wallw, wallh) #Creates a rectangle object for a new wall, with placement rules to make it neat
            wallsafetybox = pygame.Rect(wall.x, wall.y, wall.width + self.robotw, wall.height + self.roboth) #creates a buffer zone for the wall above
            if wallsafetybox.collidelist(wallhitbox) == -1: #checks if the new wall's buffer zone overlaps with any existing wall buffer zones, proceeds with the wall if it doesn't    
                if wallsafetybox.collidelist(hitboxes) == -1:
                    walls.append(wall)
                    wallhitbox.append(wallsafetybox)
        return walls

    def spawncoins(self, level, hitboxes): #Spawns 3 to 7 coins depending on the level and makes sure they're all clear of other objects
        amount = range(3,8)[int((level - 1) % 10 / 2)]
        coins = []
        coinboxes = []
        while len(coins) < amount:
            coincoords = randint(50, 1024 - self.images["coin"].get_width())-50, randint(50, self.gamefieldy - self.images["coin"].get_height()-50)
            coin = self.gethitbox(coincoords, "coin")
            if coin.collidelist(hitboxes) == -1:
                if coin.collidelist(coinboxes) == -1:
                    coins.append(coincoords)
                    coinboxes.append(coin)
        return coinboxes

    def mainloop(self): #Loop to run the game
        while True:
            self.gameeventhandle()
            self.gamehitboxcheck()
            self.movemonster()
            self.drawscreen()
            self.clock.tick(90)    

    def gameeventhandle(self): #Event handler for game loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.pressedkey[event.key] = True
            if event.type == pygame.KEYUP:
                del self.pressedkey[event.key]
            if event.type == pygame.QUIT:
                exit()

        for key in self.controls:
            if key[0] in self.pressedkey:
                self.robox += key[1]
                self.roboy += key[2]
                if self.checkrobotwallclear() or self.robox > self.screenw - self.robotw or self.robox < 0:
                    self.robox -= key[1]
                if self.checkrobotwallclear() or self.roboy > self.gamefieldy - self.roboth or self.roboy < 0:
                    self.roboy -= key[2]

    def movemonster(self): #Compares position of robot and position of monster, moves accordingly
        hitbox = self.gethitbox((self.robox, self.roboy), "robot")
        if self.monster.centerx > hitbox.centerx:
            self.monster.x -= 1
        elif self.monster.centerx < hitbox.centerx:
            self.monster.x += 1
        if self.monster.centery > hitbox.centery:
            self.monster.y -= 1
        elif self.monster.centery < hitbox.centery:
            self.monster.y += 1

    def drawscreen(self): #Renders the game screen
        self.screen.fill((self.background[0], self.background[1], self.background[2]))
        pygame.draw.line(self.screen, self.wallcolors[self.colorindex], (0, 728), (1024, 728), 3)

        text = self.font.render(f"Level: {self.level}", True, self.wallcolors[self.colorindex])
        self.screen.blit(text, (30, 730))

        text = self.font.render(f"Lives: {self.lives * '# '}", True, self.wallcolors[self.colorindex])
        self.screen.blit(text, (750, 730))

        for wall in self.walls:
            pygame.draw.rect(self.screen, self.wallcolors[self.colorindex], wall)

        for c in self.coins:
            self.screen.blit(self.images["coin"], (c.x, c.y))

        self.screen.blit(self.images["door"], (self.door.x, self.door.y))
        self.screen.blit(self.images["robot"], (self.robox, self.roboy))
        self.screen.blit(self.images["monster"], (self.monster.x, self.monster.y))

        pygame.display.flip()

    def checkrobotwallclear(self): #Prevents robot from running through walls
        hitbox = self.gethitbox((self.robox, self.roboy), "robot")
        if hitbox.collidelist(self.walls) == -1 :
            return False
        else:
            return True

    def gamehitboxcheck(self): #Handles game-affecting hitbox collisions
        self.robothitbox = self.gethitbox((self.robox, self.roboy), "robot")
        if self.checkrobotcoin() != None:
            self.coins.remove(self.checkrobotcoin())
        if self.checkrobotmonster():
            self.lives -= 1
            if self.lives <= 0:
                 self.gameover()
            else: 
                self.resetlevel()
        if self.checkrobotdoor():
            self.levelup()

    def checkrobotcoin(self): #Checks if the robot can pick up a coin, and returns the coin it picks up
        for c in self.coins:
            if self.robothitbox.colliderect(c):
                return c
        return None

    def checkrobotmonster(self): #Checks if the monster and the robot collide
        if self.robothitbox.colliderect(self.monster):
            return True
        else:
            return False
    
    def checkrobotdoor(self): #Checks whether the door is open and then whether the robot is in the door
        if len(self.coins) == 0: #There is no point in proceeding if there are still coins on the screen
            if self.robothitbox.collidepoint(self.door.center):
                return True
        return False

    def levelup (self): #Increases the game level and then calls the level generator
        self.level += 1
        if self.lives < 3: #Gotta have some mercy
            self.lives += 1 
        if self.level == 31:    #Ends the game upon beating max level. 40 was the highest level I could do without the success rate of wall spawning plummeting beyond reasonable limits,  but the difficulty becomes a barrier before that.
            self.congratulations() 
        self.colorindex += 1 #Cycles through colours for walls and texts
        if self.colorindex > 6:
            self.colorindex = 0
        self.background = [value - 6 for value in self.background] #Makes the background darker as the levels increase
        self.newlevel()

    def resetlevel(self): #Resets the level to its initial state when a life is lost
        self.robox = 10
        self.roboy = self.gamefieldy - self.roboth
        monsterx, monstery = self.screenw/2 - self.images["monster"].get_width()/2, self.gamefieldy/2 - self.images["monster"].get_height()/2
        self.monster = self.gethitbox((monsterx, monstery), "monster")
        self.coins = self.initialcoins.copy()
    
    def gameover(self): #Self explanatory
        self.screen.fill((self.background[0], self.background[1], self.background[2]))
        text = self.font.render("Game over, you lost :(", True, self.wallcolors[self.colorindex])
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, self.gamefieldy/2))
        pygame.draw.line(self.screen, self.wallcolors[self.colorindex], (0, 728), (1024, 728), 3)
        text = self.font.render("Enter to restart game    Esc to quit", True, self.wallcolors[self.colorindex])
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 730))
        pygame.display.flip()

        self.altloop()    

    def congratulations(self): #Also self explanatory
        self.screen.fill((255,255,255))
        for i in range(50):
            self.screen.blit(self.images["coin"], (randint(0, 1000), randint(0, 700)))
        text = self.font.render("Congratulations, you escaped the monster!",True,(0,0,0),(255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 75))
        text = self.font.render("I'm proud of you. Seriously.",True,(0,0,0),(255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 125))
        text = self.font.render("Take a screenshot and send it to me if you want to", True, (0,0,0), (255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 175))
        text = self.font.render("let me know that I'm supposed to be proud of you.", True, (0,0,0), (255,255,255))
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 225))
        pygame.draw.line(self.screen, self.wallcolors[self.colorindex], (0, 728), (1024, 728), 3)
        text = self.font.render("Enter to restart game    Esc to quit", True, self.wallcolors[self.colorindex])
        self.screen.blit(text, (self.screenw/2 - text.get_width()/2, 730))
        self.screen.blit(self.images["robot"], (500, self.screenw/2 - self.robotw /2))
        pygame.display.flip()

        self.altloop()


if __name__ == "__main__":
    RunBotRun() 