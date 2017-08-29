from psychopy import visual, event, core, data, gui, logging
import random
import os
import pickle

vers = '2.0'

#need to change saving out attended and unattended stim info in case of multiple trials

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
info['run'] = ''
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()
info['fixFrames'] = 60
info['cueFrames'] = 10
info['cuePauseFrames'] = 10
info['probeFrames'] = 60
info['cuePos'] = 10
info['probePos'] = 10
info['memFrames'] = 60

info['dateStr'] = data.getDateStr()


#filenames
filename = "data/" + info['participant'] + "_" + info['run'] + '_' + info['dateStr'] 
logFileName = "data/" + info['participant'] + "_" + info['run'] + '_' + info['dateStr'] + '.log'
pickle_name = 'data/' + info['participant'] + '_' + info['run'] + '_' + info['dateStr'] + 'previous_items.pkl'

#instructions
instructPractice = 'Practice about to start. Press RETURN when ready'
instructExp = 'Experiment about to start. Press RETURN when ready'
instructMem = 'Memory task about to start. Press RETURN when ready'
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
#cue = visual.Polygon(win, edges = 4, lineColor = 'white', ori = 40, size  = [5, 5] )
cue = visual.Circle(win, size = cueSize, lineColor = 'white', fillColor = 'lightGrey')
instruction = visual.TextStim(win)

#exogenous cue (red arrow)
#cue = visual.ShapeStim(win, vertices = cueVertices, lineColor = 'red', fillColor = 'black')

### KZ : eliminate need for csv or auto generate here ######

#import conditions from csv
conditions = data.importConditions('/Users/kirstenziman/Documents/GitHub/P4N2016/conditions.csv') 
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


def presBlock( run, loop = object, saveData = True ):


####### RUN EXPERIMENT #########
    """Runs a loop for an experimental block and saves reponses if requested"""
    
    previous_items = {}
    cued = []
    uncued = []
    
    for thisTrial in loop:
        
        # [1] CUE ONE SIDE
        
        #randomize side
        if bool(random.getrandbits(1)) == True:
            cue_position = info['cuePos']
        else:
            cue_position = -info['cuePos']
            
        cue.setPos( [cue_position, 0] )
        
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
            
            all_items = os.listdir("/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects")
            available_items = [x for x in all_items if (x not in cued and x not in uncued)]
            
            #select and load image stimuli at random
            img1_file = random.choice(available_items)
            img1 = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects/'+img1_file
            img2_file = img1_file
           
            while (img2_file == img1_file):
                img2_file = random.choice(available_items)
            
            img2 = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects/'+img2_file
            
            #assign images as probes (w/ sizes, locations, etc.)
            probe1 = visual.ImageStim(win, img1, size=probeSize) #pos=(5, 0), size=probeSize)
            probe2 = visual.ImageStim(win, img2, size=probeSize) #pos=(-5, 0), size=probeSize)
            
            probePos = random.choice([1,2])
            
            if probePos == 1:
                pos1 = info['probePos']
                pos2 = -info['probePos']
                
            else:
                pos1 = -info['probePos']
                pos2 = info['probePos']
             
            probe1.setPos([pos1, 0])
            probe2.setPos([pos2, 0])
             
            if pos1 == cue_position :
                cued.append(img1_file)
                uncued.append(img2_file)
            else:
                cued.append(img2_file)
                uncued.append(img1_file)
            
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
#            if saveData == True:
#                if thisTrial['probeX']>0 and resp=='right':
#                    corr = 1
#                elif thisTrial['probeX']<0 and resp=='left':
#                    corr = 1
#                elif resp=='escape':
#                    corr = None
#                    trials.finished = True
#                else:
#                    corr = 0
            
