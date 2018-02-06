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

# pres trials per run (total_trials % 8 == 0)
num_trials = 4

# catch trials per run
catch = 0 #num_trials/4

# invalid trials per run
invalid = 4

total_trials = num_trials + catch

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
global_clock = core.Clock()
logging.setDefaultClock(global_clock) 


# initialize info dictionary
info = {}

# experimenter inputs subject info
info['participant'] = ''
info['run'] = ''
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()
    
# get date
info['date_str']= data.getdate_str()[0:11]

# subject directory
dir_name = info['participant'] + '_' + info['date_str']
dir_check = 'data/' + dir_name

# if subject directory does not exist, create it
if not os.path.exists(dir_check):
    os.makedirs(dir_check)

# file_names 
file_name = "data/" + dir_name + '/'+ info['participant'] + '_' + info['run'] + '_' + info['date_str'] 
log_file_name = "data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['date_str']

#instructions 
#split up to stay within max line length; EP
instruct_practice = 'Practice about to start. Press RETURN when ready'

instruct_exp = 'PART 1: \n\n On each trial, you will be cued to covertotal_trialsy attend a face image (F) or ' \
               'location image (L) on the right or left of the screen. ' \
               '\n\n Your eyes will stay fixated at center-screen. ' \
               '\n\n After each presentation, a circle will display. ' \
               '\n\n You will immediately press a button indicating if ' \
               'the circle appears screen-left (1) or screen-right (3). ' \
               '\n\n Press RETURN to begin'

instruct_mem = 'PART 2: \n\n On each trial you will see one image appear, followed by a rating scale. ' \
               '\n\n When the scale appears, you will quickly rate (in one second) the image as being familiar ' \
               '(1), slightotal_trialsy familiar (2), slightotal_trialsy unfamiliar (3) or unfamiliar (4). ' \
               '\n\n Press RETURN to begin'

instruct_thanks = 'Thank you for your participation!'

#logging\debugging preferences
#fullscr = True; EP


log_data = logging.LogFile (log_file_name+'_log', filemode='w', level = logging.DATA)
log_data = logging.LogFile (log_file_name+'_2.log', filemode='w', level = logging.EXP)

# create window
win = visual.Window([1024,768], fullscr = True, monitor = 'test_monitor', units='deg', color = 'black')

# obtain frame rate
frame_rate_secs = win.getActualFrameRate()
print(frame_rate_secs)

# set stim display durations

# fixation
info['fix_frames'] = int(round(.8 * frame_rate_secs))

# R/L cue 
info['cue_frames'] = int(round(.5 * frame_rate_secs))
info['cue_pause_frames'] = int(round(.01* frame_rate_secs))

# probe_frames == composite images
info['probe_frames'] = int(round(3.0 * frame_rate_secs))
info['probe_pos'] = 8
info['cue_pos'] = info['probe_pos']
info['mem_frames'] = int(round(1 * frame_rate_secs))
info['mem_pause_frames'] = int(round(1 *frame_rate_secs))

#create objects
#split up lines to stay within max line length; EP 
fixation = visual.TextStim(win=win, ori=0, name='fixation', text='+', font='Arial', 
                           height = 2, color='light_grey', colorSpace='rgb', opacity=1, depth=0.0)

catch_f = visual.TextStim(win=win, ori=0, name='catch_f', text='Male (L) or Female (R)?', 
                         font='Arial', height = 2, color='light_grey', colorSpace='rgb', opacity=1, depth=0.0)

catch_h = visual.TextStim(win=win, ori=0, name='catch_f', text='Indoor (L) or Outdoor (R)?', font='Arial', 
                         height = 2, color='light_grey', colorSpace='rgb', opacity=1, depth=0.0)

probe = visual.Circle(win, size = fixation_size, line_color = 'white', fill_color = 'light_grey')

cue_vertices_r = [[-.8,-.5], [-.8,.5], [.8,0]]
cue_right = visual.ShapeStim(win, vertices = cue_vertices_r, line_color = 'white', fill_color = 'light_grey')

cue_vertices_l = [[.8,-.5], [.8,.5], [-.8,0]]
cue_left = visual.ShapeStim(win, vertices = cue_vertices_l, line_color = 'white', fill_color = 'light_grey')

