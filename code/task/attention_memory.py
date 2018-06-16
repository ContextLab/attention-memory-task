# This experiment was created by Kirsten Ziman (kirsten.k.ziman.gr@dartmouth.edu)
# for more information, visit: www.context-lab.com

# Imports 
import psychopy
import sys
import pandas as pd
from psychopy import visual, event, core, data, gui, logging
#import pylinkwrapper
sys.path.insert(0, '../analysis/')
from analysis_helpers import *
from experiment_helpers import *
import time

# Parameters #
experiment_title = 'Attention and Memory' 
practice = True # practice round before experiment
test_mode = False # to test code, not for use with subjects
save_data = True # saves out all data
eye_track = False # for eye tracking
MRI = False # for MRI sync
params = {'runs':8, 'presentations_per_run':10, 'invalid_cue_percentage':10, 'mem_to_pres':4, 'mem_pres_split':2}
categories = {'cat1':'Faces', 'cat2':'Places', 'composites':'composites'}
paths = {'data_path':'../../data/', 'stim_path':'../../stim/'}

# Obtain participant info (pop-up) and make subdir
info = subject_info(experiment_title, paths['data_path'])
subject_directory = subject_directory(info, paths['data_path'], path_only=True)

# Initiate clock #
global_clock = core.Clock()
logging.setDefaultClock(global_clock)


# RUN EXPERIMENT ########################################################################################

# pre questionnaire #
pre_info = pre_questionnaire(info, save=save_data, save_path=subject_directory)


# Initiate log file #
# log_data = logging.LogFile(paths['data_path'] + subject_info['participant'] + '.log', filemode='w', level=logging.DATA)


# Create window #
#win = visual.Window([1024,768], fullscr = True, monitor = 'testMonitor', units='deg', color = 'black')


# practice #
initialize_df(info, categories, paths, subject_directory, params) 


# eye tracker callibration #


# Set up subject dataframe #


# presentation and memory trials #


# post questionnaire #
#post_info = post_questionnaire(subject[0], save=save_data, save_path=paths['data_path'])

