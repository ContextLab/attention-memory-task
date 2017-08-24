from psychopy import visual, event, core, data, gui, logging

vers = 1.1 
#precise timing


#info = {} #a dictionary
#info['fixTime'] = 0.5 # seconds
#info['cueTime'] = 0.2
#info['probeTime'] = 0.2

globalClock = core.Clock()



info = {} #a dictionary
info['participant'] = ''
dlg = gui.DlgFromDict(info)

if not dlg.OK:
    core.quit()

#info['fixTime'] = 1.0 # seconds
#info['cueTime'] = 1.0
#info['probeTime'] = 1.0
#info['dateStr'] = data.getDateStr()

info['fixFrames'] = 60 
info['cueFrames'] = 60
info['probeFrames'] = 60
info['dateStr'] = data.getDateStr()

filename = "K:\data/" + info['participant'] + "_" + info['dateStr'] 

logging.setDefaultClock(globalClock)

logFileName = "K:\data/" + info['participant'] + "_" + info['dateStr'] + '.log'





DEBUG = True
if DEBUG:
    fullscr = False
    logging.console.setLevel(logging.INFO)
else:
    fullscr = True
    logging.console.setLevel(logging.WARNING)


logDat = logging.LogFile (logFileName, filemode='w', level = logging.DATA)
win = visual.Window([1024,768], fullscr = fullscr, units='pix')


fixation = visual.Circle(win, size = 5, lineColor = 'white', fillColor = 'lightGrey')
cue = visual.ShapeStim(win, vertices = [[-30,-20], [-30,20], [30,0]], lineColor = 'red', fillColor = 'salmon')
probe = visual.ImageStim(win, size = 80,image = None, mask = 'gauss',color = 'green')# 'size' is 3xSD for gauss, pos = [300, 0], #we'll change this later


conditions = data.importConditions('K:\conditions.csv') #import conditions from file 

trials = data.TrialHandler(trialList = conditions, nReps = 1)

thisExp = data.ExperimentHandler(name='Posner', version='1.1', #not needed, just handy
    extraInfo = info, #the info we created earlier
    dataFileName = filename, # using our string with data/name_date
    )

thisExp.addLoop(trials)


respClock = core.Clock()
for thisTrial in trials:
    probe.setPos( [thisTrial['probeX'], 0] )
    cue.setOri( thisTrial['cueOri'] )
    
    for frameN in range(info['fixFrames']):
        fixation.draw()
        win.flip()


    for frameN in range(info['cueFrames']):
        cue.draw()
        win.flip()

    for frameN in range(info['probeFrames']):
        fixation.draw()
        probe.draw()
        if frameN == 0:
            respClock.reset()
        win.flip()
    
    win.flip()

    keys = event.waitKeys(keyList = ['left','right','escape'])
    resp = keys[0] #take first response
    rt = respClock.getTime()
    
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



