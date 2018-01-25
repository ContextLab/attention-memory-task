from psychopy import visual, event, core, data, gui, logging
import random
import os
import pickle

vers = '2.0'
DEBUG = False

####### PARAMS + SUB INFO #########

# clocks
globalClock = core.Clock()
logging.setDefaultClock(globalClock)

# objects sizes
fixationSize = 0.5
probeSize = 7
cueSize = 1

# nuber of runs
repetitions = 1

# info dictionary
info = {}
info['participant'] = ''
info['run'] = ''
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()
info['dateStr']= data.getDateStr()[0:11]

# subject directory
dir_name = info['participant'] + '_' + info['dateStr']
dir_check = 'data/' + dir_name

# if subject directory does not exist, create it
if not os.path.exists(dir_check):
    os.makedirs(dir_check)

# filenames 
filename = "data/" + dir_name + '/'+ info['participant'] + '_' + info['run'] + '_' + info['dateStr'] 
logFileName = "data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['dateStr']

# stim dirs
dir1 = '../../stim/composites'

#instructions 
instructPractice = 'Practice about to start. Press RETURN when ready'
instructExp = 'Experiment about to start. Press RETURN when ready'
instructMem = 'Memory task about to start. Press RETURN when ready'
instructThanks = 'Thank you for your participation!'

#logging\debugging preferences
if DEBUG:
    fullscr = False
    logging.console.setLevel(logging.DEBUG)
else:
    fullscr = True
    logging.console.setLevel(logging.WARNING)

logDat = logging.LogFile (logFileName+'_log', filemode='w', level = logging.DATA)
logDat = logging.LogFile (logFileName+'_2.log', filemode='w', level = logging.EXP)


# create window
win = visual.Window([1024,768], fullscr = True, monitor = 'testMonitor', units='deg', color = 'black')

# obtain frame rate
fRate_secs = win.getActualFrameRate()
print(fRate_secs)

# set stim display durations
info['fixFrames'] = int(round(1.5 * fRate_secs))
info['cueFrames'] = int(round(.5 * fRate_secs))
info['cuePauseFrames'] = int(round(.2* fRate_secs))
info['probeFrames'] = int(round(.2 * fRate_secs))
info['cuePos'] = 10
info['probePos'] = 10
info['memFrames'] = int(round(2 * fRate_secs))
#info['ratingFrames'] = int(round(1 *  fRate_secs))
#^^change this in the rating settings
info['memPauseFrames'] = int(round(2 *fRate_secs))

#create objects
fixation = visual.Circle(win, size = fixationSize, lineColor = 'white', fillColor = 'lightGrey')
cueVerticesR = [[-.8,-.5], [-.8,.5], [.8,0]]
cueRight = visual.ShapeStim(win, vertices = cueVerticesR, lineColor = 'white', fillColor = 'lightGrey')
cueVerticesL = [[.8,-.5], [.8,.5], [-.8,0]]
cueLeft = visual.ShapeStim(win, vertices = cueVerticesL, lineColor = 'white', fillColor = 'lightGrey')
#cue = visual.Circle(win, size = cueSize, lineColor = 'white', fillColor = 'lightGrey')
instruction = visual.TextStim(win)

#import conditions from csv
#should be an even number
conditions = data.importConditions('conditions_short.csv') 
#
# KZ : ^ideally run independent of csv file (low priority)
#      currently, csv gives us only # of trials
#
trials = data.TrialHandler(trialList = conditions, nReps = 1)

##########################################################

#define practice run (same length as full run)
conditionsPractice = data.importConditions('conditions_short.csv')
practice = data.TrialHandler(trialList = conditionsPractice, nReps = 1)

thisExp = data.ExperimentHandler(name='Posner', version= vers, #not needed, just handy
    extraInfo = info, #the info we created earlier
    dataFileName = filename, # using our string with data/name_date
    )

thisExp.addLoop(trials)
thisExp.addLoop(practice)