#split up lines to stay within max line length; EP
cue_cat_1 = visual.TextStim(win=win, ori=0, name='cue_cat_1', text=cat1[0], font='Arial', 
                            height = 2, color='light_grey', colorSpace='rgb', opacity=1, depth=0.0, pos = [0,2])

cue_cat_2 = visual.TextStim(win=win, ori=0, name='cue_cat_2', text=cat2[0], font='Arial', 
                            height = 2, color='light_grey', colorSpace='rgb', opacity=1, depth=0.0, pos = [0,2])

#cue = visual.Circle(win, size = cue_size, line_color = 'white', fill_color = 'light_grey')
instruction = visual.TextStim(win)

#######################################################

resp_clock = core.Clock()

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

def load_mem_p(pickles):
    ''' returns list of memory pkl dicts'''
    mem = []
    for f in pickles:
        if f.endswith('mem_items.pkl'):
            mem.append(f)
            
    mem_dicts = []
    for mem_f in mem:
        with open(mem_f, 'rb') as fp:
            x=pickle.load(fp)
        mem_dicts.append(x)
    mem_dict = concat_dicts(mem_dicts)
    return mem_dict
    
def load_prev_p(pickles):
    '''returns list of prev pkl files'''
    prev = []
    for f in pickles:
        if f.endswith('previous_items.pkl'):
            prev.append(f)
            
    prev_dicts = []
    for prev_f in prev:
        with open(prev_f, 'rb') as fp:
            y=pickle.load(fp)
        prev_dicts.append(y)
    prev_dict = concat_dicts(prev_dicts)
    return prev_dict
    
############ EXP FUNCTIONS ############################

def show_instructions(text, acceptedKeys = None):
    """Presents text and waits for acceptedKeys"""
    
    # Set and display text
    instruction.setText(text)
    instruction.draw()
    win.flip()
    
    # Wait for response 
    response = event.waitKeys(keyList=acceptedKeys)
    if response == 'escape':
        core.quit()


