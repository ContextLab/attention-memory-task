from psychopy import visual, event, core, data, gui, logging

vers = '1.3'
#practice and instructions added
#trial loop defined as function
#sizes defined on top

#clocks
globalClock = core.Clock()
logging.setDefaultClock(globalClock)


#experiment parameters and participant info

#objects sizes
fixationSize = 0.5
cueVertices = [[-1.5,-1], [-1.5,1], [1.5,0]]
probeSize = 2

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
filename = "K:\data/" + info['participant'] + "_" + info['dateStr'] 
logFileName = "K:\data/" + info['participant'] + "_" + info['dateStr'] + '.log'


#instructions
instructPractice = 'Practice about to start. Press RETURN when ready'
instructExp = 'Experiment about to start. Press RETURN when ready'
instructThanks = 'Thank you and goodbye. We hope you enjoyed!'

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
cue = visual.ShapeStim(win, vertices = cueVertices, lineColor = 'red', fillColor = 'salmon')
probe = visual.ImageStim(win, size = probeSize, pos = [5, 0], image = None, mask = 'gauss',color = 'green')# 'size' is 3xSD for gauss, pos = [300, 0], #we'll change this later
instruction = visual.TextStim(win)


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

conditions = data.importConditions('K:\conditions2.csv') #import conditions from file 
trials = data.TrialHandler(trialList = conditions, nReps = 1)

conditionsPractice = data.importConditions('K:\conditionsPractice.csv')
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
        
        resp = None
        rt = None
        
        probe.setPos( [thisTrial['probeX'], 0] )
        cue.setOri( thisTrial['cueOri'] )
        
        fixation.setAutoDraw(True)
        for frameN in range(info['fixFrames']):
            win.flip()
    
        cue.setAutoDraw(True)
        for frameN in range(info['cueFrames']):
            win.flip()
        cue.setAutoDraw(False)
        
        probe.setAutoDraw(True)
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
        probe.setAutoDraw(False)
        fixation.setAutoDraw(False)
    
        #clear screen
        win.flip()
    
        if resp == None:
            
            keys = event.waitKeys(keyList = ['left','right','escape'])
            resp = keys[0]
            rt = respClock.getTime()
        
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