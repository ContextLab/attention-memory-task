# HELPER FUNCTIONS FOR ATTENTION AND MEMORY EXPERIMENT

# Imports
import pandas as pd
from psychopy import visual, event, core, data, gui, logging
import random
import os
import time
import csv
import pickle
import math

# Tiny helpersautodrw

def group_it(data, num):
    '''
    input: list of data items of any types
    output: ordered list containing length num sublists of inputted data
    '''
    return([data[i:i+num] for i in range(0, len(data), num)])

def flatten(the_list):
    '''
    input: list of lists
    output: single list containing all data, ordered, from nested lists
    '''
    return([val for sublist in the_list for val in sublist])

# Data entry & organization functions

def subject_info(header):
    '''
    input: text to show at top of pop-up (string)
           path to data directory (string)
    Creates pop up box to obtain subject# and run#
    '''
    info = {}
    info['participant'] = ''
    info['run'] = ''
    dlg = gui.DlgFromDict(dictionary=info, title=header)
    if dlg.OK:
        return(info)
    else:
        print("Error!")

def subject_directory(info, data_path, path_only=False):
    '''
    input:    info - subject information (dictionary)
              data_path - path to data directory (string)
    output:   path to subject-specific directory (string)
    If NOT path_only --> Creates subject directory if does not exist
    '''

    dir_name = data_path + str(info['participant']) + '_' + data.getDateStr()[0:11] + '/'

    if not os.path.exists(dir_name) and not path_only:
        os.makedirs(dir_name)
        with open(dir_name + 'buttons_full.csv','wb') as output:
            wr = csv.writer(output, dialect='excel')
            wr.writerows([['Button', 'Time']])
    else:
        if not path_only:
            print('WARNING: subject directory exists already!')
    return(dir_name)

def pre_questionnaire(info, save=True, save_path='.'):
    '''
    Create pop up box to obtain and save subject's demographic info
    input:    info - dictionary containing participant# and run#
              save - boolean indicating whether to autosave
              save_path - if save==True, path to data save location
    output:   if save==True, save out data, return nothing
              if save==False, return questionnaire data
    '''

    preDlg = gui.Dlg()

    preDlg.addField('1. age')
    preDlg.addField('2. sex:', choices=['--', "Male", "Female", "Other", "No Response"])
    preDlg.addField('3. Are you hispanic or latino?', choices=['--', "Yes", "No"])
    preDlg.addText('')
    preDlg.addText('4. Race (check all that apply):')
    preDlg.addField('White', False)
    preDlg.addField('Black or African American', False)
    preDlg.addField('Native Hawaiian or other Pacific Islander', False)
    preDlg.addField('Asian', False)
    preDlg.addField('American Indian or Alaskan Native', False)
    preDlg.addField('Other', False)
    preDlg.addField('No Response', False)
    preDlg.addText('')
    preDlg.addField('5. Highest Degree Achieved:', choices = ['--', 'some high school', 'high school graduate', 'some college', \
    'college graduate', 'some graduate training', "Master's", 'Doctorate'])
    preDlg.addText('')
    preDlg.addText('6. Do you have any reading impairments')
    preDlg.addField('(e.g. dyslexia, uncorrected far-sightedness, etc.)', choices = ['--', "Yes", "No"])
    preDlg.addText('')
    preDlg.addField('7. Do you have normal color vision?', choices = ['--', "Yes", "No"])
    preDlg.addText('')
    preDlg.addText('8. Are you taking any medications or have you had')
    preDlg.addText('any recent injuries that could')
    preDlg.addField('affect your memory or attention?', choices = ['--', "Yes", "No"])
    preDlg.addText('')
    preDlg.addField('9. If yes to question above, describe')
    preDlg.addText('')
    preDlg.addText('10. How many hours of sleep did')
    preDlg.addField('you get last night? (enter only a number)')
    preDlg.addText('')
    preDlg.addText('11. How many cups of coffee')
    preDlg.addField('have you had today? (enter only a number)')
    preDlg.addText('')
    preDlg.addField('12. How alert are you feeling?:', choices=['--', "Very sluggish", "A little slugglish", "Neutral", "A little alert", "Very alert"])

    end_data = preDlg.show()

    if save == True:
        name = save_path + 'pre_questionnaire_' + info['participant'] + '.pkl'
        with open(name, 'wb') as f:
            pickle.dump(end_data, f)
    else:
        return(end_data)