#                trials.addData('resp', resp)
#                trials.addData('rt', rt)
#                trials.addData('corr', corr)
#                trials.addData('img1', img1_file)
#                trials.addData('img2', img2_file)
#                thisExp.nextEntry()
                
             
            
        else: #catch trial (30% chance)
            resp = None
            rt = None
            
            
            #assign probe (circle), with position
            #probe = visual.Circle(win, size = cueSize, lineColor = 'white', fillColor = 'lightGrey')
            probe = visual.TextStim(win=win, ori=0, name='fixation', text='+', font='Arial', height = 5.5, color='black', colorSpace='rgb', opacity=1, depth=0.0)
            position = random.choice( [-10,10] )
            probe.setPos( [position, 0] )
            
            #display probe, break is response recorded
            fixation.setAutoDraw(True)
            probe.setAutoDraw(True)
            win.callOnFlip(respClock.reset)
            event.clearEvents()
            for frameN in range(info['probeFrames']):
                #fixation.setAutoDraw(True)
                #probe.setAutoDraw(True)
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
                
        win.flip()
    
    previous_items['cued'] = cued
    previous_items['uncued'] = uncued
    
    with open(pickle_name, 'wb') as f:
        pickle.dump(previous_items, f)


def memBlock( conds, previous_items ):
    
    with open(previous_items,'rb') as fp:
        previous_items = pickle.load(fp)
        #previous_items_full = [val for sublist in previous_items for val in sublist]
    
    previous_mem = []
    
    for each in conds:
        
        all_items = os.listdir("/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects")
        available_attended = [x for x in previous_items['cued'] if x not in previous_mem]
        available_unattended = [x for x in previous_items['uncued'] if x not in previous_mem]
        available_random = [x for x in all_items if (x not in previous_mem and (x not in previous_items['cued'] and x not in previous_items['uncued']))]
        
        #select and load image stimuli 
        
        options = [ 1, 1, 1, 2, 2, 2, 3, 3, 3]
        type = random.choice(options)
        
        if type == 1:
            mem_file = random.choice(available_attended)
        elif type == 2:
            mem_file = random.choice(available_unattended)
        else:
            mem_file = random.choice(available_random)
            
        mem = '/Users/kirstenziman/Documents/GitHub/P4N2016/OddballLocStims/Objects/'+mem_file
        memProbe = visual.ImageStim( win, mem, size=probeSize )
        memProbe.setPos( [0, 0] )

        win.callOnFlip(respClock.reset)
        event.clearEvents()
        memProbe.setAutoDraw(True)
        for frameN in range(info['probeFrames']):
            if frameN == 0:
                respClock.reset()
            win.flip()
        memProbe.setAutoDraw(False)
        win.flip()
        
#        for frameN in range(info['memFrames']):
#            memProbe.setAutodraw(True)
#        win.flip()
        
        ratingScale = visual.RatingScale( win, low = 1, high = 5, markerStart = 3, leftKeys = '1', rightKeys = '2', acceptKeys = 'return', labels = ['viewed before','new image'], scale = None, pos = [0,0])
        
        #item = "maybe this will display?"
        
        while ratingScale.noResponse:
            #item.draw()
            ratingScale.draw()
            win.flip()
        rating = ratingScale.getRating()
        decisionTime = ratingScale.getRT()
        choiceHistory = ratingScale.getHistory()
        
        previous_mem.append(mem_file)

#RUN PRACTICE TRIAL               
#show instructions and run practice and experimental trials
#showInstructions(text = instructPractice, acceptedKeys = ['return', 'escape'])
#runBlock(practice, saveData = False)


######### RUN EXPERIMENT ###########


#presentation task
showInstructions(text = instructExp, acceptedKeys = ['return', 'escape'])
presBlock(info['run'], trials)

#memory task
showInstructions(text = instructMem, acceptedKeys = ['return'])
memBlock(range(0,len(conditions)), pickle_name)
#pickle_name = 'data/' + info['participant'] + '_' + info['run'] + '_' + info['dateStr'] + 'previous_items.pkl'

#closing message
showInstructions(text = instructThanks, acceptedKeys = ['return'])