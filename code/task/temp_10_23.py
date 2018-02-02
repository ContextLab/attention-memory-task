from psychopy import visual, event, core, data, gui, logging
import random
import os
import pickle
import fnmatch

vers = '2.0'

####### PARAMS + SUB INFO ########################

# edit the parameters in this section ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# runs
repetitions = 1

# pres trials per run (tL % 8 == 0)
num_trials = 4

# catch trials per run
catch = 0 #num_trials/4

# invalid trials per run
invalid = 4

tL = num_trials + catch

# stim dirs
dir1 = '/Users/kirstenziman/Desktop/COMP_IMAGES/' # Overlays
stim_dir1 = '/Users/kirstenziman/Desktop/faces/' # Face
stim_dir2 = '/Users/kirstenziman/Desktop/places/' # House


# code uses first letter of this string as the category cue
cat1 = 'Face'
cat2 = 'Location'

# objects sizes
fixation_size = 0.5
probe_size = 7
cue_size = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# clocks
globalClock = core.Clock()
logging.setDefaultClock(globalClock) 


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

#instructions 
instructPractice = 'Practice about to start. Press RETURN when ready'
instructExp = 'In this task, you will be cued to attend to either a face or place image on the right or left of the screen while maintaining fixation at the center of the screen. After each image presentation period, a small cross will display. You will press a button to indicate if the cross is on the left or right of the screen as soon as it appears. Press RETURN when ready'
instructMem = 'Memory task about to start. Press RETURN when ready'
instructThanks = 'Thank you for your participation!'

#logging\debugging preferences
fullscr = True

logDat = logging.LogFile (logFileName+'_log', filemode='w', level = logging.DATA)
logDat = logging.LogFile (logFileName+'_2.log', filemode='w', level = logging.EXP)

# create window
win = visual.Window([1024,768], fullscr = True, monitor = 'testMonitor', units='deg', color = 'black')

# obtain frame rate
fRate_secs = win.getActualFrameRate()
print(fRate_secs)

# set stim display durations

# fixation
info['fixFrames'] = int(round(.8 * fRate_secs))

# R/L cue 
info['cueFrames'] = int(round(.5 * fRate_secs))
info['cuePauseFrames'] = int(round(.01* fRate_secs))

# probeFrames == composite images
info['probeFrames'] = int(round(3.0 * fRate_secs))
info['probePos'] = 8
info['cuePos'] = info['probePos']
info['memFrames'] = int(round(1 * fRate_secs))
info['memPauseFrames'] = int(round(1 *fRate_secs))