def post_questionnaire(info, save=True, save_path='.'):
    '''
    Create pop up box to obtain and save subject's demographic info
    input:    info - dictionary containing participant# and run#
              save - boolean indicating whether to autosave
              save_path - if save==True, path to data save location
    output:   if save==True, save out data, return nothing
              if save==False, return questionnaire data
    '''

    # end of task questionnaire
    postDlg = gui.Dlg(title="Post Questionnaire")
    postDlg.addField('1. How engaging did you find this experiment?', choices=['--', "Very engaging", "A little engaging", "Neutral", "A little boring", "Very boring"])
    postDlg.addField('2. How tired do you feel?', choices=['--', "Very tired", "A little tired", "Neutral", "A little alert", "Very alert"])
    postDlg.addField('3. Did you find one category easier to remember? If so, which one and why?')
    postDlg.addField('4. Did you find one side easier to attend to? If so, which one?')
    postDlg.addField('5. What strategies did you use (if any) to help remember the attended images?')

    end_data = postDlg.show()

    if save == True:
        name = save_path + 'post_questionnaire_' + info['participant'] + '.pkl'
        with open(name, 'wb') as f:
            pickle.dump(end_data, f)
    else:
        return(end_data)

def buttons_full(paths, keys, absolute_time):
    '''
    Appends key press and time stamp to subject's key-press log (buttons_full.csv)
    input:   paths - paths to relevant directories (dictionary)
             keys - button presses to be saved to file (list of strings or nested lists of strings)
             absolute_time - timestamp to be written to file with key press
    '''
    with open(paths['subject'] + 'buttons_full.csv','a') as output:
        wr = csv.writer(output, dialect='excel')
        wr.writerows([[keys, absolute_time]])


# Functions for Creating Trial Parameters & Visual Stimuli

def cue_create(params, shuffle=False):
    '''
    input:    params - experiment parameters (stimulus display times, etc.) (dictionary)
    output:   three lists (length total-trials-in-experiment) assigning cued side,
              cued category, and cue validity for each trial
    '''

    presentations_per_run = params['presentations_per_run']
    runs = params['runs']

    # create tuples, one per trial, chunked by block, that assign: cued side, cued category
    cued_side = ['<']*int(presentations_per_run*runs/2)+['>']*int(presentations_per_run*runs/2)
    cued_category = flatten([['Face']*int(presentations_per_run*runs/4)+['Place']*int(presentations_per_run*runs/4)]*2)

    # validity (attention RT)
    raw_invalid = int(params['invalid_cue_percentage']*presentations_per_run*runs/100)
    num = (presentations_per_run*runs)-raw_invalid
    validity = [0]*raw_invalid+[1]*num
    validity = random.sample(validity, len(validity))

    # chunk trials by block and randomize
    cue_tuples_0 = list(zip(cued_side, cued_category))
    if shuffle == True:
        chunk_tuples = trial_shuffle(presentations_per_run, runs)
    #    chunk_tuples = [cue_tuples_0[i:i+presentations_per_run] for i in range(0, len(cue_tuples_0), presentations_per_run)]

    else:
        chunk_tuples = [cue_tuples_0[i:i+presentations_per_run] for i in range(0, len(cue_tuples_0), presentations_per_run)]

    # while any blocks repeat cues back-to-back, reshuffle
    cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))

    reshuffle = True

    while reshuffle==True:
        
        cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))
        shuff_count = 0

        for idx,x in enumerate(cue_tuples):
            
            if idx != 0:

                if x[0]==cue_tuples[idx-1][0]:
                    shuff_count += 1

        if shuff_count == 0:
            
            reshuffle = False

    cue_tuples = flatten(cue_tuples)
    final = [[x[0] for x in cue_tuples],[x[1] for x in cue_tuples],validity]

    # return list for each
    return(cue_tuples)

# def cue_create(params):
#     '''
#     input:    params - experiment parameters (stimulus display times, etc.) (dictionary)
#     output:   three lists (length total-trials-in-experiment) assigning cued side,
#               cued category, and cue validity for each trial
#     '''

#     presentations_per_run = params['presentations_per_run']
#     runs = params['runs']

#     # create tuples, one per trial, chunked by block, that assign: cued side, cued category
#     cued_side = ['<']*int(presentations_per_run*runs/2)+['>']*int(presentations_per_run*runs/2)
#     cued_category = flatten([['Face']*int(presentations_per_run*runs/4)+['Place']*int(presentations_per_run*runs/4)]*2)

#     # validity (attention RT)
#     raw_invalid = int(params['invalid_cue_percentage']*presentations_per_run*runs/100)
#     num = (presentations_per_run*runs)-raw_invalid
#     validity = [0]*raw_invalid+[1]*num
#     validity = random.sample(validity, len(validity))

#     # chunk trials by block and randomize
#     cue_tuples_0 = list(zip(cued_side, cued_category))
#     chunk_tuples = [cue_tuples_0[i:i+presentations_per_run] for i in range(0, len(cue_tuples_0), presentations_per_run)]

#     # while any blocks repeat cues back-to-back, reshuffle
#     cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))
#     reshuffle = True