def pres_block( pickle_name, prev_stim, run, loop = object, saveData = True, test=False):

    """Runs experimental block and saves reponses if requested"""
    
    trial_clock = core.Clock()
    
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
    right_left= ['cue_L']*(int(num_trials/2)) + ['cue_R']*(int(num_trials/2))
    face_house= ([cat1[0]]*(int(num_trials/4)) + [cat2[0]]*(int(num_trials/4)))*2
    validity_0 = [[1]*(int(invalid/4)) + [0]*(int((num_trials-invalid)/4))]*4
    validity = [item for sublist in validity_0 for item in sublist]
    
    #cue_tuples is a list of tuples (one per trial) specifying: catch/no, R/L attend, F/H attend
    cue_tuples_0 = zip(right_left, face_house, validity) #, attention)
    cue_tuples = random.sample(cue_tuples_0, len(cue_tuples_0))
    
    # make catch params
    right_left_catch = ['cue_L']*(catch/2) + ['cue_R']*(catch/2)
    face_house_catch = [cat1[0]]*(catch/4) + [cat2[0]]*(catch/4)
    face_house_catch = face_house_catch*2
    validity_catch = [0]*catch
    
    #cue_tuples is a list of tuples (one per trial) specifying: catch/no, R/L attend, F/H attend
    catch_tuples_0 = zip(right_left_catch, face_house_catch, validity_catch) #, attention)
    catch_tuples = random.sample(catch_tuples_0, len(catch_tuples_0))
    
    #list to tell when catch and when regular trial
    catches_0 = num_trials*[0] + catch*[1]
    catches = random.sample(catches_0, len(catches_0))
    
    trial_num = 0
    cue_tup_num = 0
    catch_num = 0
    
    for this_trial in loop:
        
        if catches[trial_num] == 0:
            params =cue_tuples[cue_tup_num]
            cue_tup_num += 1
            
        else:
            params = catch_tuples[catch_num]
            catch_num += 1
            
        if params[0] == 'cue_R':
            cue = cue_right
        else:
            cue = cue_left
            
        if params[1]=='F':
            cue_cat = cue_cat_1
        else:
            cue_cat = cue_cat_2
                
                
        cue.setPos( [0, 0] )
        
        #show fixation
        fixation.setAutoDraw(True)
        for frame_n in range(info['fix_frames']):
            win.flip()
        
        #show cue
        fixation.setAutoDraw(False)
        cue.setAutoDraw(True)
        cue_cat.setAutoDraw(True, )
        for frame_n in range(info['cue_frames']):
            win.flip()
        cue.setAutoDraw(False) 
        cue_cat.setAutoDraw(False)
        fixation.setAutoDraw(True)
        
        #pause
        for frame_n in range(info['cue_pause_frames']):
            fixation.setAutoDraw(True)
            win.flip()
        
        # [3] RUN TRIAL
        all_items_0 = os.listdir(dir1)
        all_items = []
        
        for entry in all_items_0:
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
        probe1.setPos([info['probe_pos'], 0])
        probe2.setPos([-info['probe_pos'], 0])
        
        # save cued and uncued images
        if (cue == cue_right):
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
        win.callOnFlip(resp_clock.reset)
        event.clearEvents()
        for frame_n in range(info['probe_frames']):
            if frame_n == 0:
                resp_clock.reset()
            win.flip()
        probe1.setAutoDraw(False)
        probe2.setAutoDraw(False)
        fixation.setAutoDraw(False)
        
        #clear screen
        win.flip()
        
        
        resp = None
        rt = None
        
        #split line to stay within max line length; EP
        probe = visual.TextStim(win=win, ori=0, name='fixation', text='o', font='Arial', height = 2, color='light_grey', 
                                colorSpace='rgb', opacity=1, depth=0.0)
        
        # set attention probe location
        if cue == cue_right and params[2] == 0:
            position = info['probe_pos']
        elif cue == cue_left and params[2] == 1:
            position = info['probe_pos']
        else:
            position = -info['probe_pos']
            
        probe.setPos( [position, 0] )

        # display probe, break if response recorded
        fixation.setAutoDraw(True)
        probe.setAutoDraw(True)
        win.callOnFlip(resp_clock.reset)
        event.clearEvents()
        for frame_n in range(info['probe_frames']):
            
            # fixation.setAutoDraw(True)
            # probe.setAutoDraw(True)
            if frame_n == 0:
                resp_clock.reset()
                keys = event.getKeys(keyList = ['enter'])
            if len(keys) > 0:
                resp = keys[0]
                rt = resp_clock.getTime()
                break
                    
            # clear screen
            win.flip()
            probe.setAutoDraw(False)
            #fixation.setAutoDraw(False)

            # if no response, wait w/ blank screen until response
            if (resp == None and test == False):
                keys = event.waitKeys(keyList = ['1', '3'])
                resp = keys[0]
                rt = resp_clock.getTime()
            
            elif (resp == None and test == True):
                rt = 'test'
                
            # KZ : reaction times saved below
            #      currentotal_trialsy saves two groups: cued/uncued
            #      change to save into four:
            #           2 (cued/uncued) * 2 (right/left) = 4
            
        if ( cue == cue_right and position > 1 ):
            cued_RT.append(rt)
            
        else:
            uncued_RT.append(rt)
            #target_right.append(0)
            #clear screen upon response
            win.flip()
            
                
        win.flip()
        trial_num+=1
    
    previous_items['cued'] = cued
    previous_items['uncued'] = uncued
    previous_items['uncued_RT'] = uncued_RT
    previous_items['cued_RT'] = cued_RT
    previous_items['run_time'] = trial_clock.getTime()
    previous_items['cue_tuples'] =cue_tuples
    
    # KZ : code below saves data in pickle format
    #      if we save data per trial (we should, even if not needed; want a record of everything subject saw at each moment) 
    #      we will need to incorporate trial # and subject # into file_names
    
    #      should set up experiment so that if subject is on run 1, it makes new directory for subject
    #      other runs --> check for directory --> if exists, save out to subj dir --> if not exist..warning? create subject direcotry?
    
    with open(pickle_name, 'wb') as f:
        pickle.dump(previous_items, f)

    fixation.setAutoDraw(False)

