# This is a basic agent based disease spread simulation for our simulation class.
import itertools
import matplotlib
import matplotlib.pyplot as plt
import numpy.matlib
import numpy as np
import random

GRID_SIZE = 300
POP_SIZE = 8000
INFECTED_PER = 0.01 # Percentage of init population infected
INFECT_RATE = 0.7 # Chance of spreading
NUM_OF_CYCLES = 600
NUM_OF_SIMULATIONS = 5
DEVELOPMENT_CYCLES = 10 # time to die or recover from infection
DEATH_RATE = 0.5
DEATH_MUL_WHEN_OVER_CAP = 2.0 #amount of change in death rate when over capacity ex: deathrate*Deathmul if current infected > capacity
CAPACITY = 2000
INFECTION_RADIUS = 2
CHANCE_TO_MOVE = 1.0


def printGrid():
    stringToPrint = ""
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if(mainGrid[x][y] == None):
                stringToPrint = stringToPrint + "-" # print empty line
            else:
                stringToPrint = stringToPrint + str(mainGrid[x][y])
        print(stringToPrint)
        stringToPrint = ""
    print("") # print empty line

class person:
    
    def __init__(self, xIN, yIN):
        self.infected = False
        self.infectedTime = 0; # number of cycles infected
        self.dead = False
        self.recovered = False
        self.x = xIN
        self.y = yIN
        
    def __str__(self):
        return f'{"I" if self.infected else "X"}'
        
    def __repr__(self):
        return f'Person at ({self.x}, {self.y}) is {"infected" if self.infected else "NOT infected"}'
    
    def moveTo(self, xIN, yIN):
        if(mainGrid[xIN][yIN] == None and not self.dead): #if grid tile is empty and agent is not dead
            mainGrid[self.x][self.y] = None # clear current tile
            mainGrid[xIN][yIN] = self # move to new tile
            self.x = xIN #update self
            self.y = yIN
            return True
        return False # if could not move
        
    def moveRand(self):
        if(not self.dead and random.random() <= CHANCE_TO_MOVE): # if agent is alive and player decides to move
            clip = lambda num: max(0, min(GRID_SIZE-1, num)) #only allow numbers between 0 and the GRID_SIZE-1
            self.moveTo(
                clip(self.x + (random.randrange(-1,2))), # try random direction, if they can't move don't retry
                clip(self.y + (random.randrange(-1,2))) ) # 2 because range is wack in python
        
        
    def infectOthers(self, chance, infectRange=1):
        if(self.infected and not self.dead): #only infect others if you are infected and alive
            clip = lambda num: max(0, min(GRID_SIZE-1, num)) #only allow numbers between 0 and the GRID_SIZE-1
            
            for x in range(clip(self.x-infectRange) , clip(self.x+infectRange)): # x will go from left to right 
                for y in range(clip(self.y-infectRange) , clip(self.y+infectRange)): # y will be from bottom to top
                    if(x == self.x and y == self.y):
                        continue # do not atempt to infect self
                        
                    elif(mainGrid[x][y] != None): # attempt to infect others if they exist
                        if(mainGrid[x][y].recovered != True and mainGrid[x][y].dead != True and random.random() <= chance): #not dead or immune then possibly inffect
                            mainGrid[x][y].infected = True
                    
    def stepSickness(self, aboveCapacity):
        if(not self.dead): # if agent is alive
            if(self.infectedTime >= DEVELOPMENT_CYCLES and not self.recovered): #if sickness has develped either kill or recover the agent
                self.infected = False
                if(random.random() <= (DEATH_RATE if not aboveCapacity else (DEATH_RATE * DEATH_MUL_WHEN_OVER_CAP))):
                    self.dead = True
                    mainGrid[self.x][self.y] = None # clear current tile
                    self.x = None
                    self.y = None
                else:
                    self.recovered = True
            if(self.infected):
                self.infectedTime += 1


#start simulation
maxCycle = 0
infectedListList = []
deadListList = []
recoveredListList = []