#     while reshuffle==True:
#         for idx,x in enumerate(cue_tuples[1:-1]):
#             if x[0]==cue_tuples[idx+1][0] or x[0]==cue_tuples[idx-1][0]:
#                 cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))
#                 pass
#             elif idx==len(cue_tuples[1:-1])-1 and not (x[0]==cue_tuples[idx+1][0] or x[0]==cue_tuples[idx-1][0]):
#                 reshuffle=False

#     cue_tuples = flatten(cue_tuples)
#     final = [[x[0] for x in cue_tuples],[x[1] for x in cue_tuples],validity]

#     # return list for each
#     return(final)

def trial_setup(params):
    '''
    input:    params - experiment parameters (stimulus display times, etc.) (dictionary)
    output:   lists to assign subject number, run number, and trial type to every row
              of trial x parameter dataframe for single subject
    '''
    run = []
    trial_type = []

    for x in range(params['runs']):
        trial_type.extend(['Presentation']*params['presentations_per_run'])
        trial_type.extend(['Memory']*params['presentations_per_run']*params['mem_to_pres'])
        run.extend([x]*params['presentations_per_run']*(params['mem_to_pres']+1))

    return([run, trial_type])

def presentation_images(presentation):
    '''
    input:   list of composite images for display in presentation runs
    output:  dict with keys 'Cued' and 'Uncued', each containing three lists
             (composite images, single place images, and single face images)
    '''
    images = {}
    cued = presentation[0:int(len(presentation)/2)]
    uncued = presentation[int(len(presentation)/2):]

    for x,y in zip(['Cued','Uncued'],[cued, uncued]):
        images[x] = {'composite':y, 'place':img_split(y, cat=True)['place_im'], 'face':img_split(y, cat=True)['face_im']}

    return(images)

def img_split(image_list, cat = False):
    '''
    Splits overlay image filenames into filenames of the original, single images
    input :    list of composite image filenames
    output :   if cat==False, list of single image filenames
               if cat==True, two lists of single image filenames (listed by category)
    '''

    split = [words for segments in image_list for words in segments.split('_')]
    a = [word+'.jpg' for word in split if word[-3:]!='jpg']
    b = [word for word in split if word[-3:]=='jpg']
    glom = a+b

    if cat == False:
        return(glom)

    else:
        return({'face_im':a, 'place_im':b})

def memory_image(presentation, memory):
    '''
    inputs:  list of all presentation images
             list of all novel memory images
    outputs: list of all images for memory trials
             (half novel, and even proportions of prev seen cued/uncued, face/house)
    '''

    # parse cued/uncued presentation composites
    cued = presentation[0:int(len(presentation)/2)]
    uncued = presentation[int(len(presentation)/2):]
    # parse novel single images
    memory_face = img_split(memory, cat=True)['face_im']
    memory_place = img_split(memory, cat=True)['place_im']

    # group by trials
    cued = group_it(cued, 10)
    uncued = group_it(uncued, 10)
    memory_face = group_it(memory_face, 10)
    memory_place = group_it(memory_place, 10)

    # append the split singles from all selected images (1/2 prev seen, and all chosen for memory)
    all_singles = []
    for x in range(len(cued)):
        singles = []
        singles.extend(img_split(random.sample(cued[x],int(len(cued[x])/2))))
        singles.extend(img_split(random.sample(uncued[x],int(len(uncued[x])/2))))
        singles.extend(memory_face[x])
        singles.extend(memory_place[x])
        singles = random.sample(singles, len(singles))
        all_singles.extend(singles)
    return(all_singles)

def initialize_df(info, categories, paths, params):
    '''
    Creates dataframe for all trials (presentation and memory) for a single subject,
    including all trial-wise parameters (with empty cells as placeholders (None type)
    for impending data collection) and saves a copy to csv in subject's data directory
    input:  info- subject information (dictionary)
            categories- image categories information (dictionary)
            paths- paths to subject-relevant directories (dictionary)
            params- experiment parameters (dictionary)
    output: dataframe containing parameters, image stim, and info, for all trials
    '''

    total_pres = params['presentations_per_run']*params['runs']

    # create column names
    columns = ['Subject', 'Trial Type', 'Run', 'Cued Composite', 'Uncued Composite', 'Cued Face',
                'Cued Place', 'Uncued Face', 'Uncued Place', 'Memory Image', 'Category', 'Cued Side',
                'Cued Category', 'Attention Response Time (s)', 'Familiarity Reaction Time (s)',
                'Familiarity Rating', 'Attention Level', 'Cue Validity', 'Post Invalid Cue', 'Pre Invalid Cue',
                'Attention Button', 'Rating History', 'Stimulus Onset', 'Stimulus End', 'Attention Probe']

    df = pd.DataFrame(index = range(total_pres*5), columns=columns)

    # add subject#, run#, trial types, cues
    df['Subject'] = info['participant']
    df['Run'],df['Trial Type'] = trial_setup(params)
    mask = df['Trial Type']=='Presentation'
    df.loc[mask,'Cued Side'],df.loc[mask,'Cued Category'],df.loc[mask,'Cue Validity'] = cue_create(params)
    df.loc[mask, 'Attention Probe'] = random.sample(['o']*(len(df.loc[mask].index)/2) + ['x']*(len(df.loc[mask].index)/2), len(df.loc[mask].index))

    # Select composite images
    composites = random.sample(os.listdir(paths['stim_path']+'composite/'), total_pres*(params['mem_to_pres']-1))
    presentation = composites[0:int(len(composites)*2/3)]
    memory = composites[int(len(composites)*2/3):]

    # add presentation images
    pres_dict = presentation_images(presentation)

    for cue in ['Cued','Uncued']:
        df.loc[mask, cue+' Composite']=pres_dict[cue]['composite']
        df.loc[mask, cue+' Face']=pres_dict[cue]['face']
        df.loc[mask, cue+' Place']=pres_dict[cue]['place']

    # add memory images
    mask2 = df['Trial Type']=='Memory'
    df.loc[mask2, 'Memory Image']= memory_image(presentation, memory)

    # save dataframe
    df.to_csv(paths['subject']+'intial_df.csv')
    return(df)

