from easygopigo3 import EasyGoPiGo3
import time
import math

# to do: separate classes, refactor

########### INITIALIZE ROBOT OBJECT ###########
# create an instance of the GoPiGo3 class.
# gpg will be the GoPiGo3 object.
gpg = EasyGoPiGo3()

########### INITIALIZE VARIABLES ###########

### IDEAL SPEED ###
targetMin = 0 # minutes of target time
targetSec = 59 # seconds of target time

### DRIVE PATH ###
# A0 A1 A2 A3 A4
# B0 B1 B2 B3 B4
# C0 C1 C2 C3 C4
# D0 D1 D2 D3 D4
# E0 E1 E2 E3 E4
# to drive to A3 from the horizontal side, type d-A3-h
# to scoot back and push a water bottle to A5 horizontal, type w-A5-h
# to drive to the right edge of A4, type hd-A4-r

startCoords = "E1"
startEdge = "l"

drivePath="d-A4-v d-A1-h d-A3-h d-C3-v d-E2-v d-E4-h d-B1-v d-E1-v"
safePath="d-E4-h w-C4-v"
## IF AMBITIOUS RUN, ALL OF THE FOLLOWING SHOULD BE FALSE
testing=False
safe=True
calibrateRot=False
calibrateDrive=False

### ONLY FOR REFERENCE ###
sqLen = 50 # DO NOT CHANGE. the width of one square unit on the track.
lIndex = {"A":0, "B":1, "C":2, "D":3, "E":4}
dirts = {"u":(0,-1), "d":(0,1), "l":(-1,0), "r":(1,0)}
dirhs = {(0,-1):"u", (0,1):"d", (-1,0):"l", (1,0):"r"}

########### CONTROL PANEL ACCESS ###########
# control panel file location, for calibration
# /home/pi/Dexter/GoPiGo3/Software/Python/Examples/Control_Panel/control_panel_gui_3.py

### calibration variables ###
ninety = 90 # DEPRECIATED what 90 degrees actually is based on your robot
turnSpeed = 150
turnTime = 1.613 # run timing code below to calibrate

wheelDiameter = 69.5 # in millimeters
wheelDistance = 117 # in millimeters
startDist = 0.8

gpg.WHEEL_DIAMETER = wheelDiameter
gpg.WHEEL_CIRCUMFERENCE = gpg.WHEEL_DIAMETER * math.pi
gpg.WHEEL_BASE_WIDTH = wheelDistance
gpg.WHEEL_BASE_CIRCUMFERENCE = gpg.WHEEL_BASE_WIDTH * math.pi