for simulation in range(NUM_OF_SIMULATIONS):
    #initialize simulation
    mainGrid = [] #grid of agents positions 
    for row in range(0,GRID_SIZE):
        mainGrid.append([None]*GRID_SIZE) # init with none
        
    personList = [] #list of agents
    for agents in range(0,POP_SIZE):
        posFound = False
        xPos = random.randrange(GRID_SIZE)
        yPos = random.randrange(GRID_SIZE)
        
        while(not posFound):
            if(mainGrid[xPos][yPos] == None): #if a person does not exist on that tile
                temp = person(xPos, yPos) #temp so both personList and mainGrid reference same object
                personList.append(temp)
                mainGrid[xPos][yPos] = temp
                posFound = True
            else: #else try a random new position
                xPos = random.randrange(GRID_SIZE)
                yPos = random.randrange(GRID_SIZE)
                
    
    for agent in random.sample(personList,int (POP_SIZE*INFECTED_PER)): # infect INFECTED_PER of init populations
        agent.infected = True
        agent.infectedTime = random.randrange(0,DEVELOPMENT_CYCLES)
    
    
    print(f"simulation {simulation+1}/{NUM_OF_SIMULATIONS}")
    cycleInfected = [POP_SIZE*INFECTED_PER] #init with initial infection numbers
    cycleDead = [0]
    cycleRecovered = [0]
    
    for cycle in range(NUM_OF_CYCLES):
        if(cycle%10 == 0):
             print(f'{cycle}/{NUM_OF_CYCLES}')
        
        cycleInfected.append(0)
        cycleDead.append(0)
        cycleRecovered.append(0)
        
        aboveCap = True if cycleInfected[-1] > CAPACITY else False
        for agent in personList: # run infect for each agent
            agent.infectOthers(INFECT_RATE, INFECTION_RADIUS)
            agent.stepSickness(True if cycleInfected[-2] > CAPACITY else False)
            
        for agent in personList: # move each agent and add up infected
            agent.moveRand()
            if(agent.infected):
                cycleInfected[-1] += 1
            elif(agent.dead):
                cycleDead[-1] +=1
            elif(agent.recovered):
                cycleRecovered[-1] +=1
                
        if(cycleDead[-1] + cycleRecovered[-1] >= POP_SIZE) or (cycleInfected[-1] == 0): # if all members of the population are removed or no more infected exist stop the sim
            break
    
    maxCycle = max(maxCycle, len(cycleInfected))
    print(len(cycleInfected))
    #print(cycleInfected)
    infectedListList.append(cycleInfected.copy())
    #print(cycleDead)
    deadListList.append(cycleDead.copy())
    #print(cycleRecovered)
    recoveredListList.append(cycleRecovered.copy())
    
infectedAverage = [0]*maxCycle
deadAverage = [0]*maxCycle
recoveredAverage = [0]*maxCycle
#average simulations
for (i,d,r) in itertools.zip_longest(infectedListList, deadListList, recoveredListList): #sum values for infected, dead and recoverd
    for index in range(maxCycle):
        if (len(i) > index):
            infectedAverage[index] += i[index]
        else:
            infectedAverage[index] += i[-1] #if end of list use last element
        
        if (len(d) > index):
            deadAverage[index] += d[index]
        else:
            deadAverage[index] += d[-1] #if end of list use last element
        
        if (len(i) > index):
            recoveredAverage[index] += r[index]
        else:
            recoveredAverage[index] += r[-1] #if end of list use last element

averageDiv = lambda x : x/NUM_OF_SIMULATIONS #lambda function for dividing the added totals to get average
infectedAverage = list(map(averageDiv, infectedAverage))
deadAverage = list(map(averageDiv, deadAverage))
recoveredAverage = list(map(averageDiv, recoveredAverage))

plt.figure(figsize=(20,10))
#plt.xscale("log")
#plt.yscale("log")
plt.stackplot(np.arange(0,maxCycle),infectedAverage,deadAverage,recoveredAverage, labels=["Infected", "Dead", "Recovered"])
plt.legend(loc='upper left')
plt.ylim(top=POP_SIZE)
plt.xlim(right=maxCycle-1)
plt.title(f"Average of {NUM_OF_SIMULATIONS} Simulations with {POP_SIZE} Agents in a {GRID_SIZE}X{GRID_SIZE} Grid \nInfection Rate:{INFECT_RATE}  Infection Radius:{INFECTION_RADIUS}  Time To Recover:{DEVELOPMENT_CYCLES} Cycles \nDeathrate:{DEATH_RATE}  Chance to Move: {CHANCE_TO_MOVE} \nHealthcare Capacity:{CAPACITY}  Death Rate Multiplier When Above Capacity:{DEATH_MUL_WHEN_OVER_CAP}", fontsize=32)
plt.xlabel("Time (Cycles)", fontsize = 30)
plt.ylabel("Number of Infected", fontsize = 30)
plt.savefig("tempPlot.png",bbox_inches='tight')