def cue_stim(win, side, category, stim_dir):
    '''
    inputs: win (psychopy visual window), cue side (string),
            cue category (string), stimulus directory (string)
    outputs: appropriate cue or fixation stimulus for center screen
    '''

    stim1 = visual.ImageStim(win, image=stim_dir+'cue/'+category+'.png', size=2, autoLog=True, name='CATEGORY CUE: '+category)

    stim2 = visual.TextStim(win=win, ori=0, name='SIDE CUE: '+side, text = side, font='Arial',
            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0, autoLog=True)

    return([stim1,stim2])

def fix_stim(win):
    """
    input:  psychopy visual window
    output: central fixation stimulus for display in window
    """
    stim1 = visual.TextStim(win=win, ori=0, name='FIXATION CROSS', text='+', font='Arial',
                  height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0, autoLog=True)
    return(stim1)

def cued_pos(side, validity=True):
    """
    input: cued side for a given trial (string), desired stimulus validity (bool)
    output: x-axis screen location for the stimulus (int)
    """

    if side ==  '>' and validity==1:
        pos = 8
    elif side == '>' and validity==0:
        pos = -8
    elif side == '<' and validity==1:
        pos = -8
    elif side == '<' and validity == 0:
        pos = 8
#    else:
#        pos = 8

    return(pos)

def composite_pair(win, cued, uncued, side, stim_dir, practice=False, mem_practice=False):
    """
    input:  win (psychopy visual window), cue side (string),
            cue category (string), stimulus directory (string)
    output: list of two composite image stimuli (with stim location, size, etc)
            for display in presentation trial
    """
    cued_position = cued_pos(side)

    if practice:
        dir = 'practice_composite/'
    elif mem_practice:
        dir = 'practice_mem_composite/'
    else:
        dir = 'composite/'

    cued = stim_dir+dir+cued
    uncued = stim_dir+dir+uncued
    
    probe1 = visual.ImageStim(win, cued, size=7, name='CUED COMPOSITE '+cued, autoLog=True)
    probe1.setPos( [cued_position, 0] )

    probe2 = visual.ImageStim(win, uncued, size=7, name='UNCUED COMPOSITE '+uncued, autoLog=True)
    probe2.setPos( [-cued_position, 0] )

    return(probe1, probe2)

def probe_stim(win, cued_side, validity, text):
    """
    input: trial-wise cued side and validity
    output: attention check stimulus for display (with location, size, etc)
    """
    probe = visual.TextStim(win=win, ori=0, name='ATTENTION PROBE', text=text, font='Arial', height = 2, color='lightGrey',
            colorSpace='rgb', opacity=1, depth=0.0, autoLog=True)

    cued_position = cued_pos(cued_side, validity=validity)
    probe.setPos([cued_position, 0])
    return(probe)


def pause(win, frames):
    """
    Pauses experiment in given window (win) for 'frames' (int) number of frames
    input:  win    - psychopy visual window
            frames - number of frames (int)
    """
    for frame_n in range(frames):
        win.flip()

def memory_stim(win, image, stim_dir, practice=False, practice_single=False, practice_single_mem=False, practice_comp_mem=False):
    """
    Return single image stimulus for display in memory trial
    """
    if practice:
        image = stim_dir+'practice_composite/'+image
    elif practice_single:
        image = stim_dir+'practice_single/'+image
    elif practice_single_mem:
        image = stim_dir+'practice_mem_single/'+image
    elif practice_comp_mem:
        image = stim_dir+'practice_mem_composite/'+image
    else:
        image = stim_dir+'single/'+image

    im = visual.ImageStim(win, image, size=7, name='MEMORY IMAGE '+str(image), autoLog=True)
    im.setPos([0, 0])
    return(im)

