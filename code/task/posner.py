# This code was created by Kirsten Ziman (kirsten.k.ziman.gr@dartmouth.edu), 4/2018
# (originally modified from Posner experiment sample code found here: )
# for more information, visit: www.context-lab.com


## IMPORTS ###########################################

import psychopy
from psychopy import visual, event, core, data, gui, logging
from itertools import groupby
import random
import os
import pickle
import fnmatch
import glob
import pandas as pd
import sys
#import pylinkwrapper

sys.path.insert(0, '../analysis/')
from analysis import *

## PARAMETERS + SUB INFO #############################

vers = '2.0'

## edit parameters in section below only! ~~~~~~~~~~~

# test mode
test = False

# eye tracking
track = False

# runs
repetitions = 8

# pres trials per run
num_trials = 10

# invalid attention task trials per run
invalid = 1

# counterbalancing conditions
num_balance = 4

# block design (vs. random cue each trial)
block = True

# number of practice runs
practice_runs = 1

# stim dirs
dir1 = '../../stim/composites_new/' # Overlays

stim_dir1 = '../../stim/faces/' # Face
stim_dir2 = '../../stim/places/' # Scene

practice_dir = '../../stim/practice_F/' # Practice overlays

cue_pic1 = '../../stim/Cue/scene_icon.png' # Scene icon
cue_pic2 = '../../stim/Cue/face_icon.png' # Face icon

# categories - first letter of each string used for later labels
cat1 = 'Location'
cat2 = 'Face'

# stim sizes
fixation_size = 0.5
probe_size = 7
cue_size = 2

## edit parameters in section above only! ~~~~~~~~
## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# clocks
global_clock = core.Clock()
logging.setDefaultClock(global_clock)

# initialize info dictionary
info = {}


# USER INPUT BOXES

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

## SUBJECT FILES AND DIRECTORIES ############

# subject directory string
dir_name = info['participant'] + '_' + info['date_str']
dir_check = '../../data/' + dir_name

# if subject directory does not already exist, create it
if not os.path.exists(dir_check):
    os.makedirs(dir_check)

# file names
log_file_name = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['date_str']

# log files
log_data = logging.LogFile (log_file_name+'_log', filemode='w', level = logging.DATA)
log_data = logging.LogFile (log_file_name+'_2.log', filemode='w', level = logging.EXP)

# pre and post questionnaire filenames
pre_name = "../../data/" + dir_name + '/'+ info['participant'] + '_' + 'pre' + '_' + info['date_str'] + '.txt'
post_name = "../../data/" + dir_name + '/'+ info['participant'] + '_' + 'post' + '_' + info['date_str'] + '.txt'

# save responses to pre questionnaire
with open(pre_name, 'wb') as f:
    pickle.dump(end_data, f)


######## TASK INSTRUCTION TEXT ################

# INTRO
introduction = '\n\n Thank you for participating in this experiment! ' \
                '\n\n In the experiment, you will pay attention to specific items on the screen.' \
                '\n Then, we will test your memory for some of the items you have seen. ' \
                '\n\n Press any key to continue... ' \

# PRACTICE
instruct_pract1 = ' You will see many images like the one below.' \
                '\n You will need to pay special attention to either the OBJECT or SCENE. ' \
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n Press any key to continue...' \

instruct_pract2 = ' Let\'s practice now! \n Look straight at the image and focus as hard as you can on the OBJECT. ' \
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you can focus on the OBJECT well, press any key... ' \

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
                '\n This time, keeping your eyes at center, try and focus on the OBJECT on the RIGHT.' \
                '\n\n Press any key to begin.' \

instruct_pract7 = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you are done, press any key to continue... ' \

instruct_pract8 = ' Now, you will practice ' \
                'attending to parts of images based on cue icons. ' \
                '\n\n First, you\'ll see a pair of cue icons: ' \
                '\n One arrow icon pointing left or right (< or >) ' \
                ' and one image icon (object or scene): ' \
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


## STIMULUS TIMING ###########################

# create window
win = visual.Window([1024,768], fullscr = True, monitor = 'testMonitor', units='deg', color = 'black')

# obtain frame rate
frame_rate_secs = win.getActualFrameRate()

# set stim display durations
if test == False:

    # fixation
    info['fix_frames'] = int(round(1.0 * frame_rate_secs))

    # R/L cue
    info['cue_frames'] = int(round(.5 * frame_rate_secs))
    info['cue_pause_frames'] = int(round(0* frame_rate_secs))
    info['cue_pract_long'] = int(round(15.0 * frame_rate_secs))
    info['cue_pract_short'] = int(round(3.0 * frame_rate_secs))
    info['probe_frames'] = int(round(3.0 * frame_rate_secs))
    info['probe_pos'] = 8
    info['cue_pos'] = info['probe_pos']
    info['mem_frames'] = int(round(2 * frame_rate_secs))
    info['mem_pause_frames'] = int(round(1 *frame_rate_secs))