class Drive():
    def __init__(self,s):
        self.speed = s

    def pause(self):
        time.sleep(0.5)

    def r(self):
        # turn right, 90 degrees
        gpg.set_speed(turnSpeed)
        self.pause() # give the wheels a bit of time to rest!
        gpg.turn_degrees(ninety)
        gpg.set_speed(self.speed)

    def l(self):
        # turn left, 90 degrees
        gpg.set_speed(turnSpeed)
        self.pause()
        gpg.turn_degrees(- ninety)
        gpg.set_speed(self.speed)

    def repR(self,nt):
        for n in range(nt):
            self.r()

    def repL(self,nt):
        for n in range(nt):
            self.l()

    def repTurn(self,dir,nt):
        if dir=="r":
            self.repR(nt)
        else:
            self.repL(nt)

    def driveSq(self, nSquares):
        # drives forward by "nSquares" amount of squares.
        # input a negative number to drive backwards
        # ex. drive(-5) to go back 5 squares
        gpg.drive_cm(sqLen*nSquares)

    def gate(self):
        # drives in and out of a gate
        # returns to original position and orientation once complete
        self.drive(sqLen//2)
        self.drive(sqLen//2)

class Strat():
    def __init__(self,sl,sd,p):
        self.pathLen = startDist
        self.totalR = 0
        self.totalL = 0

        self.startLoc = sl
        self.currLoc = sl

        self.startDirh = sd
        self.currFaceh = self.reverseDirh(sd)

        self.steps = p
        self.pathSteps = []
        
        self.strategizer()

    def calcIdealSpeed(self):
        nTurns = self.totalR + self.totalL
        totalTurnTime = nTurns * turnTime
        totalTime = abs(targetMin * 60 + targetSec - totalTurnTime)
        
        
        adjDiameter = wheelDiameter/10
        wheelCircumference = adjDiameter * math.pi
        
        totalSqs = self.pathLen * sqLen
        
        totalRotations = totalSqs / wheelCircumference
        totalDegrees = totalRotations * 360
        
#        print("path length")
#        print(self.pathLen)
#        print("total degrees")
#        print(totalDegrees)
#        print("total turns")
#        print(nTurns)
#        print("total time")
#        print(totalTime)

        ans = totalDegrees / totalTime
        
        fixAns = max(10, min(abs(math.ceil(ans)), 1000))
        
        return fixAns
    
    ### turn helpers ###
    
    def reverseDirt(self,t):
        x,y = t
        return (-1*x, -1*y)
    
    def reverseDirh(self,h):
        t = dirts[h]
        nt = self.reverseDirt(t)
        nh = dirhs[nt]
        return nh

    def dirtR(self, t):
        x,y = t
        x = (x+1)%2
        y = (y+1)%2
        return (x,y) 

    def dirtL(self, t):
        x,y = t
        x = (x-1)%2
        y = (y-1)%2
        return (x,y)    

    def chooseDirh(self):
        ans = "r"
        if self.totalR > self.totalL:
            ans = "l"
        return ans

    ### turn calculator ###
    def calcNewDirt(self,goal):
        # takes in goal loc
        # returns dir tuple
        # a start
        # b end
        
        x1,y1 = self.currLoc
        x2,y2 = goal
        
        hor = x2 - x1
        ver = y2 - y1
        
        unitHor = unitVer = 0
        
        if hor!=0:
            unitHor = hor/abs(hor)
        if ver!=0:
            unitVer = ver/abs(ver)
        
        return (unitHor, unitVer)
    
    def calcNTurnsh(self,nextDirt):
        # returns direction, number of times to do
        even = self.totalR==self.totalL
        
        countTurns = 1

        rech = self.chooseDirh()
        acth = "r"
        
        currH = self.currFaceh
        nextH = dirhs[nextDirt]
        
        fx,fy = f = dirts[currH]
        nx,ny = n = nextDirt

        dx,dy = (nx-fx), (ny-fy)
        
        if dx==-1 and (currH=="u" or nextH=="u"):
            acth="l"
        elif dx==1 and (currH=="d" or nextH=="d"):
            acth="l"
        elif abs(dx)==2 or abs(dy)==2:
            acth=rech
            countTurns=2
        
        if (dx,dy)==(0,0):
            countTurns = 0
        elif not even and acth!=rech:
            acth=rech
            countTurns=3
        
#        print((dx,dy))
#        print(rech)
#        print(acth)
#        print("done")
            
        return (acth, countTurns)

    def updates(self,nr,nl,nd,gl,gd):
        self.totalR+=nr
        self.totalL+=nl
        
        self.pathLen+=nd
        self.currLoc=gl
        self.currFaceh=gd

    ### distance helpers ###
    
    def calcDist(self,goal):
        # returns horizontal and vert distances
        # a start
        # b end
        
        x1,y1 = self.currLoc
        x2,y2 = goal
        
        hor = abs(x2 - x1)
        ver = abs(y2 - y1)
        
        return (hor,ver)

    def calcEdgeLoc(self,loc,dir):
        # returns location tuple of dir edge of loc square
        lx,ly = loc
        vx,vy = dirts[dir]
        hx,hy = 0.5*vx, 0.5*vy
        halfLoc = (lx+hx,ly+hy)

        return halfLoc
    
    def addTups(self,a,b):
        x,y = a
        w,z =  b
        return (x+w, y+z)
    
    def scaleTup(self,a,scale):
        x,y = a
        return (x*scale, y*scale)
    
    ### strategizer ###
    def calcDriveSequenceh(self, act, goalLoc, goalDirh):
        # returns code instruction tokens as list of code tuples
        # (act,dir/dist,nTurns/0)
        ans = []
        horDist, verDist = dist = self.calcDist(goalLoc)
        dirtx, dirty = dirt = self.calcNewDirt(goalLoc)
        
#        print("from")
#        print(self.currLoc)
#        print("to")
#        print(goalLoc)

        order = [((0,dirty), verDist), ((dirtx,0), horDist)]

        if goalDirh=="v":
            order = [((dirtx,0), horDist),((0,dirty), verDist)]

        # assumes all instructions are some form of drive...
        for (nextDirt, nextDist) in order:
            if nextDist==0:
                continue
            
#            print("next direction")
#            print(nextDirt)
#            print("next distance")
#            print(nextDist)
    
            newTurnDirh, nTurns = self.calcNTurnsh(nextDirt)
            newTurnDirt = dirts[newTurnDirh]
            reverseNewTurnDirt = self.scaleTup(newTurnDirt,-1)
            reverseNewTurnDirh = dirhs[reverseNewTurnDirt]

            distVec = self.scaleTup(nextDirt, nextDist)
            newLoc = self.addTups(self.currLoc, distVec)
            newFaceh = dirhs[nextDirt]

            addDist = nextDist
            addR = 0
            addL = 0

            if newTurnDirh=="r":
                addR+=nTurns
            else:
                addL+=nTurns

            if act=="w":
                ans.append(("d",-0.5,0))
                ans.append(("r",reverseNewTurnDirh,1))
                ans.append(("d",0.5,0))
                ans.append(("r",newTurnDirh,1))
                ans.append(("d",0.5,0))
                ans.append(("r",newTurnDirh,1))
                ans.append(("d",0.5,0))

                if newTurnDirh=="r":
                    addR+=2
                    addL+=1
                else:
                    addL+=2
                    addR+=1

            self.updates(addR,addL,addDist,newLoc,newFaceh) #this shouldn't be here
            
            if nTurns!=0 and not act=="w":
                ans.append(("r",newTurnDirh,nTurns))
                
            if nextDist!=0:
                ans.append(("d",abs(nextDist),0))

        return ans
    
    def strategizer(self):
        ans=[("d",startDist,0)]
        for step in self.steps:
            act,loc,dirh = step

            if act=="d" or act=="w":
                newSteps = self.calcDriveSequenceh(act,loc,dirh)
                
                ans = ans + newSteps
                
        self.pathSteps = ans
    

class Bobby:
    def __init__(self, sl, sd, p):
        self.path = self.parseInit(p)

        startLoc = self.parseLoc(sl)
        
        self.logicker = Strat(startLoc,sd,self.path) # init strat object

        self.speed = self.logicker.calcIdealSpeed()

        self.driver = Drive(self.speed) # init drive object

        gpg.set_speed(self.speed) # initialize speed

    def parseLoc(self,str):
        row = str[0]
        col = str[1]
        
        fixRow = lIndex[row]
        fixCol = int(col)
        
        return (fixCol, fixRow)
        
    def parseInit(self,pathStr):
        # shall return list of instructions
        # example: "d-A3-h d-C3-v g-E1-v"
        # [("d", "A3", "h"), ("d", "C3", "v"), ("g", "E1", "h")]
        ans = []
        insts = pathStr.split()
        for i in insts:
            parts = i.split("-")
            partsTuple = tuple(parts)
            fixLoc = self.parseLoc(partsTuple[1])
            ans.append((partsTuple[0], fixLoc, partsTuple[2]))

        return ans
    
    def run(self,drv):    
    # tokens look like:
    # (act,dir/dist,nTurns/0)

        pathSteps = self.logicker.pathSteps
        
        if drv:
            for step in pathSteps:
                act, d, nTurns = step

                if act=="r":
                    self.driver.repTurn(d,nTurns)
                elif act=="d":
                    self.driver.driveSq(d)
                
        return pathSteps
        


########### WRITE CODE BELOW ###########

### turnTime calibration code, uncomment to use ###
# comment is alt 3, or cmd 3
# uncomment is alt 4, or cmd 4

### driving code ###
# print("current speed is " + str(speed)) # COMMENT THIS OUT BEFORE DRIVING

bot = Drive(300)

if calibrateRot:
    start = time.time()
    for x in range(4): bot.l()
    end = time.time()
    elapsed = end - start
    print("turn time is " + str(elapsed/4))
elif calibrateDrive:
    bot.driveSq(1)
else:
    if safe:
        bot = Bobby(startCoords, startEdge, safePath)
    else:
        bot = Bobby(startCoords, startEdge, drivePath)
    
    debugStr = bot.run(not testing)

    if testing:
        print(bot.speed)
        for t in debugStr:
            print(t)