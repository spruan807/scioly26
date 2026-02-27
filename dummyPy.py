
from easygopigo3 import EasyGoPiGo3
import time
import math

# to do: separate classes

########### INITIALIZE ROBOT OBJECT ###########
# create an instance of the GoPiGo3 class.
# gpg will be the GoPiGo3 object.
gpg = EasyGoPiGo3()

########### INITIALIZE VARIABLES ###########

### IDEAL SPEED ###
targetMin = 1 # minutes of target time
targetSec = 5 # seconds of target time
# pathLength = 20.5 # total length of path, including back and forth

# nTurns = 9 # number of turns in path

### ONLY FOR REFERENCE ###
sqLen = 50 # DO NOT CHANGE. the width of one square unit on the track.
lIndex = {"A":0, "B":1, "C":2, "D":3, "E":4}
dirts = {"u":(0,-1), "d":(0,1), "l":(-1,0), "r":(1,0)}
dirhs = {(0,-1):"u", (0,1):"d", (-1,0):"l", (1,0):"r"}

########### CONTROL PANEL ACCESS ###########
# control panel file location, for calibration
# /home/pi/Dexter/GoPiGo3/Software/Python/Examples/Control_Panel/control_panel_gui_3.py

### calibration variables ###
# preferred to calibrate in the CONTROL PANEL
ninety = 85 # what 90 degrees actually is based on your robot
turnTime = 3.618 # run timing code below to calibrate
wheelDiameter = 66.5 # in millimeters

class Drive():
    def __init__(self,s):
        speed = s

    def pause(self):
        time.sleep(0.5)

    def r(self):
        # turn right, 90 degrees
        gpg.set_speed(50)
        self.pause() # give the wheels a bit of time to rest!
        gpg.turn_degrees(ninety)
        gpg.set_speed(self.speed)

    def l(self):
        # turn left, 90 degrees
        gpg.set_speed(50)
        self.pause()
        gpg.turn_degrees(- ninety)
        gpg.set_speed(self.speed)

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

    def drive(cl, cd, fl, fd, tr, tl):
    # will always make big right angle, no zig zag
    # returns distance and turn numbers
    
        # horDist, verDist = calcDists(cl,fl)
        
        # cDirt = dirts[cd]
        # fDirt = dirts[fd]

        # if fd=="u" or fd=="d":
        #     pass
        #     # in progress

        pass

