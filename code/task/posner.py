from psychopy import visual, event, core, data, gui, logging
import random
import os
import pickle
import fnmatch
import glob

vers = '2.0'

####### PARAMS + SUB INFO ########################

# edit the parameters in this section only ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# test mode
test = True

# runs
repetitions = 8

# pres trials per run (total_trials % 8 == 0)
num_trials = 10

# catch trials per run
catch = 0 # num_trials/4

# block or random
block = True

# practice runs
practice_runs = 1

# invalid trials per run
invalid = 3
total_trials = num_trials + catch

# stim dirs
dir1 = '../../stim/composites_new/' # Overlays

stim_dir1 = '../../stim/faces/' # Face
stim_dir2 = '../../stim/places/' # Scene

practice_dir = '../../stim/practice/' # Practice overlays

cue_pic1 = '../../stim/Cue/scene_icon.png' # Scene icon
cue_pic2 = '../../stim/Cue/face_icon.png' # Face icon

# categories

cat1 = 'Location'
cat2 = 'Face'

# objects sizes
fixation_size = 0.5
probe_size = 7
cue_size = 2

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# clocks
global_clock = core.Clock()
logging.setDefaultClock(global_clock)

# initialize info dictionary
info = {}

# experimenter inputs subject info
myDlg = gui.Dlg(title="Attention and Memory Experiment")
info['participant'] = ''
info['run'] = ''

# subject enters demographic info
myDlg.addField('1. age')
myDlg.addField('2. sex:', choices=['--', "Male", "Female", "Other", "No Response"])
myDlg.addField('3. Are you hispanic or latino?', choices=['--', "Yes", "No"])
myDlg.addText('')
myDlg.addText('4. Race (check all that apply):')
myDlg.addField('White', False)
myDlg.addField('Black or African American', False)
myDlg.addField('Native Hawaiian or other Pacific Islander', False)
myDlg.addField('Asian', False)
myDlg.addField('American Indian or Alaskan Native', False)
myDlg.addField('Other', False)
myDlg.addField('No Response', False)
myDlg.addText('')
myDlg.addField('5. Highest Degree Achieved:', choices = ['--', 'some high school', 'high schoool graduate', 'some college', \
'college graduate', 'some graduate training', "Master's", 'Doctorate'])
myDlg.addText('')
myDlg.addText('6. Do you have any reading impairments')
myDlg.addField('(e.g. dyslexia, uncorrected far-sightedness, etc.)', choices = ['--', "Yes", "No"])
myDlg.addText('')
myDlg.addField('7. Do you have normal color vision?', choices = ['--', "Yes", "No"])
myDlg.addText('')
myDlg.addText('8. Are you taking any medications or have you had')
myDlg.addText('any recent injuries that could')
myDlg.addField('affect your memory or attention?', choices = ['--', "Yes", "No"])
myDlg.addText('')
myDlg.addField('9. If yes to question above, describe')
myDlg.addText('')
myDlg.addText('10. How many hours of sleep did')
myDlg.addField('you get last night? (enter only a number)')
myDlg.addText('')
myDlg.addText('11. How many cups of coffee')
myDlg.addField('have you had today? (enter only a number)')
myDlg.addText('')
myDlg.addField('12. How alert are you feeling?:', choices=['--', "Very sluggish", "A little slugglish", "Neutral", "A little alert", "Very alert"])

dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()

end_data = myDlg.show() 
if myDlg.OK:
    print(end_data)
    
# get date
info['date_str']= data.getDateStr()[0:11]

# subject directory
dir_name = info['participant'] + '_' + info['date_str']
dir_check = '../../data/' + dir_name

# if subject directory does not exist, create it
if not os.path.exists(dir_check):
    os.makedirs(dir_check)

# file_names
file_name = "../../data/" + dir_name + '/'+ info['participant'] + '_' + info['run'] + '_' + info['date_str']
log_file_name = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['date_str']

# pre and post questionnaire directories
pre_name = "../../data/" + dir_name + '/'+ info['participant'] + '_' + 'pre' + '_' + info['date_str']
post_name = "../../data/" + dir_name + '/'+ info['participant'] + '_' + 'post' + '_' + info['date_str']
    
# save responses to pre questionnaire
with open(pre_name, 'wb') as f:
    pickle.dump(end_data, f)