if test == True:
    # this test mode quickly bypasses all presentations to allow for check of saved data and stimulus order after task completion
    # different timing parameters might be ideal here for different test objectives

    # fixation
    info['fix_frames'] = int(round(0 * frame_rate_secs))

    # R/L cue
    info['cue_frames'] = int(round(0 * frame_rate_secs))
    info['cue_pause_frames'] = int(round(0* frame_rate_secs))
    info['cue_pract_long'] = int(round(0* frame_rate_secs))
    info['cue_pract_short'] = int(round(0 * frame_rate_secs))
    info['probe_frames'] = int(round(0 * frame_rate_secs))
    info['probe_pos'] = 8
    info['cue_pos'] = info['probe_pos']
    info['mem_frames'] = int(round(0 * frame_rate_secs))
    info['mem_pause_frames'] = int(round(0 *frame_rate_secs))


# create visual stim

fixation = visual.TextStim(win=win, ori=0, name='fixation', text='+', font='Arial',
                           height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

probe = visual.TextStim(win=win, ori=0, name='posner', text='o', font='Arial', height = 2, color='lightGrey',
                         colorSpace='rgb', opacity=1, depth=0.0)

cue_right = visual.TextStim(win=win, ori=0, name='cue_right', text = '>', font='Arial',
                            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

cue_left = visual.TextStim(win=win, ori=0, name='cue_left', text='<', font='Arial',
                           height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

cue_cat_1 = visual.ImageStim(win, cue_pic1, size=cue_size, name='cue_img1')
cue_cat_1.setPos([0, 2])

cue_cat_2 = visual.ImageStim(win, cue_pic2, size=cue_size, name='cue_img2')
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
validity_0 = validity_0*repetitions
validity = random.sample(validity_0, len(validity_0))

#cue_tuples is a list of tuples (one per trial) specifying: R/L attend, F/H attend, validity
cue_tuples_0 = zip(right_left, face_house, validity) #, attention)

# if not block design, shuffle all trials
if block == False :
    cue_tuples = random.sample(cue_tuples_0, len(cue_tuples_0))

else:
    # chunk the tuples into eight chunks of ten
    chunk_tuples = [cue_tuples_0[i:i+10] for i in range(0, len(cue_tuples_0), 10)]

    # order randomnly
    cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))

    # if any cues repeat back-to-back, reshuffle!
    while len([(k, sum(1 for i in g)) for k,g in groupby(cue_tuples)]) > len(chunk_tuples) :
        cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))

    # cue_tuples is a list of tuples (one per trial) specifying: catch/no, R/L attend, F/H attend
    cue_tuples = flatten(cue_tuples)


## DESIGNATE MEMORY-ONLY IMAGES #####################

# set aside composite images for memory blocks only
mem_only_0 = [f for f in random.sample([z for z in os.listdir(dir1) if z.endswith('.jpg')],num_trials*repetitions*2)]
mem_only = img_split(mem_only_0)


############ PRACTICE RUN FUNCTIONS #################

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
        center = visual.ImageStim(win, '../../stim/hybrid_1_F/00060931230fa_sunaaehaikpckyjsety.jpg', size = probe_size)
        center.setAutoDraw(True)
        win.flip()

    elif hybrid_pair == True:
        hybrid1 = visual.ImageStim(win, '../../stim/hybrids_2_F/00002940128fb_sunaaacnosloariecpa.jpg', size = probe_size)
        hybrid2 = visual.ImageStim(win, '../../stim/hybrids_2_F/00003941121fa_sunaaaenaoynzhoyheo.jpg', size = probe_size)

        hybrid1.setPos([info['probe_pos'], 0])
        hybrid2.setPos([-info['probe_pos'], 0])

        hybrid1.setAutoDraw(True)
        hybrid2.setAutoDraw(True)
        fixation.setAutoDraw(True)
        win.flip()

    else:
        win.flip()

    # wait for response
    if test == False:
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
        items = os.listdir('../../stim/hybrids_8_2_F/')

        #select and load image stimuli
        img1_filename = '../../stim/hybrids_8_2_F/'+items[trial_count*2]
        img2_filename = '../../stim/hybrids_8_2_F/'+items[trial_count*2 + 1]

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
        items = os.listdir('../../stim/hybrids_8_1_F/')

        #select and load image stimuli at random
        img1_filename = '../../stim/hybrids_8_1_F/'+items[trial_count*2]
        img2_filename = '../../stim/hybrids_8_1_F/'+items[trial_count*2 + 1]

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

    items = os.listdir('../../stim/singles_4_F/')

    trial_count = 0

    for this_trial in loop:
        #select and load image stimuli at random
        mem = '../../stim/singles_4_F/'+items[trial_count]

        mem_probe = visual.ImageStim( win, mem, size=probe_size )
        mem_probe.setPos( [0, 0] )

        event.clearEvents()

        ##################

        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4',
                                            singleClick = True, pos = [0,-.42], acceptPreText = '-',
                                            maxTime=3.0, minTime=0, marker = 'triangle', showAccept=False, acceptSize=0)

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


