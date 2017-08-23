from psychopy import visual, event, core, data, gui, logging
import random
import os

vers = '2.0'
#modified 1.3
#removed gaussian probe, replaced with text/images on either side


#clocks
globalClock = core.Clock()
logging.setDefaultClock(globalClock)


#experiment parameters and participant info

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
info['cueFrames'] = 60
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
DEBUG = True
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

#cue = visual.ShapeStim(win, vertices = cueVertices, lineColor = 'red', fillColor = 'black')



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

#import conditions from csv
conditions = data.importConditions('conditions.csv') 
trials = data.TrialHandler(trialList = conditions, nReps = 1)

#practice run (same length as full run
conditionsPractice = data.importConditions('conditions.csv')
practice = data.TrialHandler(trialList = conditionsPractice, nReps = 1)

thisExp = data.ExperimentHandler(name='Posner', version= vers, #not needed, just handy
    extraInfo = info, #the info we created earlier
    dataFileName = filename, # using our string with data/name_date
    )
thisExp.addLoop(trials)
thisExp.addLoop(practice)

respClock = core.Clock()
def runBlock(loop = object, saveData = True):
    """Runs a loop for an experimental block and saves reposnes if requested"""
    for thisTrial in loop:
        #generate csv file
        #filename = "data/" + info['participant'] + "_" + info['dateStr'] + "conds" + trial#
            #populate csv with desired params
            #add number of the trial to the filename
            #CHRISTINA
        
        
        img1_file = random.choice(os.listdir("/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Faces"))
        img1 = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Faces/'+img1_file
        
        img2_file = random.choice(os.listdir("/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects"))
        img2 = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects/'+img2_file
        
        probe1 = visual.ImageStim(win, img1, size=probeSize) #pos=(5, 0), size=probeSize)
        probe2 = visual.ImageStim(win, img2, size=probeSize) #pos=(-5, 0), size=probeSize)
        
        resp = None
        rt = None
        
        probe1.setPos( [thisTrial['probeX'], 0] )
        probe2.setPos( [-thisTrial['probeX'], 0] )
        
        #trandomize side of cue
        #random boolean --> if True, cue right
        if bool(random.getrandbits(1)) == True:
            cue.setPos(5)
        else:
            cue.setPos(-5)
        
        fixation.setAutoDraw(True)
        for frameN in range(info['fixFrames']):
            win.flip()
    
        cue.setAutoDraw(True)
        for frameN in range(info['cueFrames']):
            win.flip()
        cue.setAutoDraw(False)
        
        probe1.setAutoDraw(True)
        probe2.setAutoDraw(True)
        win.callOnFlip(respClock.reset)
        event.clearEvents()
        for frameN in range(info['probeFrames']):
            if frameN == 0:
                respClock.reset()
            keys = event.getKeys(keyList = ['left','right','escape'])
            if len(keys) > 0:
                resp = keys[0]
                rt = respClock.getTime()
                break
            win.flip()
        probe1.setAutoDraw(False)
        probe2.setAutoDraw(False)
        fixation.setAutoDraw(False)
    
        #clear screen
        win.flip()
    
#        if resp == None:
#            
#            keys = event.waitKeys(keyList = ['left','right','escape'])
#            resp = keys[0]
#            rt = respClock.getTime()
        
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


#show instructions and run practice and experimental trials
showInstructions(text = instructPractice, acceptedKeys = ['return', 'escape'])
runBlock(practice, saveData = False)
showInstructions(text = instructExp, acceptedKeys = ['return', 'escape'])
runBlock(trials)
showInstructions(text = instructThanks, acceptedKeys = ['return'])