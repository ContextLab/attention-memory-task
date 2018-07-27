

# This experiment was created by Kirsten Ziman (Kirsten.K.Ziman.gr@Dartmouth.edu)
# for more information, visit: www.context-lab.com


# Imports ############################################################################################

import psychopy
import sys
import pandas as pd
from psychopy import visual, event, core, data, gui, logging
sys.path.insert(0, '../analysis/')
from analysis_helpers import *
from experiment_helpers import * # main functions in experiment_helpers.fpy
import time


# Set Up #############################################################################################

# Experiment handler #
# exp = data.ExperimentHandler(name = 'Attention Memory', version = '1.0')

# Parameters #
experiment_title = 'Attention and Memory' 
practice = True   # instructions & practice
save_data = True  # saves all data
MRI = False       # for MRI sync

params = {'runs':8, 'presentations_per_run':10, 'invalid_cue_percentage':10, 'mem_to_pres':4, 'mem_pres_split':2}
categories = {'cat1':'Faces', 'cat2':'Places', 'composites':'composites'}
paths = {'data_path':'../../data/', 'stim_path':'../../stim/'}

# Obtain participant info (pop-up) and make subdir #
info = subject_info(experiment_title, paths['data_path'])
paths['subject'] = subject_directory(info, paths['data_path'], path_only=True)

# Initiate clock #
global_clock = core.Clock()
logging.setDefaultClock(global_clock)
 
# Pre questionnaire #
pre_info = pre_questionnaire(info, save=save_data, save_path=paths['subject'])

# Window and Stimulus timing #
win = visual.Window([1024,768], fullscr = True, monitor = 'testMonitor', units='deg', color = 'black')
rate = win.getActualFrameRate()
timing = {'cue':int(round(1.5 * rate)), 'probe':int(round(3.0 * rate)), 'mem':int(round(2 * rate)), 'pause':int(round(1 *rate))}



# Run Experiment #####################################################################################

# Instructions & Practice #
if practice:
    for x in range(11):
        practice_instructions(win, paths, pract_text(x), x, timing, acceptedKeys = [], practice=True)

# MRI sync #
# if MRI:


# Initialize dataframe and savefiles #
df = initialize_df(info, categories, paths, paths['subject'], params) 
# button_init(paths)

# create df masks
mask1 = df['Trial Type']=='Presentation'
mask2 = df['Trial Type']=='Memory'

# Pres & Mem runs #
for run in range(params['runs']):
    
    mask3 = df['Run']==run
    
    # presentation      
    text_present(win, pres_text(run))
    presentation_run(win, run, df.loc[mask1][mask3], params, timing, paths) 
    
    # memory 
    text_present(win, mem_text(run))
    memory_run(win, run, df.loc[mask2][mask3], params, timing, paths)
    
# thanks for participating #
text_present(win, 'Thank you for your participation!')

# post questionnaire #
post_info = post_questionnaire(subject[0], save=save_data, save_path=paths['data_path'])
df.to_csv(paths['subject']+'final_df.csv')