############ EXPERIMENT FUNCTIONS #################

def pres_block( cue_tuples, pickle_name, prev_stim, run, loop = object, saveData = True, test=test):
# """Runs experimental block and saves reponses if requested"""

    previous_items = {}
    cue_tuples = random.sample(cue_tuples, len(cue_tuples))

    trial_clock = core.Clock()

    cued = []
    uncued = []
    reaction_time={}
    cued_RT = []
    uncued_RT = []
    trial_num = 0
    cue_tup_num = 0


    if track:

        # Eye tracker trial set-up
        stxt = info['run']
        tracker.set_status(stxt)  # Define status message that appears on eye-link
        #  display

        tracker.set_trialid()  # Sends trial start message for EDF
        tracker.send_message('Presentation Trial')

        # Draw IA
        tracker.draw_ia(0, 0, 1, 1, 5, 'fixation')  # Draw interest area and box

        # Start recording
        tracker.record_on()

    for this_trial in loop:

        counter = 0
        params = cue_tuples[cue_tup_num]

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

        # show cue on each iteration if NOT block design
        if block == False:
            fixation.setAutoDraw(False)
            cue.setAutoDraw(True)
            cue_cat.setAutoDraw(True)
            for frame_n in range(info['cue_frames']):
                win.flip()
            cue.setAutoDraw(False)
            cue_cat.setAutoDraw(False)
            fixation.setAutoDraw(True)

        # pause
        for frame_n in range(info['cue_pause_frames']):
            fixation.setAutoDraw(True)
            win.flip()

        # [3] RUN TRIAL
        all_items = [f for f in os.listdir(dir1) if f.endswith('.jpg')]
        available_items = [x for x in all_items if (x not in cued and x not in uncued and x not in prev_stim and x not in mem_only_0)]

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
        if cue == cue_right:
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
            if frame_n == 0:
                resp_clock.reset()
                keys = event.getKeys(keyList = ['1','3'])
            if len(keys) > 0:
                resp = keys[0]
                rt = resp_clock.getTime()
                break

            # clear screen
            win.flip()
            probe.setAutoDraw(False)

            # if no response, wait until response
            if (resp == None and test == False):
                keys = event.waitKeys(keyList = ['1', '3'])
                resp = keys[0]
                rt = resp_clock.getTime()

            elif (resp == None and test == True):
                rt = 'test'

        if cue == cue_right and position > 1 :
            cued_RT.append(rt)

        elif cue == cue_left and position < 1:
            cued_RT.append(rt)

        else:
            uncued_RT.append(rt)
            win.flip()

        win.flip()
        trial_num+=1

    if track:
        # Stop Recording
        tracker.record_off()

        # Send response key to EDF file
        #tracker.send_var('response', keyp[0][0])

        # End trial for EDF
        tracker.set_trialresult()

        # ISI with fixation check
        cfix.draw()
        win.flip()
        tracker.fixcheck(2, 1, 'z')

        # Retrieve EDF
        tracker.end_experiment(edf_name)  # Closes and retrieves EDF file

    previous_items['cued'] = cued
    previous_items['uncued'] = uncued
    previous_items['uncued_RT'] = uncued_RT
    previous_items['cued_RT'] = cued_RT
    previous_items['cue_tuples'] = cue_tuples

    with open(pickle_name, 'wb') as f:
        pickle.dump(previous_items, f)

    fixation.setAutoDraw(False)


