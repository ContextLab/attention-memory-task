# HELPER FUNCTIONS FOR ATTENTION AND MEMORY EXPERIMENT

# Imports
import pandas as pd
from psychopy import visual, event, core, data, gui, logging
from analysis_helpers import *
import random
import os
import time
import matplotlib.pyplot as plt

# Tiny helpers
def group_it(data, num):
    '''
    input: list of data items of any types
    output: ordered list of length num sublists of inputted data
    '''
    return([data[i:i+num] for i in range(0, len(data), num)])

def flatten(the_list):
    '''
    input: list of lists
    output: single list containing all data, ordered, from nested lists
    '''
    return([val for sublist in the_list for val in sublist])

# Data entry & organization functions

def subject_info(header, data_path, path_only=False):
    '''
    Create pop up box to obtain subject# and run#
    Create subject directory, if not already existing
    '''

    info = {}
    info['participant'] = ''
    info['run'] = ''
    dlg = gui.DlgFromDict(info)

    # if not dlg.OK:
    #     core.quit()

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

# Functions for Creating Trial Parameters & Visual Stimuli

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

def img_split(image_list, cat = False):
    '''
    splits overlay image filenames into filenames of the original, single images

    input : list of image filenames
    output : list of image filenames OR two lists, separated by category

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
                'Familiarity Rating', 'Attention Level', 'Cue Validity', 'Post Invalid Cue', 'Pre Invalid Cue',
                'Attention Button', 'Rating History', 'Stimulus Onset', 'Stimulus End']

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
    df.loc[mask2, 'Memory Image']= memory_image(presentation, memory)

    # save dataframe
    df.to_csv(paths['subject']+'intial_df.csv')
    return(df)

def cue_stim(win, side, category, stim_dir):
    '''
    inputs: win, cue side, cue cat, stimulus directory
    outputs: appropriate cue or fixation stim for center screen
    '''

    stim1 = visual.ImageStim(win, image=stim_dir+'cue/'+category+'.png', size=2) #, name=category+'_icon')
    #stim1.setPos([-2.5, 0])

    stim2 = visual.TextStim(win=win, ori=0, name='cue_side', text = side, font='Arial',
            height=2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)

    return([stim1,stim2])

def fix_stim(win):
    """
    returns fixation stimulus for display in window
    """
    stim1 = visual.TextStim(win=win, ori=0, name='fixation_cross', text='+', font='Arial',
                  height = 2, color='lightGrey', colorSpace='rgb', opacity=1, depth=0.0)
    return(stim1)

def cued_pos(side, validity=True):
    """
    input: cued side in this trial (string), desired stimulus validity (bool)
    output: x-axis screen location for the stimulus (int)
    """

    if side == '>' and validity==True:
        pos = 8
    if side == '>' and validity==False:
        pos = -8
    if side == '<' and validity==True:
        pos = -8
    else:
        pos = 8

    return(pos)

def composite_pair(win, cued, uncued, side, stim_dir, practice=False):
    """
    returns list of two composite image stimuli (with stim location, size, etc)
    for display in presentation trial
    """
    cued_position = cued_pos(side)

    if practice:
        dir = 'practice_composite/'
    else:
        dir = 'composite/'

    cued = stim_dir+dir+cued
    uncued = stim_dir+dir+uncued

    probe1 = visual.ImageStim(win, cued, size=7, name='Probe1')
    probe1.setPos( [cued_position, 0] )

    probe2 = visual.ImageStim(win, uncued, size=7, name='Probe2')
    probe2.setPos( [-cued_position, 0] )

    return(probe1, probe2)

def probe_stim(win, cued_side, validity):
    """
    input: trial-wise cued side and validity
    output: attention check stimulus for display (with location, size, etc)
    """
    probe = visual.TextStim(win=win, ori=0, name='posner', text='o', font='Arial', height = 2, color='lightGrey',
            colorSpace='rgb', opacity=1, depth=0.0)

    cued_position = cued_pos(cued_side, validity=validity)
    probe.setPos([cued_position, 0])
    return(probe)

def display(win, stim_list, frames, accepted_keys=None, trial=0, df=None):
    """
    inputs:
        win - visual window
        stim_list - list of psychopy visual Stimuli
        frames - int
        accepted_keys - list of strings, or None
        trial - int
        df - pandas dataframe of trial information

    displays all stimuli in window simultaneously.
    if accepted_keys list passed, displays until key press; else, displays for 'frames' number of frames
    if both dataframe and trial# passed, saves reaction time to coorresponding trial row in df
    """

    rt = None
    resp = None

    for x in stim_list:
        x.setAutoDraw(True)

    if type(accepted_keys)==list:
        resp_clock = core.Clock()
        win.callOnFlip(resp_clock.reset)
        event.clearEvents()

    for frame_n in range(frames):

        absolute_time = time.time()

        if df is not None:
            if frame_n == 0:
                df.loc[trial, 'Stimulus Start'] = absolute_time
            if frame_n == range(frames)[-1]:
                df.loc[trial, 'Stimulus End'] = absolute_time

        if type(accepted_keys)==list:
            if frame_n == 0:
                resp_clock.reset()
                keys = event.getKeys(keyList = accepted_keys)
            if len(keys) > 0:
                resp = keys[0]
                rt = resp_clock.getTime()
                break

            win.flip()
            for x in stim_list:
                x.setAutoDraw(False)

            # if no response, wait until response
            if resp == None:
                keys = event.waitKeys(keyList = accepted_keys)
                resp = keys[0]
                rt = resp_clock.getTime()

            win.flip()

        else:
            win.flip()

    win.flip()
    for x in stim_list:
        x.setAutoDraw(False)

        if type(x) is visual.RatingScale:
            choice_history = x.getHistory()
            df["Familiarity Rating"].loc[trial],df['Familiarity Reaction Time (s)'].loc[trial] = rating_pull(choice_history)

    return([rt, resp])

def pause(win, frames):
    """
    pauses experiment in given window (win) for 'frames' (int) number of frames
    without affecting the stimuli on display
    """
    for frame_n in range(frames):
        win.flip()

def memory_stim(win, image, stim_dir, practice=False, practice_single=False):
    """
    return single image stimulus for display in memory trial
    """
    if practice:
        image = stim_dir+'practice_composite/'+image
    elif practice_single:
        image = stim_dir+'practice_single/'+image
    else:
        image = stim_dir+'single/'+image

    im = visual.ImageStim(win, image, size=7, name='mem_image')
    im.setPos([0, 0])
    return(im)

def rating_pull(rating_tuple):
    '''
    pulls subject's rating out of rating tuple
    '''
    if len(rating_tuple)>1:
        rating = rating_tuple[1][0]
        rt = rating_tuple[1][1]
    else:
        rating = rating_tuple[0][0]
        rt = rating_tuple[0][1]
    return(rating, rt)

# Functions to Execute Presentation & Memory Runs

def presentation_run(win, run, pres_df, params, timing, paths, loop = object, test = False):
    """
    displays a full presentation run, saves out data
    """

    first_row = pres_df.index.values[0]

    # Create cue, fixation, and validity stim
    cue1, cue2 = cue_stim(win, pres_df['Cued Side'][first_row], pres_df['Cued Category'][first_row], paths['stim_path'])
    cue1.setPos( [0, 2] )
    cue2.setPos( [0, 0] )
    fixation = fix_stim(win)

    # flash cue
    display(win, [cue1,cue2], timing['cue'])
    pause(win, timing['pause'])

    # start fixation
    fixation.setAutoDraw(True)

    for trial in pres_df.index.values:

        # make stim
        images = composite_pair(win, pres_df['Cued Composite'].loc[trial],pres_df['Uncued Composite'].loc[trial], pres_df['Cued Side'][trial], paths['stim_path'])
        circle = probe_stim(win, pres_df['Cued Side'][trial], pres_df['Cue Validity'][trial])

        # display stim
        display(win, images, timing['probe'], accepted_keys=None, trial=trial, df=pres_df)
        pres_df['Attention Reaction Time (s)'].loc[trial], pres_df['Attention Button'].loc[trial] = display(win, [circle], timing['probe'], accepted_keys=['1','3'])
        pause(win, timing['pause'])

        pres_df.to_csv(paths['subject']+'pres'+str(run)+'.csv')

    fixation.setAutoDraw(False)

def memory_run(win, run, mem_df, params, timing, paths, test = False):
    """
    displays full memory run, saves out data
    """
    fixation = fix_stim(win)

    for trial in mem_df.index.values:

        display(win, [fixation], timing['pause'])

        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4',
                                            singleClick = True, pos = [0,-.42], acceptPreText = '-',
                                            maxTime=3.0, minTime=0, marker = 'triangle', showAccept=False, acceptSize=0)

        resp_clock = core.Clock()
        im_path = paths['stim_path']+'single/'+mem_df['Memory Image']
        image = memory_stim(win, mem_df['Memory Image'][trial], paths['stim_path'])

        # display(win, [fixation], timing['pause'])
        display(win, [image, rating_scale], timing['mem'], accepted_keys=None, trial=trial, df=mem_df)
        mem_df.to_csv(paths['subject']+'mem'+str(run)+'.csv')


# Functions to Display Instruction Text and Practice Trials

def pract_text(trial):
    """
    returns practice instruction text (string) for given practice trial, 'trial' (int)
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
                      '\n\n This time will be the same, but after each pair, a circle (o) will appear.' \
                      '\n When you see the circle, you should immediately press a button! ' \
                      '\n\n        If the circle appears on the LEFT, press 1 ' \
                      '\n        If the circle appears on the RIGHT, press 3 ' \
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
    returns memory instruction text (string) for given practice trial, 'trial' (int)
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

        return(instructions[trial])

def pres_text(trial):
    """
    returns presentation trial text (string) for given practice trial, 'trial' (int)
    """

    pres1 = ' Now we will begin the main experiment! ' \
                    'Again you will see cue icons, followed by a series of image pairs and circles (and a fixation cross).' \
                    '\n\n Remember to: ' \
                    '\n\n        Keep your eyes staring at the cross' \
                    '\n        Shift your attention to the SAME cued side and part for EACH pair' \
                    '\n        Immeditaely press 1 (Left) or 3 (Right) when you see the circle (o) ' \
                    '\n\n Do you have questions? Ask them now! ' \
                    '\n Otherwise, position your hand over the 1 and 3 buttons, clear your mind, and press any key to begin. '

    pres2 = ' Feel free to take a moment to rest, if you like! ' \
                    ' When you\'re ready, we will do another round with a cue, followed by image pairs and circles (o).' \
                    ' \n\n Remember to: ' \
                    '\n Keep your eyes staring at the cross' \
                    '\n Shift your attention to the SAME cued side and part for EACH pair' \
                    '\n Immeditaely press 1 (Left) or 3 (Right) when you see the circle (o) ' \
                    '\n\n Press any key to begin. '

    instructions = [pres1, pres2]

    if trial >= 1:
        num = 1
    else:
        num = 0

    return(instructions[num])

def thank_text():
        """
        returns closing message text (str)
        """
    thanks = 'Thank you for your participation! '
    return(thanks)

def text_present(win, text):

    instruction = visual.TextStim(win, text=text, wrapWidth=40)
    instruction.setAutoDraw(True)
    win.flip()

    event.waitKeys(keyList=None)
    instruction.setAutoDraw(False)
    win.flip()

def practice_instructions(win, paths, text, pract_run, timing, acceptedKeys = [], practice=False):
    '''
    Displays instruction text and instruction images that are not part of a practice loop
    :param practice_round: indicates which text and image(s) to display
    '''

    # make list of stim for this practice_round
    cat_cues = [paths['stim_path']+'cue/'+x for x in ['Face.png', 'Place.png']]
    composites = os.listdir(paths['stim_path']+'practice_composite')
    singles = os.listdir(paths['stim_path']+'practice_single')
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
            cue = visual.ImageStim(win, x, size=2)
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
        pract_pres(win, paths, composites[-12:-6], timing, circle=False)

    # pract_pres2
    if pract_run == 9:
        pract_pres(win, paths, composites[-6:], timing, circle=True)

    # pract_mem
    elif pract_run == 10:
        pract_mem(win, singles, paths, timing)

def pract_pres(win, paths, im_list, timing, circle=False):
    """
    display practice presentation runs
    """

    cue1, cue2 = cue_stim(win, '>', 'Face', paths['stim_path'])

    cue1.setPos([0, 2])
    cue2.setPos([0, 0])

    display(win, [cue1,cue2], timing['cue'])
    pause(win, timing['pause'])

    fix = fix_stim(win)
    fix.setAutoDraw(True)

    for x in range(3):
        stim = composite_pair(win, im_list[x*2], im_list[x*2+1], '>', paths['stim_path'], practice=True)
        display(win, stim, timing['probe'])

        if circle:
            if x in [0,1]:
                validity = 1
            else:
                validity = 0

            circle = probe_stim(win, '>', validity)
            display(win, [circle], timing['probe'], accepted_keys=['1','3'])

        pause(win, timing['pause'])
    fix.setAutoDraw(False)

def pract_mem(win, im_list, paths, timing):
    """
    display practice memory text
    """

    fixation = fix_stim(win)

    for trial in range(4):
        rating_scale = visual.RatingScale( win, low = 1, high = 4, labels=['unfamiliar','familiar'], scale='1               2               3               4',
                                            singleClick = True, pos = [0,-.42], acceptPreText = '-',
                                            maxTime=3.0, minTime=0, marker = 'triangle', showAccept=False, acceptSize=0)

        image = memory_stim(win, im_list[trial], paths['stim_path'], practice_single=True)
        display(win, [fixation], timing['pause'])

        event.getKeys(keyList = None)
        for frame_n in range(timing['mem']):
            image.setAutoDraw(True)
            rating_scale.setAutoDraw(True)
            win.flip()
        choice_history = rating_scale.getHistory()
        rating_scale.setAutoDraw(False)
        image.setAutoDraw(False)
        win.flip()