class Strat():
    def __init__(self,sl,cl,el,sd,cd,ed,p):
        pathLen = 0
        totalR = 0
        totalL = 0

        startLoc = sl
        currLoc = cl
        endLoc = el

        startDirh = sd
        currFaceh = self.reverseDirh(cd)
        endDirh = ed

        steps = p

    def calcIdealSpeed(self):
        nTurns = self.totalR + self.totalL
        totalTurnTime = nTurns * turnTime
        totalTime = targetMin * 60 + targetSec - totalTurnTime

        wheelCircumference = wheelDiameter * math.pi
        
        totalSqs = self.pathLen * sqLen
        
        totalRotations = totalSqs / wheelCircumference
        totalDegrees = totalRotations * 360
        ans = totalDegrees / totalTime
        
        return math.ceil(ans)
    
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
        
        unitHor = hor/abs(hor)
        unitVer = ver/abs(ver)
        
        return (unitHor, unitVer)
    
    def calcNTurnsh(self,nextDirh):
        # returns direction, number of times to do
        turnDirh = self.chooseDirh()
        countTurns = 0

        fx,fy = f = dirts[self.faceCurrh]
        nx,ny = n = dirts[nextDirh]

        dx,dy = (fx-nx), (fy-ny)

        # {"u":(0,-1), "d":(0,1), "l":(-1,0), "r":(1,0)}
        # ur (1,1)  r
        # ru (-1,-1) l

        # ul (-1,1)  l
        # lu (1,-1)  r

        # dr (1,-1)   l
        # rd (-1,1) r

        # dl (-1,-1) r
        # ld (1,1) l

        # ll (0,0)
        # ud (0,2)
        # du (0,-2)
        # lr (2,0)
        # rl (-2,0)

        if abs(dx)==2 or abs(dy)==2:
            countTurns = 2
        elif f=="u" or n=="u":
            if (dx==1 and turnDirh=="l") or (dx==-1 and turnDirh=="r"):
                countTurns = 3
        elif f=="d" or n=="d":
            if (dx==1 and turnDirh=="r") or (dx==-1 and turnDirh=="l"):
                countTurns = 3
            
        return (turnDirh, countTurns)

    def updateCounters(self,ntd,nt,nd):
        if ntd=="r": 
            self.totalR+=nt
        else:
            self.totalL+=nt
        
        self.pathLen+=nd

    def calcDriveSequenceh(self, goalLoc, goalDirh):
        # returns code instruction tokens as list of code tuples
        # (act,dir/dist,nTurns/0)
        ans = []
        horDist, verDist = dist = self.calcDist(goalLoc)
        dirtx, dirty = dirt = self.calcNewDirt(goalLoc)

        order = [((0,dirty), verDist), ((dirtx,0), horDist)]

        if goalDirh=="v":
            order = [((dirtx,0), horDist),((0,dirty), verDist)]

        for (nextDirt, nextDist) in order:
            newTurnDirh, nTurns = self.calcNTurnsh(nextDirt)

            self.updateCounters(newTurnDirh,nTurns,nextDist) #this shouldn't be here

            ans.append(("r",newTurnDirh,nTurns))
            ans.append(("d",nextDist,0))

        return ans


    ### distance helpers ###
    
    def calcDist(self,goal):
        # returns horizontal and vert distances
        # a start
        # b end
        
        x1,y1 = self.currLoc
        x2,y2 = goal
        
        hor = x2 - x1
        ver = y2 - y1
        
        return (hor,ver)

    def calcEdgeLoc(self,loc,dir):
        # returns location tuple of dir edge of loc square
        lx,ly = loc
        vx,vy = dirts[dir]
        hx,hy = 0.5*vx, 0.5*vy
        halfLoc = (lx+hx,ly+hy)

        return halfLoc
    
    ### strategizer ###
    def strategizer(self):
        ans=[]
        for step in self.steps:
            act,loc,dirh = step

            if act=="d":
                newSteps = self.calcDriveSequenceh(loc,dirh)
                ans = ans + newSteps
    

class Bobby:
    def __init__(self, sl, cl, el, sd, cd, ed, p):
        pathStr = p
        path = self.parseInit()

        logicker = Strat(sl,cl,el,sd,cd,ed,path) # init strat object

        speed = logicker.calcIdealSpeed()

        driver = Drive(speed) # init drive object

        gpg.set_speed(speed) # initialize speed

    def parseInit(self):
        # shall return list of instructions
        # example: "d-A3-h d-C3-v g-E1-v"
        # [("d", "A3", "l"), ("d", "C3", "u"), ("g", "E1", "u")]
        ans = []
        insts = self.pathStr.split()
        for i in insts:
            parts = i.split("-")
            ans.append(tuple(parts))

        return ans
    
    def parseToken(self):
        pass
    
    def run(self,str):
    # str is a string of instructions
    # rows A-E   (y-axis)
    # cols 0-4   (x-axis)
    #
    # A0 A1 A2 A3 A4
    # B0 B1 B2 B3 B4
    # C0 C1 C2 C3 C4
    # D0 D1 D2 D3 D4
    # E0 E1 E2 E3 E4
    #
    # to drive to A3 from the horizontal side, type d-A3-h
    # to drive to the right edge of A4, type hd-A4-r
        pass



########### WRITE CODE BELOW ###########

### turnTime calibration code, uncomment to use ###
# comment is alt 3, or cmd 3
# uncomment is alt 4, or cmd 4

# start = time.time()
# r()
# end = time.time()
# elapsed = end - start
# print("turn time is " + str(elapsed))

### driving code ###
# print("current speed is " + str(speed)) # COMMENT THIS OUT BEFORE DRIVING