def mem_block( conds, current_pickle, prev_stim ):
    trial_clock = core.Clock()

    # variables to store mem data
    mem_task = {}
    previous_mem = []
    all_ratings = []

    # file_name for saved output
    pickle_name_mem = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + info['date_str'] + 'mem_items.pkl'

    # load in pickle file
    with open(current_pickle,'rb') as fp:
        current_list = pickle.load(fp)

    # split composites
    attended_side = img_split(current_list['cued'], cat=True)
    unattended_side = img_split(current_list['uncued'], cat=True)

    # choose 160 novel, 40 side cat (x4), then randomize order, then present
    this_mem = []

    for x in attended_side.keys():
        this_mem.append(random.sample(attended_side[x], len(attended_side[x])/2))
        this_mem.append(random.sample(unattended_side[x], len(unattended_side[x])/2))

    this_mem.append(random.sample([x for x in mem_only if x not in previous_mem and x not in prev_stim and x.startswith('sun')],10))
    this_mem.append(random.sample([x for x in mem_only if x not in previous_mem and x not in prev_stim and x[0].isdigit()],10))
    this_mem = random.sample(flatten(this_mem), len(flatten(this_mem)))

    for each,mem_file in zip(conds,this_mem):
        if os.path.isfile(stim_dir1+mem_file):
            mem_dir = stim_dir1
        else:
            mem_dir = stim_dir2

        mem = mem_dir + mem_file
        mem_probe = visual.ImageStim( win, mem, size=probe_size )
        mem_probe.setPos( [0, 0] )

        win.callOnFlip(resp_clock.reset)
        event.clearEvents()

        ##################

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

    with open(pickle_name_mem, 'wb') as f:
        pickle.dump(mem_task, f)


######### RUN EXPERIMENT ###########

if track == True:

    # Initiate eye-tracker link and open EDF
    tracker = pylinkwrapper.Connect(win, '1_test')

    # Calibrate eye-tracker
    tracker.calibrate()

# show practice presentation
if practice_runs != 0:
    practice_trials = data.TrialHandler(trialList = [{}]*(10), nReps = 1)
    show_instructions(text = introduction, acceptedKeys = None)
    practice_block(practice_dir, practice_runs, practice_trials)

else:
    show_instructions(text = introduction)

# for specified # of reps, run presentation then memory
for rep in range(0,repetitions):

    # select chunk of tuples from cue_tuples
    cue_tuple_input = cue_tuples[rep*num_trials:(rep+1)*num_trials]

    # pickle_name for use in both functions
    pickle_name = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + \
                  info['date_str'] + 'previous_items.pkl'
    edf_name = "../../data/" + dir_name + '/' + info['participant'] + '_' + info['run'] + '_' + \
                info['date_str'] + '.edf'

    # if pkl files exist from previous runs, load the data
    prev_runs = []
    files = get_files(dir_check)

    # obtain all previously displayed images
    if len(files)>0:
        mem_dict = load_mem_p(files)
        prev_dict = load_prev_p(files)

        # list of all previous single memory images
        prev_stim = [mem_dict['images']]

        # list of all previous composite presentation stim
        prev_stim.append(prev_dict['cued'])
        prev_stim.append(prev_dict['uncued'])

        # flatten list (twice)
        prev_stim = [val for sublist in prev_stim for val in sublist]
        prev_stim = [val for sublist in prev_stim for val in sublist]

    else:
        prev_stim = []

    trials = data.TrialHandler(trialList = [{}]*num_trials, nReps = 1)

    cue_pic1 = '../../stim/Cue/obj_icon.png'

    # presentation task
    if rep == 0:
        show_instructions(text = instruct_exp)
    else:
        show_instructions(text = instruct_exp2)

    pres_block(cue_tuple_input, pickle_name, prev_stim, info['run'], trials, test=test)


    # memory task
    if rep == 0:
        show_instructions(text = instruct_mem)

    else:
        show_instructions(text = instruct_mem2)

    mem_block(range(0,num_trials*4), pickle_name, prev_stim)

    info['run'] = str(int(info['run'])+1)

# closing message
show_instructions(text = instruct_thanks)
win.close()

# end of task questionnaire
endDlg = gui.Dlg(title="Post Questionnaire")
endDlg.addField('1. How engaging did you find this experiment?', choices=['--', "Very engaging", "A little engaging", "Neutral", "A little boring", "Very boring"])
endDlg.addField('2. How tired do you feel?', choices=['--', "Very tired", "A little tired", "Neutral", "A little alert", "Very alert"])
endDlg.addField('3. Did you find one category easier to remember? If so, which one and why?')
endDlg.addField('4. Did you find one side easier to attend to? If so, which one?')
endDlg.addField('5. What strategies did you use (if any) to help remember the attended images?')

end_data = endDlg.show()

# save out questionnaire info
if endDlg.OK:
    (end_data)
    with open(post_name, 'wb') as f:
        pickle.dump(end_data, f)