def rating_pull(rating_tuple):
    '''
    Pulls subject's rating out of rating tuple
    input- rating scale tuple
    '''
    if len(rating_tuple)>1:
        rating = rating_tuple[1][0]
        rt = rating_tuple[1][1]
    else:
        rating = rating_tuple[0][0]
        rt = rating_tuple[0][1]
    return(rating, rt)

# Functions to Execute Presentation & Memory Runs

def presentation_run(win, run, pres_df, params, timing, paths):
    """
    Displays a full presentation run, saves out data to csv
    inputs:
        win     - visual window
        run     - run number (int)
        paths   - paths to subject-relevant directories (dictionary)
        params  - experiment parameters (dictionary)
        timing  - stimulus display times (dictionary)
        pres_df - all trial info for current presentation block (dataframe)
    """
    
    event.Mouse(visible=False)
    first_row = pres_df.index.values[0]

    # Create cue, fixation, and validity stim
    cue1, cue2 = cue_stim(win, pres_df['Cued Side'][first_row], pres_df['Cued Category'][first_row], paths['stim_path'])
    cue1.setPos( [0, 2] )
    cue2.setPos( [0, 0] )
    fixation = fix_stim(win)
    
    # create image pair and attention probe stim
    images_all = [composite_pair(win, pres_df['Cued Composite'].loc[trial],pres_df['Uncued Composite'].loc[trial], pres_df['Cued Side'][trial], paths['stim_path']) for trial in pres_df.index.values]
    circle_all = [probe_stim(win, pres_df['Cued Side'][trial], pres_df['Cue Validity'][trial], pres_df['Attention Probe'][trial]) for trial in pres_df.index.values]
    
    # set up ISI for timing precision
    ISI = core.StaticPeriod(screenHz=win.getActualFrameRate())
    
    # flip cues on
    cue1.setAutoDraw(True)
    cue2.setAutoDraw(True)
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : CUES ON')
    win.flip()
    
    # start 1s period
    ISI.start(1.5)   
    cue1.setAutoDraw(False)  
    cue2.setAutoDraw(False)
    fixation.setAutoDraw(True)
    logging.flush()
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : CUES OFF, FIXATION ON')
    ISI.complete()
    
    # flip cues off and fixation on
    win.flip()
    
    for idx,trial in enumerate(pres_df.index.values):
        
        ISI.start(1)  
        logging.flush()
        if idx>0:
            pres_df['Attention Response Time (s)'].loc[trial-1], pres_df['Attention Button'].loc[trial-1] = response[0][1],response[0][0]
        
        # composite images - 3 seconds
        images_all[idx][0].setAutoDraw(True)
        images_all[idx][1].setAutoDraw(True)
        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : COMPOSITES ON')
        ISI.complete() 
        
        win.flip()
        ISI.start(3)
        images_all[idx][0].setAutoDraw(False)
        images_all[idx][1].setAutoDraw(False)
        circle_all[idx].setAutoDraw(True)
        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : COMPOSITES OFF, ATTNTION PROBE ON')
        ISI.complete()
        win.flip()
        response = event.waitKeys(keyList = ['1','3'], timeStamped=True, clearEvents=True)
        
        # attention probe, until button press
        circle_all[idx].setAutoDraw(False)
        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : ATTENTION PROBE OFF')
        win.flip()
        
    fixation.setAutoDraw(False)
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION OFF')
    win.flip()
    
    #save data from last one
    pres_df['Attention Response Time (s)'].loc[trial], pres_df['Attention Button'].loc[trial] = response[0][1],response[0][0]
    pres_df.to_csv(paths['subject']+'pres'+str(run)+'.csv')