######## INSTRUCTIONS #########

# INTRO
introduction = '\n\n Thank you for participating in this experiment! ' \
                '\n\n In the experiment, you will pay attention to specific items on the screen.' \
                '\n Then, we will test your memory for some of the items you have seen. ' \
                '\n\n Press any key to continue... ' \

# PRACTICE
instruct_pract1 = ' You will see many images like the one below.' \
                '\n You will need to pay special attention to either the FACE or SCENE. ' \
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n Press any key to continue...' \
                
instruct_pract2 = ' Let\'s practice now! \n Look straight at the image and focus as hard as you can on the FACE. ' \
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you can focus on the FACE well, press any key... ' \
                
instruct_pract3 = ' Great job! ' \
                '\n Now, focus as hard as you can on the SCENE. ' \
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you can focus on the SCENE well, press any key... ' \

instruct_pract4 = ' Next, you will see a cross and two images on the screen. ' \
                '\n\n Keep your eyes staring straight at the cross, ' \
                'but try to focus on the SCENE on the LEFT. ' \
                '\n\n Only your attention should shift, not your eyes!' \
                '\n You will not see the image perfectly clearly, just do your best, and feel free to ask questions!' \
                '\n\n Press any key to begin. ' \
                
instruct_pract5 = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you are done, press any key to continue... ' \
                
instruct_pract6 = '\n\n Great job! ' \
                '\n This time, keeping your eyes at center, try and focus on the FACE on the RIGHT.' \
                '\n\n Press any key to begin.' \

instruct_pract7 = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you are done, press any key to continue... ' \

instruct_pract8 = ' Now, you will practice ' \
                'attending to parts of images based on cue icons. ' \
                '\n\n First, you\'ll see a pair of cue icons: ' \
                '\n One arrow icon pointing left or right (< or >) ' \
                ' and one image icon (face or scene): ' \
                '\n\n\n\n\n\n After the cue icons, you will see several image pairs in a row. You\'ll attend to the SAME cued side and image part for EVERY pair.' \
                ' Remember to keep your eyes fixated on the cross! ' \
                '\n\n Press any key to begin.' \

instruct_pract9 = ' Great job, let\'s try it one more time!' \
                  '\n\n This time will be the same, but after each pair, a circle (o) will appear.' \
                  '\n When you see the circle, you should immediately press a button! ' \
                  '\n\n        If the circle appears on the LEFT, press 1 ' \
                  '\n        If the circle appears on the RIGHT, press 3 ' \
                  '\n\n Remember to respond as quickly as you can!' \
                  '\n Press any key to begin.' \

instruct_pract10 = '\n\n Finally, you will practice reporting which images you remember. ' \
                '\n You will use the following scale to rate individual images displayed on the screen: ' \
                '\n\n        (1) I definitely have not seen the image before' \
                '\n        (2) I probably have not seen the image before' \
                '\n        (3) I probably have seen the image before' \
                '\n        (4) I definitely have seen the image before' \
                '\n\n You will need to respond quickly -- you\'ll have just 2 seconds!' \
                '\n\n When you\'re ready to begin, press any key.' \

# PRESENTATION
instruct_exp = ' Now we will begin the main experiment! ' \
                'Again you will see cue icons, followed by a series of image pairs and circles (and a fixation cross).' \
                '\n\n Remember to: ' \
                '\n\n        Keep your eyes staring at the cross' \
                '\n        Shift your attention to the SAME cued side and part for EACH pair' \
                '\n        Immeditaely press 1 (Left) or 3 (Right) when you see the circle (o) ' \
                '\n\n Do you have questions? Ask them now! ' \
                '\n Otherwise, position your hand over the 1 and 3 buttons, clear your mind, and press any key to begin. ' \

instruct_exp2 = ' Feel free to take a moment to rest, if you like! ' \
                ' When you\'re ready, we will do another round with a cue, followed by image pairs and circles (o).' \
                ' \n\n Remember to: ' \
                '\n Keep your eyes staring at the cross' \
                '\n Shift your attention to the SAME cued side and part for EACH pair' \
                '\n Immeditaely press 1 (Left) or 3 (Right) when you see the circle (o) ' \
                '\n\n Press any key to begin. ' \

