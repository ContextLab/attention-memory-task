from psychopy import visual, event, core, data, gui, logging
import random
import os

vers = '2.0'

####### PARAMS + SUB INFO #########

#clocks
globalClock = core.Clock()
logging.setDefaultClock(globalClock)

#objects sizes
fixationSize = 0.5
probeSize = 7
cueSize = 1

#dictionary
info = {}
info['participant'] = ''
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()
info['fixFrames'] = 60
info['cueFrames'] = 10
info['cuePauseFrames'] = 10
info['probeFrames'] = 60
info['dateStr'] = data.getDateStr()

#filenames
filename = "data/" + info['participant'] + "_" + info['dateStr'] 
logFileName = "data/" + info['participant'] + "_" + info['dateStr'] + '.log'

#instructions
instructPractice = 'Practice about to start. Press RETURN when ready'
instructExp = 'Experiment about to start. Press RETURN when ready'
instructThanks = 'Thank you for your participation!'

#logging\debugging preferences
DEBUG = False

if DEBUG:
    fullscr = False
    logging.console.setLevel(logging.DEBUG)
else:
    fullscr = True
    logging.console.setLevel(logging.WARNING)

logDat = logging.LogFile (logFileName, filemode='w', level = logging.DATA)


# create window
win = visual.Window([1024,768], fullscr = fullscr, monitor = 'testMonitor', units='deg')

#create objects
fixation = visual.Circle(win, size = fixationSize, lineColor = 'white', fillColor = 'lightGrey')
cue = visual.Circle(win, size = cueSize, lineColor = 'white', fillColor = 'lightGrey')
instruction = visual.TextStim(win)

#exogenous cue (red arrow)
#cue = visual.ShapeStim(win, vertices = cueVertices, lineColor = 'red', fillColor = 'black')

### KZ : eliminate need for csv or auto generate here ######

#import conditions from csv
conditions = data.importConditions('conditions.csv') 
trials = data.TrialHandler(trialList = conditions, nReps = 1)

##########################################################

#define practice run (same length as full run)
conditionsPractice = data.importConditions('conditions.csv')
practice = data.TrialHandler(trialList = conditionsPractice, nReps = 1)

thisExp = data.ExperimentHandler(name='Posner', version= vers, #not needed, just handy
    extraInfo = info, #the info we created earlier
    dataFileName = filename, # using our string with data/name_date
    )

thisExp.addLoop(trials)
thisExp.addLoop(practice)

respClock = core.Clock()


####### EXP FUNCTIONS #########

def showInstructions(text, acceptedKeys = None):
    """Presents a question and waits for acceptedKeys"""
    
    # Set and display text
    instruction.setText(text)
    instruction.draw()
    win.flip()
    
    # Wait for response and return it
    response = event.waitKeys(keyList=acceptedKeys)
    #return response
    if response == 'escape':
        core.quit()

def runBlock(loop = object, saveData = True):


####### RUN EXPERIMENT #########
    """Runs a loop for an experimental block and saves reposnes if requested"""
    for thisTrial in loop:
        
        # [1] CUE ONE SIDE
        
        #randomize side
        if bool(random.getrandbits(1)) == True:
            cue.setPos(5)
        else:
            cue.setPos(-5)
        
        #show fixation
        fixation.setAutoDraw(True)
        for frameN in range(info['fixFrames']):
            win.flip()
        
        #show cue
        cue.setAutoDraw(True)
        for frameN in range(info['cueFrames']):
            win.flip()
        cue.setAutoDraw(False) 
        
        #pause
        for frameN in range(info['cuePauseFrames']):
            win.flip()
        
        
        # [2] DETERMINE TRIAL TYPE (IMAGE vs CATCH)
        trialType = random.choice([1, 1, 1, 2, 2, 2, 2, 2, 2, 2])

        # [3] RUN TRIAL
        if trialType == 2: #image trial (70% chance)
            
            #select and load image stimuli at random
            img1_file = random.choice(os.listdir("/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Faces"))
            img1 = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Faces/'+img1_file
            
            img2_file = random.choice(os.listdir("/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects"))
            img2 = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects/'+img2_file
            
            #assign images as probes (w/ sizes, locations, etc.)
            probe1 = visual.ImageStim(win, img1, size=probeSize) #pos=(5, 0), size=probeSize)
            probe2 = visual.ImageStim(win, img2, size=probeSize) #pos=(-5, 0), size=probeSize)
            
            probe1.setPos( [thisTrial['probeX'], 0] )
            probe2.setPos( [-thisTrial['probeX'], 0] )
            
            #response and reaction time variables
            resp = None
            rt = None
            
            #display probes simultaneously
            probe1.setAutoDraw(True)
            probe2.setAutoDraw(True)
            win.callOnFlip(respClock.reset)
            event.clearEvents()
            for frameN in range(info['probeFrames']):
                if frameN == 0:
                    respClock.reset()
                win.flip()
            probe1.setAutoDraw(False)
            probe2.setAutoDraw(False)
            fixation.setAutoDraw(False)
        
            #clear screen
            win.flip()
            
            #save data
            if saveData == True:
                if thisTrial['probeX']>0 and resp=='right':
                    corr = 1
                elif thisTrial['probeX']<0 and resp=='left':
                    corr = 1
                elif resp=='escape':
                    corr = None
                    trials.finished = True
                else:
                    corr = 0
            
                trials.addData('resp', resp)
                trials.addData('rt', rt)
                trials.addData('corr', corr)
                thisExp.nextEntry()
                
        else: #catch trial (30% chance)
            resp = None
            rt = None
            
            #assign probe (circle), with position
            probe = visual.Circle(win, size = cueSize, lineColor = 'white', fillColor = 'lightGrey')
            position = random.choice( [-8,8] )
            probe.setPos( [position, 0] )
            
            #display probe, break is response recorded
            fixation.setAutoDraw(False)
            probe.setAutoDraw(True)
            win.callOnFlip(respClock.reset)
            event.clearEvents()
            for frameN in range(info['probeFrames']):
                fixation.setAutoDraw(True)
                probe.setAutoDraw(True)
                if frameN == 0:
                    respClock.reset()
                keys = event.getKeys(keyList = ['left','right','escape'])
                if len(keys) > 0:
                    resp = keys[0]
                    rt = respClock.getTime()
                    break
        
            #clear screen
            win.flip()
            probe.setAutoDraw(False)
            fixation.setAutoDraw(False)

            #if no response, wait w/ blank screen until response
            if resp == None:
                
                keys = event.waitKeys(keyList = ['left','right','escape'])
                resp = keys[0]
                rt = respClock.getTime()
                
            #clear screen upon response
            win.flip()
            

            #save data
            if saveData == True: 
                if thisTrial['probeX']>0 and resp=='right':
                    corr = 1
                elif thisTrial['probeX']<0 and resp=='left':
                    corr = 1
                elif resp=='escape':
                    corr = None
                    trials.finished = True
                else:
                    corr = 0
            
                trials.addData('resp', resp)
                trials.addData('rt', rt)
                trials.addData('corr', corr)
                thisExp.nextEntry()

#RUN PRACTICE TRIAL               
#show instructions and run practice and experimental trials
#showInstructions(text = instructPractice, acceptedKeys = ['return', 'escape'])
#runBlock(practice, saveData = False)

#RUN TRIAL
showInstructions(text = instructExp, acceptedKeys = ['return', 'escape'])
runBlock(trials)
showInstructions(text = instructThanks, acceptedKeys = ['return'])