respClock = core.Clock()


####### FILE LOAD FUNCTIONS #########

def get_files(dir_name):
    '''returns all subj pkl files'''
    files = [dir_name + '/' + f for f in os.listdir(dir_name) if f.endswith('.pkl')]
    return files
    
def concat_dicts(dicts):
    big_dict = {}
    for k in dicts[0]:
        big_dict[k] = [d[k] for d in dicts]
    return big_dict

def load_memP(pickles):
    ''' returns list of memory pkl dicts'''
    mem = []
    for f in pickles:
        if f.endswith('mem_items.pkl'):
            mem.append(f)
            
    mem_dicts = []
    for memf in mem:
        with open(memf, 'rb') as fp:
            x=pickle.load(fp)
        mem_dicts.append(x)
    mem_dict = concat_dicts(mem_dicts)
    return mem_dict
    
def load_prevP(pickles):
    '''returns list of prev pkl files'''
    prev = []
    for f in pickles:
        if f.endswith('previous_items.pkl'):
            prev.append(f)

            
    prev_dicts = []
    for prevf in prev:
        with open(prevf, 'rb') as fp:
            y=pickle.load(fp)
        prev_dicts.append(y)
    prev_dict = concat_dicts(prev_dicts)
    return prev_dict
    
############ EXP FUNCTIONS ############

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


def presBlock( pickle_name, prev_stim, run, loop = object, saveData = True, test=False):

    """Runs a loop for an experimental block and saves reponses if requested"""
    
    trialClock = core.Clock()
    
    previous_items = {}
    cued = []
    uncued = []
    cue_right = []
    
    reaction_time={}
    cued_RT = []
    uncued_RT = []
    
    trial_count = 0
    
    for thisTrial in loop:
        
        trial_count += 1
        
        # [1] CUE ONE SIDE
        
        #randomize side
        if bool(random.getrandbits(1)) == True:
            cue = cueRight
            cue_right.append(1)

        else:
            cue = cueLeft
            cue_right.append(0)
            
        cue.setPos( [0, 0] )
        
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
            fixation.setAutoDraw(True)
            win.flip()
        
        # [2] DETERMINE TRIAL TYPE (STANDARD vs CATCH)
        #trialType = random.choice([1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2])

        # [3] RUN TRIAL
        all_items = os.listdir(dir1)+os.listdir(dir2)
        available_items = [x for x in all_items if (x not in cued and x not in uncued and x not in prev_stim)]
            
        #select and load image stimuli at random
        #select and load image stimuli at random
        img1_file = random.choice([x for x in available_items if x in os.listdir(dir1)])
        img1 = dir1+img1_file
        img2_file = img1_file
           
        while (img2_file == img1_file):
            img2_file = random.choice([x for x in available_items if x in os.listdir(dir2)])
            
        img2 = dir2 + img2_file
        
        #assign images as probes (w/ sizes, locations, etc.)
        probe1 = visual.ImageStim(win, img1, size=probeSize, name='Probe1') 
        probe2 = visual.ImageStim(win, img2, size=probeSize, name='Probe2') 

        if random.choice([1,2]) == 1:
            pos = info['probePos']
        else:
            pos = -info['probePos']
        
        probe1.setPos([pos, 0])
        probe2.setPos([-pos, 0])
        
        # save cued and uncued images
        if (cue == cueRight and pos > 0) :
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
        
            #KZ : code below from the original repo
            #     maybe useful format for saving
            #####################################