#create objects
fixation = visual.TextStim(win=win, ori=0, name='fixation', text='+', font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

catchF = visual.TextStim(win=win, ori=0, name='catchF', text='Male (L) or Female (R)?', font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)
catchH = visual.TextStim(win=win, ori=0, name='catchF', text='Indoor (L) or Outdoor (R)?', font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)
probe = visual.Circle(win, size = fixation_size, lineColor = 'white', fillColor = 'lightGrey')

cueVerticesR = [[-.8,-.5], [-.8,.5], [.8,0]]
cueRight = visual.ShapeStim(win, vertices = cueVerticesR, lineColor = 'white', fillColor = 'lightGrey')

cueVerticesL = [[.8,-.5], [.8,.5], [-.8,0]]
cueLeft = visual.ShapeStim(win, vertices = cueVerticesL, lineColor = 'white', fillColor = 'lightGrey')

cueCat1 = visual.TextStim(win=win, ori=0, name='cuecat1', text=cat1[0], font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0, pos = [0,2])
cueCat2 = visual.TextStim(win=win, ori=0, name='cuecat2', text=cat2[0], font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0, pos = [0,2])

#cue = visual.Circle(win, size = cue_size, lineColor = 'white', fillColor = 'lightGrey')
instruction = visual.TextStim(win)

#######################################################

respClock = core.Clock()

####### FILE LOAD FUNCTIONS ###########################

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
    
############ EXP FUNCTIONS ############################

def showInstructions(text, acceptedKeys = None):
    """Presents text and waits for acceptedKeys"""
    
    # Set and display text
    instruction.setText(text)
    instruction.draw()
    win.flip()
    
    # Wait for response 
    response = event.waitKeys(keyList=acceptedKeys)
    if response == 'escape':
        core.quit()


def presBlock( pickle_name, prev_stim, run, loop = object, saveData = True, test=False):

    """Runs experimental block and saves reponses if requested"""
    
    trialClock = core.Clock()
    
    previous_items = {}
    cued = []
    uncued = []
    cue_right = []
    
    reaction_time={}
    cued_RT = []
    uncued_RT = []
    
    trial_count = 0
    
    # generate conditions
    # When using AFNI jittering, will create all for whole exp outside of loop (prior, even, to running?)
    # maybe make csv from afni
    RL = ['cue_L']*(int(num_trials/2)) + ['cue_R']*(int(num_trials/2))
    FH = ([cat1[0]]*(int(num_trials/4)) + [cat2[0]]*(int(num_trials/4)))*2
    validity0 = [[1]*(int(invalid/4)) + [0]*(int((num_trials-invalid)/4))]*4
    validity = [item for sublist in validity0 for item in sublist]
    
    # cueTuples is a list of tuples (one per trial) specifying: catch/no, R/L attend, F/H attend
    cueTuples0 = zip(RL, FH, validity) #, attention)
    cueTuples = random.sample(cueTuples0, len(cueTuples0))
    
    # make catch params
    RL_catch = ['cue_L']*(catch/2) + ['cue_R']*(catch/2)
    FH_catch = [cat1[0]]*(catch/4) + [cat2[0]]*(catch/4)
    FH_catch = FH_catch*2
    validity_catch = [0]*catch
    
    # cueTuples is a list of tuples (one per trial) specifying: catch/no, R/L attend, F/H attend
    catchTuples0 = zip(RL_catch, FH_catch, validity_catch) #, attention)
    catchTuples = random.sample(catchTuples0, len(catchTuples0))
    
    #list to tell when catch and when regular trial
    catches0 = num_trials*[0] + catch*[1]
    catches = random.sample(catches0, len(catches0))
    
    trialnum = 0
    cueTupNum = 0
    catchNum = 0
    
    for thisTrial in loop:
        
        if catches[trialnum] == 0:
            params = cueTuples[cueTupNum]
            cueTupNum += 1
            
        else:
            params = catchTuples[catchNum]
            catchNum += 1
            
        if params[0] == 'cue_R':
            cue = cueRight
        else:
            cue = cueLeft
            
        if params[1]=='F':
            cueCat = cueCat1
        else:
            cueCat = cueCat2
                
                
        cue.setPos( [0, 0] )
        
        #show fixation
        fixation.setAutoDraw(True)
        for frameN in range(info['fixFrames']):
            win.flip()
        
        #show cue
        fixation.setAutoDraw(False)
        cue.setAutoDraw(True)
        cueCat.setAutoDraw(True, )
        for frameN in range(info['cueFrames']):
            win.flip()
        cue.setAutoDraw(False) 
        cueCat.setAutoDraw(False)
        fixation.setAutoDraw(True)
        
        #pause
        for frameN in range(info['cuePauseFrames']):
            fixation.setAutoDraw(True)
            win.flip()
        
        # [3] RUN TRIAL
        all_items0 = os.listdir(dir1)
        all_items = []
        
        for entry in all_items0:
            if fnmatch.fnmatch(entry,'*.jpg'):
                all_items.append(entry)
                
        available_items = [x for x in all_items if (x not in cued and x not in uncued and x not in prev_stim)]
            
        #select and load image stimuli at random
        img1_file = random.choice([x for x in available_items if x in os.listdir(dir1)])
        img1 = dir1+img1_file
        img2_file = img1_file
           
        while (img2_file == img1_file):
            img2_file = random.choice([x for x in available_items if x in os.listdir(dir1)])
            
        img2 = dir1 + img2_file
        
        #assign images as probes (w/ sizes, locations, etc.)
        probe1 = visual.ImageStim(win, img1, size=probe_size, name='Probe1')
        probe2 = visual.ImageStim(win, img2, size=probe_size, name='Probe2')
        
        # Probe1 displays right, Probe 2 displays left
        probe1.setPos([info['probePos'], 0])
        probe2.setPos([-info['probePos'], 0])
        
        # save cued and uncued images
        if (cue == cueRight):
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
        
        
        resp = None
        rt = None
        
        probe = visual.TextStim(win=win, ori=0, name='fixation', text='o', font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)
        
        # set attention probe location
        if cue == cueRight and params[2] == 0:
            position = info['probePos']
        elif cue == cueLeft and params[2] == 1:
            position = info['probePos']
        else:
            position = -info['probePos']
            
        probe.setPos( [position, 0] )

        # display probe, break if response recorded
        fixation.setAutoDraw(True)
        probe.setAutoDraw(True)
        win.callOnFlip(respClock.reset)
        event.clearEvents()
        for frameN in range(info['probeFrames']):
            
            # fixation.setAutoDraw(True)
            # probe.setAutoDraw(True)
            if frameN == 0:
                respClock.reset()
                keys = event.getKeys(keyList = ['enter'])
            if len(keys) > 0:
                resp = keys[0]
                rt = respClock.getTime()
                break
                    
            # clear screen
            win.flip()
            probe.setAutoDraw(False)
            #fixation.setAutoDraw(False)

            # if no response, wait w/ blank screen until response
            if (resp == None and test == False):
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
            
                
        win.flip()
        trialnum+=1
    
    previous_items['cued'] = cued
    previous_items['uncued'] = uncued
    previous_items['uncued_RT'] = uncued_RT
    previous_items['cued_RT'] = cued_RT
    previous_items['run_time'] = trialClock.getTime()
    previous_items['cue_tuples'] = cueTuples
    
    # KZ : code below saves data in pickle format
    #      if we save data per trial (we should, even if not needed; want a record of everything subject saw at each moment) 
    #      we will need to incorporate trial # and subject # into filenames
    
    #      should set up experiment so that if subject is on run 1, it makes new directory for subject
    #      other runs --> check for directory --> if exists, save out to subj dir --> if not exist..warning? create subject direcotry?
    
    with open(pickle_name, 'wb') as f:
        pickle.dump(previous_items, f)

    fixation.setAutoDraw(False)

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
        
        all_items0 = os.listdir(stim_dir1) + os.listdir(stim_dir2)
        all_items = []
        
        for entry in all_items0:
            if fnmatch.fnmatch(entry,'*.jpg'):
                all_items.append(entry)

        # EDIT
        # first, parse the previous_mem cued and uncued into separate image file names
        # additionally split into attended cat, attended side, cue Left, cue Right, etc
        
        # split the composite images into indivudal image filenames
        current_list['cued'] = [words for segments in current_list['cued'] for words in segments.split('_')]
        current_list['uncued'] = [words for segments in current_list['uncued'] for words in segments.split('_')]
        
        current_list['cued_1'] = current_list['cued'][0::2]
        current_list['cued_1'] = [s + '.jpg' for s in current_list['cued_1']]
        current_list['cued_2'] = current_list['cued'][1::2]
        
        current_list['uncued_1'] = current_list['uncued'][0::2]
        current_list['uncued_1'] = [s + '.jpg' for s in current_list['uncued_1']]
        current_list['uncued_2'] = current_list['uncued'][1::2]
        
        available_attended_stim1 = [x for x in current_list['cued_1'] if x not in previous_mem]
        available_attended_stim2 = [x for x in current_list['cued_2'] if x not in previous_mem]
        
        available_unattended_stim1 = [x for x in current_list['uncued_1'] if x not in previous_mem]
        available_unattended_stim2 = [x for x in current_list['uncued_2'] if x not in previous_mem]
        
        available_random = [x for x in all_items if 
                            (x not in previous_mem 
                            and x not in current_list['cued_1'] 
                            and x not in current_list['cued_2']
                            and x not in current_list['uncued_1']
                            and x not in current_list['uncued_2']
                            and x not in prev_stim)]
        
        #select and load image stimuli 
        #options = [ 1, 2, 3]
        options = []
        if len(available_attended_stim1)>0:
            options.append(1)
        if len(available_attended_stim2)>0:
            options.append(4)
        if len(available_unattended_stim1)>0:
            options.append(2)
        if len(available_unattended_stim2)>0:
            options.append(5)
        if len(available_random)>0:
            options.append(3)
        
        # if we decide not to show all images then will want to show Rpres and Lpres with same frequency
        type = random.choice(options)
        
        if type == 1:
            mem_file = random.choice(available_attended_stim1)
            mem_dir = stim_dir1
        elif type == 4:
            mem_file = random.choice(available_attended_stim2)
            mem_dir = stim_dir2
        elif type == 2:
            mem_file = random.choice(available_unattended_stim1)
            mem_dir = stim_dir1
        elif type == 5:
            mem_file = random.choice(available_unattended_stim2)
            mem_dir = stim_dir2
        else:
            mem_file = random.choice(available_random)
            
            if os.path.isfile(stim_dir1+mem_file):
                mem_dir = stim_dir1
            else: 
                mem_dir = stim_dir2
        
        
        #change to if statement to get rid of pesky errors
        #try:
        #Type = 'Faces'
        #mem = '/Users/kirstenziman/Documents/GitHub/P4N2016/stim/OddballLocStims/'+Type+'/'+mem_file
        mem = mem_dir + mem_file
        
        memProbe = visual.ImageStim( win, mem, size=probe_size )
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
        
        event.getKeys(keyList=None)
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

# for specified # of reps, run presentation then memory
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
    trials = data.TrialHandler(trialList = [{}]*tL, nReps = 1)

    #presentation task
    showInstructions(text = instructExp, acceptedKeys = ['1','2','3','4','return', 'escape'])
    presBlock(pickle_name, prev_stim, info['run'], trials, test=False)
#   presBlock(info['run'], trials)

    #memory task
    showInstructions(text = instructMem, acceptedKeys = ['1','2','3','4','return'])
    memBlock(range(0,num_trials*8), pickle_name, prev_stim)
    
    info['run'] = str(int(info['run'])+1)
    
#closing message
showInstructions(text = instructThanks, acceptedKeys = ['1','2','3','4','return'])