def memory_run(win, run, mem_df, params, timing, paths, test = False):
    
    """
    Displays full memory run, saves out data to csv
    inputs:
        win    - visual window
        run    - run number (int)
        paths  - paths to subject-relevant directories (dictionary)
        params - experiment parameters (dictionary)
        timing - stimulus display times (dictionary)
        mem_df - all trial info for current memory block (dataframe)
    """
    event.Mouse(visible=False)
    ISI = core.StaticPeriod(screenHz=win.getActualFrameRate())
    # set up ISI for timing precision
    
    # create fixation and image stimuli
    fixation = fix_stim(win)
    images = [memory_stim(win, mem_df['Memory Image'][x], paths['stim_path']) for x in mem_df.index.values] 

    # auto draw fixation
    fixation.setAutoDraw(True)
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION ON')

    # for every trial
    for idx,trial in enumerate(mem_df.index.values):
        # win flip (fixation on)
        win.flip()
        # start 1s period
        ISI.start(1.0) 
        # update memory csv
        if idx > 0 :
           mem_df["Familiarity Rating"].loc[trial-1],mem_df['Familiarity Reaction Time (s)'].loc[trial-1] = rating_pull(rating_scale.getHistory())

        # fixation auto draw False
        fixation.setAutoDraw(False)
        
        # create rating scale stim
        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4', 
        pos = [0,-.42], acceptPreText = '-',
        maxTime=2.0, minTime = 0, marker = 'triangle', showAccept=False, singleClick = True,
        disappear = False, markerStart=None, noMouse = True, markerColor = 'Black' )
        
        # update memory file
        mem_df.to_csv(paths['subject']+'mem'+str(run)+'.csv')
        
        # flush what we have so far to the log
        logging.flush()
        ISI.complete()
     
        event.getKeys(keyList = None)
        
        # start timer for displaying rating scale (2 seconds)
        rating_timer = core.CountdownTimer(2)
        
        rating_scale.setAutoDraw(True)
        images[idx].setAutoDraw(True)
        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION OFF, SCALE AND MEMORY ON')
        
        while rating_timer.getTime() > 0: # while time greater than the approx timing for a single flip
            # flip scale and image on
                    # auto draw scale and image, remover auto draw of fixation

            win.flip()
        
        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : SCALE AND MEMORY OFF, FIXATION ON')
        rating_scale.setAutoDraw(False)
        images[idx].setAutoDraw(False)
        fixation.setAutoDraw(True)
        #win.flip()
    
    fixation.setAutoDraw(False)
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION OFF')
    win.flip()
    
    # save from last trial
    mem_df["Familiarity Rating"].loc[trial],mem_df['Familiarity Reaction Time (s)'].loc[trial] = rating_pull(rating_scale.getHistory())
    mem_df.to_csv(paths['subject']+'mem'+str(run)+'.csv')


# Functions to Display Instruction Text and Practice Trials

def pract_text(trial):
    """
    input:  current practice trial # (int)
    output: practice instruction text (string) for given practice trial
    """

    intro = '\n\n Thank you for participating in this experiment! ' \
                    '\n\n In the experiment, you will pay attention to specific items on the screen.' \
                    '\n Then, we will test your memory for some of the items you have seen. ' \
                    '\n\n Press any key to continue... '

    # PRACTICE
    pract1 = ' You will see many images like the one below.' \
                    '\n You will need to pay special attention to either the FACE or SCENE. ' \
                    '\n\n\n\n\n\n\n\n\n\n\n\n\n\n Press any key to continue...'

    pract2 = ' Let\'s practice now! \n Look straight at the image and focus as hard as you can on the FACE. ' \
                    '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you can focus on the FACE well, press any key... '

    pract3 = ' Great job! ' \
                    '\n Now, focus as hard as you can on the SCENE. ' \
                    '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you can focus on the SCENE well, press any key... '

    pract4 = ' Next, you will see a cross and two images on the screen. ' \
                    '\n\n Keep your eyes staring straight at the cross, ' \
                    'but try to focus on the SCENE on the LEFT. ' \
                    '\n\n Only your attention should shift, not your eyes!' \
                    '\n You will not see the image perfectly clearly, just do your best, and feel free to ask questions!' \
                    '\n\n Press any key to begin. '

    pract5 = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you are done, press any key to continue... '

    pract6 = '\n\n Great job! ' \
                    '\n This time, keeping your eyes at center, try and focus on the FACE on the RIGHT.' \
                    '\n\n Press any key to begin.' \

    pract7 = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n When you are done, press any key to continue... '

    pract8 = ' Now, you will practice ' \
                    'attending to parts of images based on cue icons. ' \
                    '\n\n First, you\'ll see a pair of cue icons: ' \
                    '\n One arrow icon pointing left or right (< or >) ' \
                    ' and one image icon (face or scene): ' \
                    '\n\n\n\n\n\n After the cue icons, you will see several image pairs in a row. You\'ll attend to the SAME cued side and image part for EVERY pair.' \
                    ' Remember to keep your eyes fixated on the cross! ' \
                    '\n\n Press any key to begin.'

    pract9 = ' Great job, let\'s try it one more time!' \
                      '\n\n This time will be the same, but after each pair, a letter ("x" or "o") will appear on one side.' \
                      '\n When you see the letter, you should immediately press a button! ' \
                      '\n\n        If the "x" appears, press 1 ' \
                      '\n        If the "o" appears, press 3 ' \
                      '\n\n Remember to respond as quickly as you can!' \
                      '\n Press any key to begin.'

    pract10 = '\n\n Finally, you will practice reporting which images you remember. ' \
                    '\n You will use the following scale to rate individual images displayed on the screen: ' \
                    '\n\n        (1) I definitely have not seen the image before' \
                    '\n        (2) I probably have not seen the image before' \
                    '\n        (3) I probably have seen the image before' \
                    '\n        (4) I definitely have seen the image before' \
                    '\n\n You will need to respond quickly -- you\'ll have just 2 seconds!' \
                    '\n\n When you\'re ready to begin, press any key.'

    instructions = [intro, pract1, pract2, pract3, pract4, pract5, pract6, pract7, pract8, pract9, pract10]

    return(instructions[trial])