def mem_block( conds, current_pickle, prev_stim ):
    trial_clock = core.Clock()
    
    # start dictionary to store data
    mem_task = {}
    
    # file_name for saved output
    pickle_name_mem = "data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['date_str'] + 'mem_items.pkl'
    
    #KZ : reads in the pickle file
    with open(current_pickle,'rb') as fp:
        current_list = pickle.load(fp)
        #previous_items_full = [val for sublist in previous_items for val in sublist]
    
    
    # empty list to store items used in memory task
    previous_mem = []
    all_ratings = []
    
    
    for each in conds:
        
        all_items_0 = os.listdir(stim_dir1) + os.listdir(stim_dir2)
        all_items = []
        
        for entry in all_items_0:
            if fnmatch.fnmatch(entry,'*.jpg'):
                all_items.append(entry)

        # EDIT
        # first, parse the previous_mem cued and uncued into separate image file names
        # additionally split into attended cat, attended side, cue Left, cue Right, etc
        
        # split the composite images into indivudal image file_names
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
        
        mem_probe = visual.ImageStim( win, mem, size=probe_size )
        mem_probe.setPos( [0, 0] )
        
        win.callOnFlip(resp_clock.reset)
        event.clearEvents()
        
        for frame_n in range(info['mem_frames']):
            mem_probe.setAutoDraw(True)
            if frame_n == 0:
                resp_clock.reset()
            win.flip()
        mem_probe.setAutoDraw(False)
        win.flip()
        
#        for frame_n in range(info['mem_frames']):
#            mem_probe.setAutodraw(True)
#        win.flip()
        
        
        ##################
        
        ##KIRSTEN ORIGINAL##
        #split line to stay within max line length; EP
        rating_scale = visual.rating_scale( win, low = 1, high = 4, labels = ['familiar','unfamiliar'], 
                                            singleClick=True, scale = None, pos = [0,0], acceptPreText='-', 
                                            maxTime=2.0, disappear=False)
        
        event.getKeys(keyList=None)
        while rating_scale.noResponse == True:
            rating_scale.setAutoDraw(True)
            win.flip()
        rating_scale.setAutoDraw(False)
        choice_history = rating_scale.getHistory()
        
        for frame_n in range(info['mem_pause_frames']):
            fixation.setAutoDraw(True)
            win.flip()
        fixation.setAutoDraw(False)
        
        # KZ : need to save decisionTime and choice_history
        #      need to save decisionTime grouped by type of image subj is responding to
        #      10 image types : 1 (seen) * 2 (attended/unattended) * 2 (displayed right/left) * 2 (face/house)  +  1 (unseen) * 2 (face/house)
        
        previous_mem.append(mem_file)
        all_ratings.append(choice_history)
        
    mem_task['ratings'] = all_ratings
    mem_task['images'] = previous_mem
    mem_task['run_time'] = trial_clock.getTime()
    mem_task['total_iters'] = conds
    #mem_task['choiceHist']=all_ratings
    
    with open(pickle_name_mem, 'wb') as f:
        pickle.dump(mem_task, f)


######### RUN EXPERIMENT ###########

# for specified # of reps, run presentation then memory
for rep in range(0,repetitions):
    
    #pickle_name for use in both functions
    #split line to stay within max line length; EP
    pickle_name = "data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + \
                  info['date_str'] + 'previous_items.pkl'
    
    # if pkl files exist from previous runs, load the data
    prev_runs = []
    files = get_files(dir_check)
    if len(files)>0:
        mem_dict = load_mem_p(files)
        prev_dict = load_prev_p(files)
        
        prev_stim = mem_dict['images']
        prev_stim.append(prev_dict['cued'])
        prev_stim.append(prev_dict['uncued'])
        prev_stim = [val for sublist in prev_stim for val in sublist]
    else:
        prev_stim = []
    
    #prev_stim list of all images shown BEFORE THIS TRIAL
    
    # load trials
    trials = data.TrialHandler(trialList = [{}]*total_trials, nReps = 1)

    #presentation task
    show_instructions(text = instruct_exp, acceptedKeys = ['1','2','3','4','return', 'escape'])
    pres_block(pickle_name, prev_stim, info['run'], trials, test=False)
#   pres_block(info['run'], trials)

    #memory task
    show_instructions(text = instruct_mem, acceptedKeys = ['1','2','3','4','return'])
    mem_block(range(0,num_trials*8), pickle_name, prev_stim)
    
    info['run'] = str(int(info['run'])+1)
    
#closing message
show_instructions(text = instruct_thanks, acceptedKeys = ['1','2','3','4','return'])
