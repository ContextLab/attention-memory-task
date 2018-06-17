# helper functions for attention and memory experiment

import pandas as pd
from psychopy import visual, event, core, data, gui, logging
from analysis_helpers import *
import random
import os
import time

# Data entry, organization, trial setup functions

def subject_info(header, data_path, path_only=False):
    '''
    Create pop up box to obtain subject# and run#
    Save out subject directory
    '''

    info = {}
    info['participant'] = ''
    info['run'] = ''
    dlg = gui.DlgFromDict(info)

    if not dlg.OK:
        core.quit()

    subject_directory(info, data_path)
    return(info)

def subject_directory(info, data_path, path_only=False):
    '''
    Creates subject directory if does not exist
    '''

    dir_name = data_path + str(info['participant']) + '_' + data.getDateStr()[0:11] + '/'

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        return(dir_name)
    else:
        return(dir_name)
        if not path_only:
            print('WARNING: subject directory exists already!')

def pre_questionnaire(info, save=True, save_path='.'):
    '''
    Create pop up box to obtain and save subject's demographic info

    :param info: dictionary containing participant# and run#
    :param save: boolean indicating whether to autosave
    :param save_path: if save==True, path to data save location

    :return: if save==True, save out data, return nothing
             if save==False, return questionnaire data
    '''

    preDlg = gui.Dlg()

    # second pop up (demographic info)
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
    preDlg.addField('5. Highest Degree Achieved:', choices = ['--', 'some high school', 'high schoool graduate', 'some college', \
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

    dlg = gui.DlgFromDict(info)

    if not dlg.OK:
        core.quit()
    end_data = preDlg.show()

    if save == True:
        name = save_path + 'pre_questionnaire_' + info['participant'] + '.pkl'
        with open(name, 'wb') as f:
            pickle.dump(end_data, f)
    else:
        return(end_data)

def post_questionnaire(info, save=True, save_path='.'):
    '''
    Create pop up box to obtain and save subject's post-study info

    :param info: dictionary containing participant# and run#
    :param save: boolean indicating whether to autosave
    :param save_path: if save==True, path to data save location

    :return: if save==True, save out data, return nothing
             if save==False, return questionnaire data
    '''

    # end of task questionnaire
    postDlg = gui.Dlg(title="Post Questionnaire")
    postDlg.addField('1. How engaging did you find this experiment?', choices=['--', "Very engaging", "A little engaging", "Neutral", "A little boring", "Very boring"])
    postDlg.addField('2. How tired do you feel?', choices=['--', "Very tired", "A little tired", "Neutral", "A little alert", "Very alert"])
    postDlg.addField('3. Did you find one category easier to remember? If so, which one and why?')
    postDlg.addField('4. Did you find one side easier to attend to? If so, which one?')
    postDlg.addField('5. What strategies did you use (if any) to help remember the attended images?')

    if not dlg.OK:
        core.quit()
    end_data = preDlg.show()

    if save == True:
        name = save_path + 'post_questionnaire_' + info['participant'] + '.pkl'
        with open(name, 'wb') as f:
            pickle.dump(end_data, f)
    else:
        return(end_data)

def cue_create(params):
    '''
    return three lists, total-tirals-in-experiment long, assigning cued side,
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
    chunk_tuples = [cue_tuples_0[i:i+presentations_per_run] for i in range(0, len(cue_tuples_0), presentations_per_run)]

    # while any blocks repeat cues back-to-back, reshuffle
    cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))
    reshuffle = True

    while reshuffle==True:
        for idx,x in enumerate(cue_tuples[1:-1]):
            if x[0]==cue_tuples[idx+1][0] or x[0]==cue_tuples[idx-1][0]:
                cue_tuples = random.sample(chunk_tuples, len(chunk_tuples))
                pass
            elif idx==len(cue_tuples[1:-1])-1 and not (x[0]==cue_tuples[idx+1][0] or x[0]==cue_tuples[idx-1][0]):
                reshuffle=False

    cue_tuples = flatten(cue_tuples)
    final = [[x[0] for x in cue_tuples],[x[1] for x in cue_tuples],validity]

    # return list for each
    return(final)

def trial_setup(params):
    '''
    returns lists to assign subject number, run number, and trial type to every row
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
    returns dict with keys 'Cued' and 'Uncued', each containing three lists (composites, single places, and single faces)
    '''
    images = {}
    cued = presentation[0:int(len(presentation)/2)]
    uncued = presentation[int(len(presentation)/2):]

    for x,y in zip(['Cued','Uncued'],[cued, uncued]):
        images[x] = {'composite':y, 'place':img_split(y, cat=True)['place_im'], 'face':img_split(y, cat=True)['face_im']}

    return(images)

def group_it(data, num):
    return([data[i:i+num] for i in range(0, len(data), num)])

def memory_images(presentation, memory):
    '''
    returns list of memory images, half novel and half previously seen
    '''

    # parse the presented and mem_only images
    cued = presentation[0:int(len(presentation)/2)]
    uncued = presentation[int(len(presentation)/2):]
    memory_face = img_split(memory, cat=True)['face_im']
    memory_place = img_split(memory, cat=True)['place_im']

    # group by trials
    cued = group_it(cued, 10)
    uncued = group_it(uncued, 10)
    memory_face = group_it(memory_face, 10)
    memory_place = group_it(memory_place, 10)

    # append the split singles from all selected images (1/2 prev seen, and all chosen for memory)
    singles = []
    for x in range(len(cued)):
        singles.extend(img_split(random.sample(cued[x],int(len(cued[x])/2))))
        singles.extend(img_split(random.sample(uncued[x],int(len(uncued[x])/2))))
        singles.extend(memory_face[x])
        singles.extend(memory_place[x])
    singles = random.sample(singles, len(singles))

    return(singles)

def initialize_df(info, categories, paths, subject_directory, params, save=True):
    '''
    Creates trial x parameter dataframe for all trials (presentation and memory) for a single subject,
    including all trial-wise parameters, and empty cells (None type) for experimental data
    '''

    total_pres = params['presentations_per_run']*params['runs']

    # create column names
    columns = ['Subject', 'Trial Type', 'Run', 'Cued Composite', 'Uncued Composite', 'Cued Face',
                'Cued Place', 'Uncued Face', 'Uncued Place', 'Memory Image', 'Category', 'Cued Side',
                'Cued Category', 'Attention Reaction Time (s)', 'Familiarity Reaction Time (s)',
                'Familiarity Rating', 'Attention Level', 'Cue Validity', 'Post Invalid Cue', 'Pre Invalid Cue']

    df = pd.DataFrame(index = range(total_pres*5), columns=columns)

    # add subject#, run#, trial types, cues
    df['Subject'] = info['participant']
    df['Run'],df['Trial Type'] = trial_setup(params)
    mask = df['Trial Type']=='Presentation'
    df.loc[mask,'Cued Side'],df.loc[mask,'Cued Category'],df.loc[mask,'Cue Validity'] = cue_create(params)

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
    df.loc[mask2, 'Memory Image']= memory_images(presentation, memory)

    # save dataframe
    df.to_csv('intial_df')

    return(df)


# Visual stim creation & presentation

def cue_stim(win, side, category, stim_dir):
    '''
    inputs: presentation trial #, cue side, cue cat
    outputs: appropriate cue or fixation stim for center screen
    '''

    stim1 = visual.ImageStim(win, image=stim_dir+'cue/'+category+'.png', size=2) #, name=category+'_icon')
    #stim1.setPos([-2.5, 0])

    stim2 = visual.TextStim(win=win, ori=0, name='cue_side', text = side, font='Arial',
            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

    return([stim1,stim2])

def fix_stim(win):
    stim1 = visual.TextStim(win=win, ori=0, name='fixation_cross', text='+', font='Arial',
                  height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)
    return(stim1)

# def probe_stim(win):
#     probe = visual.TextStim(win=win, ori=0, name='posner', text='o', font='Arial', height = 2, color='lightGrey',
#             colorSpace='rgb', opacity=1, depth=0.0)
#     return(probe)

def cued_pos(side, validity=True):

    if side == '>' and validity==True:
        pos = 8
    if side == '>' and validity==False:
        pos = -8
    if side == '<' and validity==True:
        pos = -8
    else:
        pos = 8

    return(pos)

def composite_pair(win, cued, uncued, side, stim_dir):
    cued_position = cued_pos(side)

    cued = stim_dir+'composite/'+cued
    uncued = stim_dir+'composite/'+uncued
    probe_size=7

    probe1 = visual.ImageStim(win, cued, size=probe_size, name='Probe1')
    probe1.setPos( [cued_position, 0] )

    probe2 = visual.ImageStim(win, uncued, size=probe_size, name='Probe2')
    probe2.setPos( [-cued_position, 0] )

    return(probe1, probe2)

def probe_stim(win, cued_side, validity):
    probe = visual.TextStim(win=win, ori=0, name='posner', text='o', font='Arial', height = 2, color='lightGrey',
            colorSpace='rgb', opacity=1, depth=0.0)

    cued_position = cued_pos(cued_side, validity=validity)
    probe.setPos([cued_position, 0])
    return(probe)

def display(win, stim_list, frames, accepted_keys=None):
    rt = None

    for x in stim_list:
        x.setAutoDraw(True)

    if type(accepted_keys)==list:
        resp_clock = core.Clock()
        win.callOnFlip(resp_clock.reset)
        event.clearEvents()

    for frame_n in range(frames):
        if type(accepted_keys)==list:
            if frame_n == 0:
                keys = event.getKeys(keyList = accepted_keys)
            if len(keys) > 0:
                rt = resp_clock.getTime()
                resp = keys[0]
                break
        win.flip()

    for x in stim_list:
        x.setAutoDraw(False)

    win.flip()
    return(rt)

def pause(win, frames):

    for frame_n in range(frames):
        win.flip()




# Presentation run

def presentation_run(win, pres_df, params, timing, paths, test = False):

    # Create cue, fixation, and validity stim
    cue1, cue2 = cue_stim(win, pres_df['Cued Side'][0], pres_df['Cued Category'][0], paths['stim_path'])
    cue1.setPos( [0, 2] )
    cue2.setPos( [0, 0] )
    fixation = fix_stim(win)
    #probe = probe_stim(win)

    # flash cue
    display(win, [cue1,cue2], timing['cue'])
    #display(win, [probe], timing['cue'], accepted_buttons=[])
    pause(win, timing['pause'])

    # start fixation
    fixation.setAutoDraw(True)

    for trial in pres_df.index.values:
        # make stim
        images = composite_pair(win, pres_df['Cued Composite'].loc[trial],pres_df['Uncued Composite'].loc[trial], pres_df['Cued Side'][trial], paths['stim_path'])
        circle = probe_stim(win, pres_df['Cued Side'][trial], pres_df['Cue Validity'][trial])

        # display stim
        display(win, images, timing['probe'])
        pres_df['Attention Reaction Time (s)'].loc[trial] = display(win, [circle], timing['probe'], accepted_keys=[])
        # accepted_keys = [] accepts keypress from any button
        pause(win, timing['pause'])




# Memory run







#def image_stimuli(data, composite=True, number=2):

#def rating_scale():

def show_instructions(practice_round = 'cue_pos1', acceptedKeys = None):
    '''
    Displays instruction text and instruction images that are not part of a practice loop

    :param practice_round: indicates which text and image(s) to display
    '''

    # Set and display text
    instruction = visual.TextStim(win, text=text, wrapWidth=40)
    instruction.setAutoDraw(True)
    win.flip()

    # if cue_pos1, show icons
    if practice_round == 'cue_pos1':
        cat_inst_1 = visual.ImageStim(win, cue_pic1, size=cue_size, name='cue_img1')
        cat_inst_2 = visual.ImageStim(win, cue_pic2, size=cue_size, name='cue_img2')
        cat_inst_2.setPos([-2.5, 0])
        cat_inst_1.setPos([2.5, 0])
        cat_inst_1.setAutoDraw(True)
        cat_inst_2.setAutoDraw(True)
        win.flip()

    # if cue_pos2, show single example icon and arrow
    elif practice_round == 'cue_pos2':
        cat_inst_1 = visual.ImageStim(win, cue_pic2, size=cue_size, name='cue_img2')
        cat_inst_1.setPos([0, 3])

        cue_inst_right = visual.TextStim(win=win, ori=0, name='cue_right', text='>', font='Arial',
                            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

        cue_inst_right.setPos([0, 1])
        cue_inst_right.setAutoDraw(True)
        cat_inst_1.setAutoDraw(True)
        win.flip()

    elif practice_round == 'center_image1':
        center = visual.ImageStim(win, '../../stim/hybrid_1_F/00060931230fa_sunaaehaikpckyjsety.jpg', size = probe_size)
        center.setAutoDraw(True)
        win.flip()

    elif practice_round == 'hybrid_pair':
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

    if practice_round == 'cue_pos1':
        cat_inst_1.setAutoDraw(False)
        cat_inst_2.setAutoDraw(False)

    elif practice_round == 'cue_pos2':
        cat_inst_1.setAutoDraw(False)
        cue_inst_right.setAutoDraw(False)

    elif practice_round == 'hybrid_pair':
        hybrid1.setAutoDraw(False)
        hybrid2.setAutoDraw(False)
        fixation.setAutoDraw(False)

    elif practice_round == 'center_image':
        center.setAutoDraw(False)

    win.flip()




# Trial block funcions

# def practice_block(loop = object):
#     '''
#     Displays practice trials
#
#     :params loop: loop object psychopy iterates over for trials
#     '''
#
#     instr_dict =  {1: instruct_pract1, 2: instruct_pract2, 3: instruct_pract3, 4: instruct_pract4, 5: instruct_pract5, 6: instruct_pract6, 7: instruct_pract7, 8: instruct_pract8, 9:instruct_pract9, 10: instruct_pract10}
#     trial_count = 1
#     previously_practiced = []
#     cue_pract_prev = []
#
#     for this_trial in loop:
#         # select instructions
#         this_instruct = instr_dict[trial_count]
#
#         # display text for practice instructions
#         if trial_count in [1,2,3]:
#             show_instructions(text = this_instruct, practice_round = 'center_image1', acceptedKeys = None)
#         elif trial_count in [5,7]:
#             show_instructions(text = this_instruct, practice_round = 'hybrid_pair', acceptedKeys = None)
#         elif trial_count in [8]:
#             show_instructions(text = this_instruct, practice_round = 'cue_pos1', acceptedKeys = None)
#         else:
#             show_instructions(text = this_instruct, acceptedKeys = None)
#
#         # PRACTICE BLOCKS AFTER TEXT INSTRUCTION
#         if trial_count == 8:
#             # presentation block, w/cue, no (o) x4
#             practice_trials1 = data.TrialHandler(trialList = [{}]*(4), nReps = 1)
#             pract_pres1(practice_trials1)
#
#         if trial_count == 9:
#             # presentation block w/cue, w/(o) x4
#             practice_trials1 = data.TrialHandler(trialList = [{}]*(4), nReps = 1)
#             pract_pres2(practice_trials1)
#
#         if trial_count == 10:
#             # memory block x4
#             practice_trials1 = data.TrialHandler(trialList = [{}]*(4), nReps = 1)
#             pract_mem(practice_trials1)
#
#         trial_count += 1
#
# def presentation_block(df, practice=False):
#
# def memory_block(df, practice=False):
