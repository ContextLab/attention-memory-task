from psychopy import visual, event, core, data, gui, logging

vers = '1.2'
#replaced draw() with setAutoDraw()
#response can be given upon stimulus presentation 
# cms to degrees


globalClock = core.Clock()



info = {} #a dictionary
info['participant'] = ''
dlg = gui.DlgFromDict(info)

if not dlg.OK:
    core.quit()


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
    logging.console.setLevel(logging.DEBUG)
else:
    fullscr = True
    logging.console.setLevel(logging.WARNING)


logDat = logging.LogFile (logFileName, filemode='w', level = logging.DATA)



win = visual.Window([1024,768], fullscr = fullscr, monitor = 'testMonitor', units='deg')


fixation = visual.Circle(win, size = 0.5, lineColor = 'white', fillColor = 'lightGrey')
cue = visual.ShapeStim(win, vertices = [[-1.5,-1], [-1.5,1], [1.5,0]], lineColor = 'red', fillColor = 'salmon')
probe = visual.ImageStim(win, size = 2, pos = [5, 0], image = None, mask = 'gauss',color = 'green')# 'size' is 3xSD for gauss, pos = [300, 0], #we'll change this later


conditions = data.importConditions('K:\conditions2.csv') #import conditions from file 

trials = data.TrialHandler(trialList = conditions, nReps = 1)

thisExp = data.ExperimentHandler(name='Posner', version= vers, #not needed, just handy
    extraInfo = info, #the info we created earlier
    dataFileName = filename, # using our string with data/name_date
    )

thisExp.addLoop(trials)


respClock = core.Clock()
for thisTrial in trials:
    
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