# MEMORY
instruct_mem = ' Now we\'re going to test your memory. ' \
                '\n Just like the practice round, you will rate single images using the following scale: ' \
                '\n\n (1) I definitely have not seen the image before' \
                '\n (2) I probably have not seen the image before' \
                '\n (3) I probably have seen the image before' \
                '\n (4) I definitely have seen the image before' \
                '\n\n You will need to make your responses quickly -- you\'ll have just 2 seconds. ' \
                ' If you aren\'t sure what to say for a particular image, make your best guess! ' \
                '\n\n Press any key to begin.' \

instruct_mem2 = ' MEMORY BLOCK. ' \
                '\n\n Press any key to begin.' \

# CLOSING
instruct_thanks = 'Thank you for your participation! ' \

#logging\debugging preferences
#fullscr = True; EP

log_data = logging.LogFile (log_file_name+'_log', filemode='w', level = logging.DATA)
log_data = logging.LogFile (log_file_name+'_2.log', filemode='w', level = logging.EXP)

# create window
win = visual.Window([1024,768], fullscr = True, monitor = 'testMonitor', units='deg', color = 'black')

# obtain frame rate
frame_rate_secs = win.getActualFrameRate()
print(frame_rate_secs)

# set stim display durations

# fixation
info['fix_frames'] = int(round(1.0 * frame_rate_secs))

# R/L cue
info['cue_frames'] = int(round(.5 * frame_rate_secs))
info['cue_pause_frames'] = int(round(0* frame_rate_secs))

# practice frames
# R/L cue
info['cue_pract_long'] = int(round(15.0 * frame_rate_secs))
info['cue_pract_short'] = int(round(3.0 * frame_rate_secs))
info['probe_frames'] = int(round(3.0 * frame_rate_secs))
info['probe_pos'] = 8
info['cue_pos'] = info['probe_pos']
info['mem_frames'] = int(round(2 * frame_rate_secs))
info['mem_pause_frames'] = int(round(1 *frame_rate_secs))