#                trials.addData('resp', resp)
#                trials.addData('rt', rt)
#                trials.addData('corr', corr)
#                thisExp.nextEntry()
            #####################################
                
             
            
        #if trialType == 1: #if catch trial (30% chance):
                #pause
                
        #for frameN in range(info['cuePauseFrames']):
            #win.flip()

        resp = None
        rt = None
        
        probe = visual.TextStim(win=win, ori=0, name='fixation', text='+', font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)
        
        # 70% chance attn cross on cued side
        if cue == cueRight:
            position = random.choice( [-10, -10, -10, 10, 10, 10, 10, 10, 10, 10] )
        else:
            position = random.choice( [10, 10, 10, -10, -10, -10, -10, -10, -10, -10] )
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
                keys = event.getKeys(keyList = ['enter'])
                if len(keys) > 0:
                    resp = keys[0]
                    rt = respClock.getTime()
                    break
                    
            #clear screen
            win.flip()
            probe.setAutoDraw(False)
            fixation.setAutoDraw(False)

            #if no response, wait w/ blank screen until response
            if (resp == None and test==False):
                keys = event.waitKeys(keyList = ['1', '3'])
                resp = keys[0]
                rt = respClock.getTime()
            
            elif (resp == None and test == True):
                rt = 'test'
                
            # KZ : reaction times saved below
            #      currently saves two groups: cued/uncued
            #      change to save into four:
            #           2 (cued/uncued) * 2 (right/left) = 4
            
        if ( cue == cueRight and position > 1 ):
            cued_RT.append(rt)
            
        else:
            uncued_RT.append(rt)
            #target_right.append(0)
            #clear screen upon response
            win.flip()
            

            #KZ : code below from the original repo
            #     maybe useful format for saving
            #####################################
#                trials.addData('resp', resp)
#                trials.addData('rt', rt)
#                trials.addData('corr', corr)
#                thisExp.nextEntry()
            #####################################
                
        win.flip()
    
    previous_items['cued'] = cued
    previous_items['uncued'] = uncued
    previous_items['uncued_RT'] = uncued_RT
    previous_items['cued_RT'] = cued_RT
    previous_items['cued_RT'] = cued_RT
    previous_items['cue_Right'] = cue_right
    previous_items['run_time'] = trialClock.getTime()
    previous_items['total_iters'] = trial_count
    
    # KZ : code below saves data in pickle format
    #      if we save data per trial (we should, even if not needed; want a record of everything subject saw at each moment) 
    #      we will need to incorporate trial # and subject # into filenames
    
    #      should set up experiment so that if subject is on run 1, it makes new directory for subject
    #      other runs --> check for directory --> if exists, save out to subj dir --> if not exist..warning? create subject direcotry?
    
    with open(pickle_name, 'wb') as f:
        pickle.dump(previous_items, f)





def memBlock( conds, current_pickle, prev_stim ):
    trialClock = core.Clock()
    
    # start dictionary to store data
    mem_task = {}
    
    # filename for saved output
    pickle_name_mem = "data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['dateStr'] + 'mem_items.pkl'
    
    #KZ : reads in the pickle file
    with open(current_pickle,'rb') as fp:
        current_list = pickle.load(fp)
        #previous_items_full = [val for sublist in previous_items for val in sublist]
    
    
    # empty list to store items used in memory task
    previous_mem = []
    all_ratings = []
    
    
    for each in conds:
        
        all_items = os.listdir(dir1)+os.listdir(dir2)
        available_attended = [x for x in current_list['cued'] if x not in previous_mem]
        available_unattended = [x for x in current_list['uncued'] if x not in previous_mem]
        available_random = [x for x in all_items if (x not in previous_mem and x not in current_list['cued'] and x not in current_list['uncued'] and x not in prev_stim)]
        
        #select and load image stimuli 
        #options = [ 1, 2, 3]
        options = []
        if len(available_attended)>0:
            options.append(1)
        if len(available_unattended)>0:
            options.append(2)
        if len(available_random)>0:
            options.append(3)
        
        # if we decide not to show all images then will want to show Rpres and Lpres with same frequency
        type = random.choice(options)
        
        if type == 1:
            mem_file = random.choice(available_attended)
        elif type == 2:
            mem_file = random.choice(available_unattended)
        else:
            mem_file = random.choice(available_random)
        
        #change to if statement to get rid of pesky errors
        try:
            #Type = 'Faces'
            #mem = '/Users/kirstenziman/Documents/GitHub/P4N2016/stim/OddballLocStims/'+Type+'/'+mem_file
            mem = dir1 + mem_file
            memProbe = visual.ImageStim( win, mem, size=probeSize )
            memProbe.setPos( [0, 0] )
            
        except:
            #Type = 'Houses'
            #mem = '/Users/kirstenziman/Documents/GitHub/P4N2016/stim/OddballLocStims/'+Type+'/'+mem_file
            mem = dir2 + mem_file
            memProbe = visual.ImageStim( win, mem, size=probeSize )
            memProbe.setPos( [0, 0] )

        
        win.callOnFlip(respClock.reset)
        event.clearEvents()

        for frameN in range(info['memFrames']):
            memProbe.setAutoDraw(True)
            if frameN == 0:
                respClock.reset()
            win.flip()
        memProbe.setAutoDraw(False)
        win.flip()
        