def mem_text(trial):
    """
    input:  current memory trial # (int)
    output: memory instruction text (string) for given memory trial
    """

    mem1 = ' Now we\'re going to test your memory. ' \
                    '\n Just like the practice round, you will rate single images using the following scale: ' \
                    '\n\n (1) I definitely have not seen the image before' \
                    '\n (2) I probably have not seen the image before' \
                    '\n (3) I probably have seen the image before' \
                    '\n (4) I definitely have seen the image before' \
                    '\n\n You will need to make your responses quickly -- you\'ll have just 2 seconds. ' \
                    ' If you aren\'t sure what to say for a particular image, make your best guess! ' \
                    '\n\n Press any key to begin.'

    mem2 = ' MEMORY BLOCK. ' \
                    '\n\n Press any key to begin.'

    instructions = [mem1, mem2]

    if trial >= 1:
        num = 1
    else:
        num = 0

    return(instructions[num])

def pres_text(trial):
    """
    input:  current presentation trial # (int)
    output: presentation instruction text (string) for given presentation trial
    """
    pres1 = ' Now we will begin the main experiment! ' \
                    'Again you will see cue icons, followed by a series of image pairs and letters (and a fixation cross).' \
                    '\n\n Remember to: ' \
                    '\n\n        Keep your eyes staring at the cross' \
                    '\n        Shift your attention to the SAME cued side and part for EACH pair' \
                    '\n        Immeditaely press 1 ("x") or 3 ("o") when you see the letter ' \
                    '\n\n Do you have questions? Ask them now! ' \
                    '\n Otherwise, position your hand over the 1 and 3 buttons, clear your mind, and press any key to begin. '

    pres2 = ' Feel free to take a moment to rest, if you like! ' \
                    ' When you\'re ready, we will do another round with a cue, followed by image pairs and letters.' \
                    ' \n\n Remember to: ' \
                    '\n Keep your eyes staring at the cross' \
                    '\n Shift your attention to the SAME cued side and part for EACH pair' \
                    '\n Immeditaely press 1 ("x") or 3 ("o") when you see the letter ' \
                    '\n\n Press any key to begin. '

    instructions = [pres1, pres2]

    if trial >= 1:
        num = 1
    else:
        num = 0

    return(instructions[num])


def text_present(win, text, close=False, timing=None):
    '''
    Displays text on screen, until button press
    input: window (psychopy object) and text (str)
    '''
    instruction = visual.TextStim(win, text=text, wrapWidth=40, name='INSTRCUCTION TEXT')
    instruction.setAutoDraw(True)
    win.flip()
    
    key = event.waitKeys(keyList=None)
    
    if close:
        pause(win, timing['pause'])
        win.close()
    else:
        instruction.setAutoDraw(False)
        win.flip()

def practice_instructions(win, paths, text, pract_run, timing, acceptedKeys = [], practice=False, cat = 'cat', sid = 'sid'):
    '''
    Sequentially presents instruction text, images, and practice trials
    '''

    # make list of stim for this practice_round
    cat_cues = [paths['stim_path']+'cue/'+x for x in ['Face.png', 'Place.png']]
    composites = os.listdir(paths['stim_path']+'practice_composite')
    singles = os.listdir(paths['stim_path']+'practice_single')
    
    mem_composites = os.listdir(paths['stim_path']+'practice_mem_composite')
    l = os.listdir(paths['stim_path']+'practice_mem_single')
    mem_single = random.sample(l, k=len(l))
    
    instruction = visual.TextStim(win, text=text, wrapWidth=40)
    ims = [instruction]

    # center composite
    if pract_run in [1,2,3]:
        ims.append(memory_stim(win, composites[pract_run-1], paths['stim_path'], practice=True))

    # composite pair, fixation
    elif pract_run in [5,7]:
        image1,image2 = [composites[pract_run-1], composites[pract_run-2]]
        ims.extend(composite_pair(win, composites[pract_run-1], composites[pract_run-2], '>', paths['stim_path'], practice=True))
        ims.append(fix_stim(win))

    # face cue, place cue
    elif pract_run == 8:
        for x,pos in zip(cat_cues, [2.5, -2.5]):
            cue = visual.ImageStim(win, x, size=2, autoLog=True, name = 'CATEGORY CUE')
            cue.setPos([pos, 0])
            ims.append(cue)

    # display stim until button press
    for x in ims:
        x.setAutoDraw(True)

    win.flip()
    
    event.waitKeys(keyList=None)

    for x in ims:
        x.setAutoDraw(False)
    win.flip()

    # dynamic practice trials
    # pract_pres1
    if pract_run ==8:
        pract_pres(win, paths, composites[-6:], timing, circle=False, cat = cat, sid = sid)

    # pract_pres2
    if pract_run == 9:
        pract_pres(win, paths, mem_composites, timing, circle=True, cat = cat, sid = sid, mem=True)

    # pract_mem
    elif pract_run == 10:
        pract_mem(win, mem_single, paths, timing)