#create objects
#split up lines to stay within max line length; EP
fixation = visual.TextStim(win=win, ori=0, name='fixation', text='+', font='Arial',
                           height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

catch_f = visual.TextStim(win=win, ori=0, name='catch_f', text='Male (L) or Female (R)?',
                         font='Arial', height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

catch_h = visual.TextStim(win=win, ori=0, name='catch_f', text='Indoor (L) or Outdoor (R)?', font='Arial',
                         height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

probe = visual.Circle(win, size = fixation_size, lineColor = 'white', fillColor = 'lightGrey')

cue_right = visual.TextStim(win=win, ori=0, name='cue_right', text = '>', font='Arial',
                            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

cue_left = visual.TextStim(win=win, ori=0, name='cue_left', text='<', font='Arial',
                           height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

cue_cat_1 = visual.ImageStim(win, cue_pic1, size=cue_size, name='cue_img1')
cue_cat_2 = visual.ImageStim(win, cue_pic2, size=cue_size, name='cue_img2')
cue_cat_1.setPos([0, 2])
cue_cat_2.setPos([0, 2])

instruction = visual.TextStim(win, wrapWidth=40)

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
    '''
    input: list of pickle files
    output: list of prev pkl files
    '''

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
    return mem_dict

def load_prev_p(pickles):
    '''
    input: list of pickle files
    output: list of prev pkl files
    '''

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

########## MAKE RUN PARAMS ############################
total_runs = num_trials*repetitions

# generate conditions
# if jittering for scanner, will need to change order and timing accordingly

right_left = ['cue_L']*(int(total_runs/2)) + ['cue_R']*(int(total_runs/2))
face_house = ([cat1[0]]*(int(total_runs/4)) + [cat2[0]]*(int(total_runs/4)))*2
validity_0 = ([1]*invalid + [0]*(num_trials-invalid))
validity = random.sample(validity_0, len(validity_0))
validity = validity*total_runs

#cue_tuples is a list of tuples (one per trial) specifying: catch/no, R/L attend, F/H attend
cue_tuples_0 = zip(right_left, face_house, validity) #, attention)

if block == False :
    cue_tuples = random.sample(cue_tuples_0, len(cue_tuples_0))

else:
    cue_tuples = cue_tuples_0

# make catch params
# currently not using catch trials

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

# PRE ALLOCATE MEM ONLY IMAGES
# select out required number of composite images (runs * trials)
# avoid using these for presentation stim
# use only split singles from this list for "unseen" memory images


# IMTRACE 
# mem_only_0 --> composite images for mem only
# mem_only --> single images for mem only
mem_only_0 = [f for f in random.sample([z for z in os.listdir(dir1) if z.endswith('.jpg')],num_trials*repetitions*4)]
mem_only_1 = [words for segments in mem_only_0 for words in segments.split('_')]

mem_only_a = mem_only_1[0::2]
mem_only_a = [s + '.jpg' for s in mem_only_a]
mem_only_b = mem_only_1[1::2]

mem_only = mem_only_a + mem_only_b

############ EXP FUNCTIONS ############################

def show_instructions(text, cue_pos1 = False, cue_pos2 = False, center_image1 = False, hybrid_pair = False, center_image_end = False, acceptedKeys = None):
    """Presents text and desired images, per arguments, then waits for acceptedKeys"""
    
    # Set and display text
    instruction = visual.TextStim(win, text=text, wrapWidth=40)
    instruction.setAutoDraw(True)
    win.flip()
    
    # if cue_pos1, show icons
    if cue_pos1:
        cat_inst_1 = visual.ImageStim(win, cue_pic1, size=cue_size, name='cue_img1')
        cat_inst_2 = visual.ImageStim(win, cue_pic2, size=cue_size, name='cue_img2')
        cat_inst_2.setPos([-2.5, 0])
        cat_inst_1.setPos([2.5, 0])
        cat_inst_1.setAutoDraw(True)
        cat_inst_2.setAutoDraw(True)
        win.flip()

    # if cue_pos2, show single example icon and arrow 
    elif cue_pos2:
        cat_inst_1 = visual.ImageStim(win, cue_pic2, size=cue_size, name='cue_img2')
        cat_inst_1.setPos([0, 3])

        cue_inst_right = visual.TextStim(win=win, ori=0, name='cue_right', text='>', font='Arial', 
                            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

        cue_inst_right.setPos([0, 1])
        cue_inst_right.setAutoDraw(True)
        cat_inst_1.setAutoDraw(True)
        win.flip()
        
    elif center_image1 == True:
        center = visual.ImageStim(win, '../../stim/hybrid_1/00060931230fa_sunaaehaikpckyjsety.jpg', size = probe_size)
        center.setAutoDraw(True)
        win.flip()

    elif hybrid_pair == True:
        hybrid1 = visual.ImageStim(win, '../../stim/hybrids_2/00002940128fb_sunaaacnosloariecpa.jpg', size = probe_size)
        hybrid2 = visual.ImageStim(win, '../../stim/hybrids_2/00003941121fa_sunaaaenaoynzhoyheo.jpg', size = probe_size)
        
        hybrid1.setPos([info['probe_pos'], 0])
        hybrid2.setPos([-info['probe_pos'], 0])
        
        hybrid1.setAutoDraw(True)
        hybrid2.setAutoDraw(True)
        fixation.setAutoDraw(True)
        win.flip()
        
    else:
        win.flip()
        
    # Wait for response
    response = event.waitKeys(keyList=None)
    
    instruction.setAutoDraw(False)
    #if len(response)>0:
    if cue_pos1:
        cat_inst_1.setAutoDraw(False)
        cat_inst_2.setAutoDraw(False)
        
    if cue_pos2: 
        cat_inst_1.setAutoDraw(False)
        cue_inst_right.setAutoDraw(False)
        
    if hybrid_pair == True:
        hybrid1.setAutoDraw(False)
        hybrid2.setAutoDraw(False)
        fixation.setAutoDraw(False)
        
    if center_image1:
        center.setAutoDraw(False)

    win.flip()

def practice_block( practice_dir, practice_runs, loop = object, maxWait = 120 ):
    """Displays trials for subject to practice attending to sides and categories"""

    instr_dict =  {1: instruct_pract1, 2: instruct_pract2, 3: instruct_pract3, 4: instruct_pract4, 5: instruct_pract5, 6: instruct_pract6, 7: instruct_pract7, 8: instruct_pract8, 9:instruct_pract9, 10: instruct_pract10}
    trial_count = 1
    previously_practiced = []
    cue_pract_prev = []

    for this_trial in loop:

        # select instructions
        this_instruct = instr_dict[trial_count]
        
        # display text for practice instructions
        if trial_count in [1,2,3]:
            if trial_count == 3:
                show_instructions(text = this_instruct, center_image1=True, acceptedKeys = None)
            else:
                show_instructions(text = this_instruct, center_image1=True, acceptedKeys = None)
        elif trial_count in [5,7]:
            show_instructions(text = this_instruct, hybrid_pair=True, acceptedKeys = None)
        elif trial_count in [8]:
            show_instructions(text = this_instruct, cue_pos1=True, acceptedKeys = None)
        else:
            show_instructions(text = this_instruct, acceptedKeys = None)

        # FOR PRACTICE BLOCKS AFTER TEXT INSTRUCTION
        if trial_count == 8:
            # presentation block, w/cue, no (o) x4
            practice_trials1 = data.TrialHandler(trialList = [{}]*(4), nReps = 1)
            pract_pres1(practice_trials1)

        if trial_count == 9:
            # presentation block w/cue, w/(o) x4
            practice_trials1 = data.TrialHandler(trialList = [{}]*(4), nReps = 1)
            pract_pres2(practice_trials1)

        if trial_count == 10:
            # memory block x4
            practice_trials1 = data.TrialHandler(trialList = [{}]*(4), nReps = 1)
            pract_mem(practice_trials1)

        trial_count += 1

def pract_pres1(loop = object):
    
    trial_count = 0
    for this_trial in loop:
        cue = cue_right
        cue_cat = cue_cat_1

        cue.setPos( [0, 0] )

        if trial_count == 0 :
            cue.setAutoDraw(True)
            cue_cat.setAutoDraw(True)
            for frame_n in range(info['cue_frames']*3):
                win.flip()
            cue.setAutoDraw(False)
            cue_cat.setAutoDraw(False)
            fixation.setAutoDraw(True)

        #show fixation
        fixation.setAutoDraw(True)
        for frame_n in range(info['fix_frames']):
            win.flip()

        # [3] RUN TRIAL
        items = os.listdir('../../stim/hybrids_8_1/')

        #select and load image stimuli at random
        img1_filename = '../../stim/hybrids_8_1/'+items[trial_count*2]
        img2_filename = '../../stim/hybrids_8_1/'+items[trial_count*2 + 1]

        #assign images as probes (w/ sizes, locations, etc.)
        probe1 = visual.ImageStim(win, img1_filename, size=probe_size, name='Probe1')
        probe2 = visual.ImageStim(win, img2_filename, size=probe_size, name='Probe2')

        # Probe1 displays right, Probe 2 displays left
        probe1.setPos([info['probe_pos'], 0])
        probe2.setPos([-info['probe_pos'], 0])


        #display probes simultaneously
        probe1.setAutoDraw(True)
        probe2.setAutoDraw(True)
        for frame_n in range(info['probe_frames']):
            win.flip()
        probe1.setAutoDraw(False)
        probe2.setAutoDraw(False)
        fixation.setAutoDraw(False)

        #clear screen
        win.flip()
        
        trial_count +=1
        
    fixation.setAutoDraw(False)

def pract_pres2(loop = object):
    
    trial_count = 0
    for this_trial in loop:
        cue = cue_left
        cue_cat = cue_cat_2

        cue.setPos( [0, 0] )

        if trial_count == 0 :
            cue.setAutoDraw(True)
            cue_cat.setAutoDraw(True)
            for frame_n in range(info['cue_frames']*3):
                win.flip()
            cue.setAutoDraw(False)
            cue_cat.setAutoDraw(False)
            fixation.setAutoDraw(True)
            win.flip()


        #show fixation
        fixation.setAutoDraw(True)
        for frame_n in range(info['fix_frames']):
            win.flip()

        # [3] RUN TRIAL
        items = os.listdir('../../stim/hybrids_8_1/')

        #select and load image stimuli at random
        img1_filename = '../../stim/hybrids_8_1/'+items[trial_count*2]
        img2_filename = '../../stim/hybrids_8_1/'+items[trial_count*2 + 1]

        #assign images as probes (w/ sizes, locations, etc.)
        probe1 = visual.ImageStim(win, img1_filename, size=probe_size, name='Probe1')
        probe2 = visual.ImageStim(win, img2_filename, size=probe_size, name='Probe2')

        # Probe1 displays right, Probe 2 displays left
        probe1.setPos([info['probe_pos'], 0])
        probe2.setPos([-info['probe_pos'], 0])

        #display probes simultaneously
        probe1.setAutoDraw(True)
        probe2.setAutoDraw(True)
        for frame_n in range(info['probe_frames']):
            win.flip()
        probe1.setAutoDraw(False)
        probe2.setAutoDraw(False)
        fixation.setAutoDraw(False)

        #clear screen
        win.flip()

        #split line to stay within max line length; EP
        probe = visual.TextStim(win=win, ori=0, name='fixation', text='o', font='Arial', height = 2, color='lightGrey',
                                colorSpace='rgb', opacity=1, depth=0.0)

        # set circle position (three valid, one invalid)
        if trial_count == 2:
            position = info['probe_pos']
        else:
            position = -info['probe_pos']

        probe.setPos( [position, 0] )

        # display probe, break if response recorded
        fixation.setAutoDraw(True)
        probe.setAutoDraw(True)
        win.callOnFlip(resp_clock.reset)
        event.clearEvents()
        
        resp = None
        
        for frame_n in range(info['probe_frames']):
            if frame_n == 0:
                keys = event.getKeys(keyList = ['1','3'])
            if len(keys) > 0:
                resp = keys[0]
                break

            # clear screen
            win.flip()
            probe.setAutoDraw(False)

            # if no response, wait w/ blank screen until response
            if resp == None:
                keys = event.waitKeys(keyList = ['1', '3'])
                resp = keys[0]
                
        trial_count += 1
        
        win.flip()

    fixation.setAutoDraw(False)
    
def pract_mem(loop = object):
    
    items = os.listdir('../../stim/singles_4/')
    trial_count = 0
    
    for this_trial in loop:
        #select and load image stimuli at random
        mem = '../../stim/singles_4/'+items[trial_count]

        mem_probe = visual.ImageStim( win, mem, size=probe_size )
        mem_probe.setPos( [0, 0] )
        
        event.clearEvents()

        ##################

        ##KIRSTEN ORIGINAL##
        #split line to stay within max line length; EP
        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4',
                                            singleClick = True, pos = [0,-.42], acceptPreText = '-',
                                            maxTime=3.0, minTime=0, marker = 'triangle', showAccept=False, acceptSize=0) #disappear=True)

        #visual.RatingScale(win=win, name='rating', marker=u'triangle', size=1.0, pos=[0.0, -0.4], low=1, high=4, labels=[u''], scale=u'')


        event.getKeys(keyList = None)
        for frame_n in range(info['mem_frames']):
            mem_probe.setAutoDraw(True)
            rating_scale.setAutoDraw(True)
            if frame_n == 0:
                resp_clock.reset()
            win.flip()
        choice_history = rating_scale.getHistory()
        rating_scale.setAutoDraw(False)
        mem_probe.setAutoDraw(False)
        win.flip()

        for frame_n in range(info['mem_pause_frames']):
            fixation.setAutoDraw(True)
            win.flip()
        fixation.setAutoDraw(False)
        win.flip()
        
        trial_count += 1

def pres_block( cue_tuples, pickle_name, prev_stim, run, loop = object, saveData = True, test=False):
    """Runs experimental block and saves reponses if requested"""

    trial_clock = core.Clock()

    previous_items = {}
    cued = []
    uncued = []

    reaction_time={}
    cued_RT = []
    uncued_RT = []

    trial_num = 0
    cue_tup_num = 0
    catch_num = 0

    for this_trial in loop:

        if catches[trial_num] == 0:
            params = cue_tuples[cue_tup_num]

        else:
            params = catch_tuples[catch_num]
            catch_num += 1

        if params[0] == 'cue_R':
            cue = cue_right
        else:
            cue = cue_left

        if params[1] == cat1[0]:
            cue_cat = cue_cat_1
        else:
            cue_cat = cue_cat_2

        cue.setPos( [0, 0] )

        if block == True and cue_tup_num == 0 :
            fixation.setAutoDraw(False)
            cue.setAutoDraw(True)
            cue_cat.setAutoDraw(True)
            for frame_n in range(info['cue_frames']*3):
                win.flip()
            cue.setAutoDraw(False)
            cue_cat.setAutoDraw(False)
            fixation.setAutoDraw(True)

        cue_tup_num += 1

        #show fixation
        fixation.setAutoDraw(True)
        for frame_n in range(info['fix_frames']):
            win.flip()

        #show cue on each iteration if NOT block design
        if block == False:
            fixation.setAutoDraw(False)
            cue.setAutoDraw(True)
            cue_cat.setAutoDraw(True)
            for frame_n in range(info['cue_frames']):
                win.flip()
            cue.setAutoDraw(False)
            cue_cat.setAutoDraw(False)
            fixation.setAutoDraw(True)

        #pause
        for frame_n in range(info['cue_pause_frames']):
            fixation.setAutoDraw(True)
            win.flip()

        # IMTRACE
        # available_images = images not in: cued/uncued current trial, prev stim, mem_only_0
        # randomly select img1 and img2 from available_images
        
        # [3] RUN TRIAL
        all_items = [f for f in os.listdir(dir1) if f.endswith('.jpg')]
        available_items = [x for x in all_items if 
                          (x not in cued and 
                          x not in uncued and 
                          x not in prev_stim and 
                          x not in mem_only_0)]

        #select and load image stimuli at random
        img1_file = random.choice(available_items)
        img1 = dir1+img1_file
        img2_file = img1_file

        while (img2_file == img1_file):
            img2_file = random.choice(available_items)

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

        # clear screen
        win.flip()

        resp = None
        rt = None

        probe = visual.TextStim(win=win, ori=0, name='fixation', text='o', font='Arial', height = 2, color='lightGrey',
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
                keys = event.getKeys(keyList = ['1','3'])
            if len(keys) > 0:
                resp = keys[0]
                rt = resp_clock.getTime()
                break

            # if no response, wait until response
            if (resp == None and test == False):
                keys = event.waitKeys(keyList = ['1', '3'])
                resp = keys[0]
                rt = resp_clock.getTime()

            elif (resp == None and test == True):
                rt = 'test'

            probe.setAutoDraw(False)

        if ( cue == cue_right and position > 1 ):
            cued_RT.append(rt)

        else:
            uncued_RT.append(rt)
            win.flip()

        win.flip()
        trial_num+=1

    previous_items['cued'] = cued
    previous_items['uncued'] = uncued
    previous_items['uncued_RT'] = uncued_RT
    previous_items['cued_RT'] = cued_RT
    previous_items['run_time'] = trial_clock.getTime()
    previous_items['cue_tuples'] = cue_tuples

    with open(pickle_name, 'wb') as f:
        pickle.dump(previous_items, f)

    fixation.setAutoDraw(False)

def mem_block( conds, current_pickle, prev_stim ):
    trial_clock = core.Clock()

    # start dictionary to store data
    mem_task = {}

    # file_name for saved output
    pickle_name_mem = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['date_str'] + 'mem_items.pkl'

    #KZ : reads in the pickle file
    with open(current_pickle,'rb') as fp:
        current_list = pickle.load(fp)

    # empty list to store items used in memory task
    previous_mem = []
    all_ratings = []

    for each in conds:
        all_items = mem_only
        
        # REMOVE AFTER SUCCESSFUL RUN
#        all_items = []
#
#        for entry in all_items_0:
#            if fnmatch.fnmatch(entry,'*.jpg'):
#                all_items.append(entry)


        # IMTRACE -- see notes below

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
        available_attended_stim1 = random.sample(available_attended_stim1, len(available_attended_stim1)/2)
        
        available_attended_stim2 = [x for x in current_list['cued_2'] if x not in previous_mem]
        available_attended_stim2 = random.sample(available_attended_stim2, len(available_attended_stim2)/2)

        available_unattended_stim1 = [x for x in current_list['uncued_1'] if x not in previous_mem]
        available_unattended_stim1 = random.sample(available_unattended_stim1, len(available_unattended_stim1)/2)
        
        available_unattended_stim2 = [x for x in current_list['uncued_2'] if x not in previous_mem]
        available_unattended_stim2 = random.sample(available_unattended_stim2, len(available_unattended_stim2)/2)

        # IMTRACE -- MAKE SURE PREV_STIM ARE SPLIT FILENAMES
        available_random = [x for x in all_items if
                            (x not in previous_mem
                            and x not in current_list['cued_1']
                            and x not in current_list['cued_2']
                            and x not in current_list['uncued_1']
                            and x not in current_list['uncued_2']
                            and x not in prev_stim)]

        # IMTRACE -- LEFT OFF HERE (3/15 KZ)

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

        ##################

        ##KIRSTEN ORIGINAL##
        #split line to stay within max line length; EP
        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4',
                                            singleClick = True, pos = [0,-.42], acceptPreText = '-',
                                            maxTime=3.0, minTime=0, marker = 'triangle', showAccept=False, acceptSize=0) #disappear=True)

        event.getKeys(keyList = None)
        for frame_n in range(info['mem_frames']):
            mem_probe.setAutoDraw(True)
            rating_scale.setAutoDraw(True)
            if frame_n == 0:
                resp_clock.reset()
            win.flip()
        choice_history = rating_scale.getHistory()
        rating_scale.setAutoDraw(False)
        mem_probe.setAutoDraw(False)
        win.flip()

        for frame_n in range(info['mem_pause_frames']):
            fixation.setAutoDraw(True)
            win.flip()
        fixation.setAutoDraw(False)

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
# for specified # of runs, show practice presentation
#for rep in range(0, practice_runs):

if practice_runs != 0:
    practice_trials = data.TrialHandler(trialList = [{}]*(10), nReps = 1)
    show_instructions(text = introduction, acceptedKeys = None)
    practice_block(practice_dir, practice_runs, practice_trials)

if practice_runs == 0:
    show_instructions(text = introduction, acceptedKeys = ['1','2','3','4','return', 'escape'])

# for specified # of reps, run presentation then memory
for rep in range(0,repetitions):

    cue_tuple_input = cue_tuples[rep*num_trials:(rep+1)*num_trials]
    #practice_trials = data.TrialHandler(trialList = [{}]*(practice_slow_trials + practice_quick_trials), nReps = 1)

    # pickle_name for use in both functions
    # split line to stay within max line length; EP
    pickle_name = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + \
                  info['date_str'] + 'previous_items.pkl'

    # if pkl files exist from previous runs, load the data
    prev_runs = []
    files = get_files(dir_check)

    # obtain all previously displayed images
    if len(files)>0:
        mem_dict = load_mem_p(files)
        prev_dict = load_prev_p(files)

        # list of all previous single memory images
        prev_stim= mem_dict['images']

        # list of all previous composite presentation stim
        prev_stim.append(prev_dict['cued'])
        prev_stim.append(prev_dict['uncued'])
        prev_stim = [val for sublist in prev_stim for val in sublist]

    else:
        prev_stim = []

    trials = data.TrialHandler(trialList = [{}]*total_trials, nReps = 1)

    # presentation task
    if rep == 0:
        show_instructions(text = instruct_exp, acceptedKeys = ['1','2','3','4','return', 'escape'])
    else:
        show_instructions(text = instruct_exp2, acceptedKeys = ['1','2','3','4','return', 'escape'])
    
    if test == False:
        pres_block(cue_tuple_input, pickle_name, prev_stim, info['run'], trials, test=False)
    else:
        pres_block(cue_tuple_input, pickle_name, prev_stim, info['run'], trials, test=True)

    # memory task
    if rep == 0:
        show_instructions(text = instruct_mem, acceptedKeys = ['1','2','3','4','return'])
        
    else:
        show_instructions(text = instruct_mem2, acceptedKeys = ['1','2','3','4','return'])

    mem_block(range(0,num_trials*4), pickle_name, prev_stim)

    info['run'] = str(int(info['run'])+1)

# closing message
show_instructions(text = instruct_thanks, acceptedKeys = ['1','2','3','4','return'])

win.close()

#end of task questionnaire
endDlg = gui.Dlg(title="Post Questionnaire")
endDlg.addField('1. How engaging did you find this experiment?', choices=['--', "Very engaging", "A little engaging", "Neutral", "A little boring", "Very boring"])
endDlg.addField('2. How tired do you feel?', choices=['--', "Very tired", "A little tired", "Neutral", "A little alert", "Very alert"])
endDlg.addField('3. Did you find one category easier to remember? If so, which one and why?')
endDlg.addField('4. Did you find one side easier to attend to? If so, which one?')
endDlg.addField('5. What strategies did you use (if any) to help remember the attended images?')

end_data = endDlg.show()
if endDlg.OK:
    print(end_data)
    with open(post_name, 'wb') as f:
        pickle.dump(end_data, f)