#        for frameN in range(info['memFrames']):
#            memProbe.setAutodraw(True)
#        win.flip()
        
        
        ##################
        
        ##KIRSTEN ORIGINAL##
        ratingScale = visual.RatingScale( win, low = 1, high = 4, labels = ['viewed before','new image'], singleClick=True, scale = None, pos = [0,0], acceptPreText='-', maxTime=2.0, disappear=False)

        while ratingScale.noResponse == True:
            ratingScale.setAutoDraw(True)
            win.flip()
        ratingScale.setAutoDraw(False)
        choiceHistory = ratingScale.getHistory()

        for frameN in range(info['memPauseFrames']):
            fixation.setAutoDraw(True)
            win.flip()
        fixation.setAutoDraw(False)

        # KZ : need to save decisionTime and choiceHistory
        #      need to save decisionTime grouped by type of image subj is responding to
        #      10 image types : 1 (seen) * 2 (attended/unattended) * 2 (displayed right/left) * 2 (face/house)  +  1 (unseen) * 2 (face/house)
        
        previous_mem.append(mem_file)
        all_ratings.append(choiceHistory)
    
    mem_task['ratings'] = all_ratings
    mem_task['images'] = previous_mem
    mem_task['run_time'] = trialClock.getTime()
    mem_task['total_iters'] = conds
    #mem_task['choiceHist']=all_ratings

    with open(pickle_name_mem, 'wb') as f:
        pickle.dump(mem_task, f)
        
        
        
######### RUN EXPERIMENT ###########

# for specified number of reps, run presentation them memory
for rep in range(0,repetitions):
    
    #pickle_name for use in both functions
    pickle_name = "data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['dateStr'] + 'previous_items.pkl'
    
    # if pkl files exist from previous runs, load the data
    prev_runs = []
    files = get_files(dir_check)
    if len(files)>0:
        mem_dict = load_memP(files)
        prev_dict = load_prevP(files)
        
        prev_stim = mem_dict['images']
        prev_stim.append(prev_dict['cued'])
        prev_stim.append(prev_dict['uncued'])
        prev_stim = [val for sublist in prev_stim for val in sublist]
    else:
        prev_stim = []
    #prev_stim list of all images shown BEFORE THIS TRIAL
        
    # load trials
    conditions = data.importConditions('conditions_short.csv') 
    trials = data.TrialHandler(trialList = conditions, nReps = 1)

    #presentation task
    showInstructions(text = instructExp, acceptedKeys = ['1','2','3','4','return', 'escape'])
    presBlock(pickle_name, prev_stim, info['run'], trials, test=False)
#    presBlock(info['run'], trials)

    #memory task
    showInstructions(text = instructMem, acceptedKeys = ['1','2','3','4','return'])
    memBlock(range(0,len(conditions)*3), pickle_name, prev_stim)
    
    info['run'] = str(int(info['run'])+1)

#closing message
showInstructions(text = instructThanks, acceptedKeys = ['1','2','3','4','return'])