def pract_pres(win, paths, im_list, timing, circle=False, cat = 'cat', sid= 'sid', mem=False):
    """
    Present dynamic practice presentation runs
    """
    
    event.Mouse(visible=False)
    # set up ISI for timing precision
    ISI = core.StaticPeriod(screenHz=win.getActualFrameRate())
    
    fix = fix_stim(win)
    
    cue1, cue2 = cue_stim(win, sid, cat, paths['stim_path'])
    cue1.setPos([0, 2])
    cue2.setPos([0, 0])
    cue1.setAutoDraw(True)
    cue2.setAutoDraw(True)
    win.flip()
    
    ISI.start(1.5)
    cue1.setAutoDraw(False)
    cue2.setAutoDraw(False)
    fix.setAutoDraw(True)
    ISI.complete()
    
    win.flip()
    ISI.start(1)

    text=[random.choice(['x','o']) for _ in range(3)]
    validity_list = random.sample([1, 1, 0], k=3)
    
    if mem == False:
        stims = [composite_pair(win, im_list[x*2], im_list[x*2+1], sid, paths['stim_path'], practice=True) for x in range(3)]
    
    else:
        stims = [composite_pair(win, im_list[x*2], im_list[x*2+1], sid, paths['stim_path'], mem_practice=True) for x in range(3)]

    for idx,x in enumerate(range(3)):
        
        stims[idx][0].setAutoDraw(True)
        stims[idx][1].setAutoDraw(True)
        ISI.complete()
        win.flip()
        
        ISI.start(3)
        
        if circle:
            circle = probe_stim(win, sid, validity_list[x], text=text[x])
            circle.setAutoDraw(True)
                    
        stims[idx][0].setAutoDraw(False)
        stims[idx][1].setAutoDraw(False)
        ISI.complete()
        win.flip()
        
        if circle:
            response = event.waitKeys(keyList = ['1','3'], timeStamped=True, clearEvents=True)
        
            # attention probe, until button press
            circle.setAutoDraw(False)
            win.logOnFlip(level=logging.EXP, msg='WIN FLIP : ATTENTION PROBE OFF')
            win.flip()
        
        ISI.start(1)
        
    fix.setAutoDraw(False)


def pract_mem(win, im_list, paths, timing):
    """
    Display dynamic practice memory runs
    """
    event.Mouse(visible=False)
    fixation = fix_stim(win)     
        
    ISI = core.StaticPeriod(screenHz=win.getActualFrameRate())
    # set up ISI for timing precision
    
    # create fixation and image stimuli
    fixation = fix_stim(win)
    images = [memory_stim(win, x, paths['stim_path'], practice_single_mem=True) for x in im_list] 

    # auto draw fixation
    fixation.setAutoDraw(True)
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION ON')

    # for every trial
    for idx,trial in enumerate(range(4)):
        
        # win flip (fixation on)
        win.flip()
        
        # start 1s period
        ISI.start(1.0) 
        
        # update memory csv
        #if idx > 0 :
        #   mem_df["Familiarity Rating"].loc[trial-1],mem_df['Familiarity Reaction Time (s)'].loc[trial-1] = rating_pull(rating_scale.getHistory())

        # fixation auto draw False
        fixation.setAutoDraw(False)
        
        # create rating scale stim
        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4', 
        pos = [0,-.42], acceptPreText = '-',
        maxTime=2.0, minTime = 0, marker = 'triangle', showAccept=False, singleClick = True,
        disappear = False, noMouse=True, markerStart=None, markerColor='Black' )

        # auto draw scale and image, remover auto draw of fixation
        rating_scale.setAutoDraw(True)
        images[idx].setAutoDraw(True)
        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION OFF, SCALE AND MEMORY ON')
        
        # flush what we have so far to the log
        logging.flush()
        ISI.complete()
     
        event.getKeys(keyList = None)
        # start timer for displaying rating scale (2 seconds)
        rating_timer = core.CountdownTimer(2)
        while rating_timer.getTime() > .016: # while time greater than the timing for a single flip
            # flip scale and image on
            win.flip()

        win.logOnFlip(level=logging.EXP, msg='WIN FLIP : SCALE AND MEMORY OFF, FIXATION ON')
        rating_scale.setAutoDraw(False)
        images[idx].setAutoDraw(False)
        fixation.setAutoDraw(True)
        #win.flip()
    
    fixation.setAutoDraw(False)
    win.logOnFlip(level=logging.EXP, msg='WIN FLIP : FIXATION OFF')
    win.flip()


