
from easygopigo3 import EasyGoPiGo3
import time
import math

# to do: make bot class

########### INITIALIZE ROBOT OBJECT ###########
# create an instance of the GoPiGo3 class.
# gpg will be the GoPiGo3 object.
gpg = EasyGoPiGo3()

########### INITIALIZE VARIABLES ###########

### IDEAL SPEED ###
targetMin = 1 # minutes of target time
targetSec = 5 # seconds of target time
pathLength = 20.5 # total length of path, including back and forth

nTurns = 9 # number of turns in path

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
    def __init__(self):
        speed = self.calcIdealSpeed()
        gpg.set_speed(speed) # initialize speed
    
    def calcIdealSpeed(self):
        totalTurnTime = nTurns * turnTime
        totalTime = targetMin * 60 + targetSec - totalTurnTime

        wheelCircumference = wheelDiameter * math.pi
        
        totalSqs = pathLength * sqLen
        
        totalRotations = totalSqs / wheelCircumference
        totalDegrees = totalRotations * 360
        ans = totalDegrees / totalTime
        
        return math.ceil(ans)
    
    def calcDirt(self, a,b):
        # returns dir tuple
        # a start
        # b end
        
        x1,y1 = a
        x2,y2 = b
        
        hor = x2 - x1
        ver = y2 - y1
        
        unitHor = hor/abs(hor)
        unitVer = ver/abs(ver)
        
        return (unitHor, unitVer)

    def calcDists(self, a,b):
        # returns taxicab distance
        # a start
        # b end
        
        x1,y1 = a
        x2,y2 = b
        
        hor = x2 - x1
        ver = y2 - y1
        
        return (hor,ver)

    def calcHalfLoc(self, loc,dir):
        # returns location tuple
        lx,ly = loc
        vx,vy = dirts[dir]
        hx,hy = 0.5*vx, 0.5*vy
        halfLoc = (lx+hx,ly+hy)

        return halfLoc
        
    

    def reverseDirt(self,t):
        x,y = t
        return (-1*x, -1*y)
    
    def reverseDirh(self,h):
        t = dirts[h]
        nt = self.reverseDirt(t)
        nh = dirhs[nt]

        return nh


    def calcCW(self, t):
        x,y = t
        x = (x+1)%2
        y = (y+1)%2
        return (x,y)    

    def chooseDirh(self, tr,tl):
        ans = "r"
        if tr>tl:
            ans = "l"
        return ans

    def calcTurn(self, cd,fd,tr,tl):
        cDirt = cx, cy = dirts[cd]
        fDirt = fx, fy = dirts[fd]
        currDirh = "r"

        tx,ty = (fx-cx), (fy-cy)

        hflip = (cd=="l" or cd=="r") and (fd=="l" or fd=="r")
        vflip = (cd=="u" or cd=="d") and (fd=="u" or fd=="d")
        flip = hflip or vflip

        # {"u":(0,-1), "d":(0,1), "l":(-1,0), "r":(1,0)}
        # ur (1,-1)  r
        # ul (-1,1)  l
        # dr (1,1)   l
        # dl (-1,-1) r
        # ll (0,0)

        # if flip:
        #     currDirh = chooseDirh(tr,tl)
            
        pass

class Bobby:
    def __init__(self, sl, cl, el, sd, cd, ed):
        driver = Drive()
        logicker = Strat()

        startLoc = sl
        currLoc = cl
        endLoc = el
        startDirh = sd
        currDirh = logicker.reverseDir(cd)
        endDirh = ed

        totalDist = 0
        totalR = 0
        totalL = 0

    def parse(self,str):
        # shall return list of instructions
        # example: "d-A3-l d-C3-u g-E1-u"
        # [("d", "A3", "l"), ("d", "C3", "u"), ("g", "E1", "u")]
        ans = []
        insts = str.split()
        for i in insts:
            parts = i.split("-")
            ans.append(tuple(parts))

        return ans
    
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
    # to drive to A3 from the left, type d-A3-l
    # to drive to the right edge of A4, type hd-A4-r
    # to enter a gate at E1 from the top, g-E1-u
    # no special water bottle function yet

        insts = self.parse(str)

        for i in insts:
            act, loc, dirh = i
            dirt = dirts[dirh]

            if act=="d":
                # in progress
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


