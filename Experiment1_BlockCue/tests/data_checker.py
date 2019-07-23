# FUNCTIONS TO CHECK COLLECTED BEHAVIORAL DATA FOR ATTENTION AND MEMORY EXPERIMENT

import os
import pickle
import pandas as pd
from matplotlib import pyplot as plt

# Functions to Aggregate Subject Data and Verify Correct Stimuli were Presented

def sum_pd(subdir):
    '''
    input: subject directory (string)
    output: full experiment info (dataframe)
    '''

    files = [ x for x in os.listdir(subdir) if 'pres' in x or 'mem' in x ]
    df_list = [ pd.read_csv(subdir+'/'+x) for x in files ]
    df = pd.concat(df_list, ignore_index=True)

    return(df)

def images(df_col):
    '''
    input: df column
    output: list of image names (strings)
    '''
    return([ x for x in df_col if type(x)==str])

def check_reps(lst):
    '''
    input: list of imagenames (strings)
    output: number of repeats (int)
    '''
    return(len(lst)-len(set(lst)))

def list_compare(lst1, lst2):
    '''
    input: two lists
    output: number of shared items between lists
    '''
    return(set(lst1) & set(lst2))

def check_shared(df, col1, col2,x=None):
    '''
    inputs: dataframe, two column names (strings), run#=None
    outputs: lists images shared between the columns, if any exist
    '''
    if type(x)==int:
        mask = df['Run']==x
        msg = list_compare(list(images(df.loc[mask,col1])), list(images(df.loc[mask,col2])))
    else:
        msg = list_compare(list(images(df[col1])), list(images(df[col2])))

    if msg != None:
        return(msg)


def validity_check(df, params):
    '''
    inputs: dataframe, parameters
    outputs: if there is an error, outputs
             message about validity percentage
             (list containing string)
    '''
    msg = []

    if len(df.Run.unique())<params['runs']:
        msg = ["It looks like there is test data here! (Fewer than expected # of runs).  "]

    if len(msg)==0:
        if df['Cue Validity'].sum()/(float(params['runs']*params['presentations_per_run'])) != .9:
            if len(df.Run.unique())==params['runs']:
                msg.append('Incorrect number of invalid attention circles.  '+str(params['presentations_per_run']*params['runs']*(100-params['invalid_cue_percentage'])/100))
    if len(msg)>0:
        return(msg)

def stimulus_check(subdir, params):
    '''
    input: subject directory (string)
    output: message indicating if all stimulus proportions are correct (string)
    '''
    msg = []
    select_cols = ['Cued Face', 'Cued Place',
                   'Uncued Face', 'Uncued Place',
                'Memory Image']

    df = sum_pd(subdir)
    for x in select_cols:
        # check internal repetitions
        if check_reps(df[x]) > 0:
            msg.append('Internal repetition in '+x+'.  ')
        # check correct proportion in memory runs, by run
        for run in range(params['runs']):
            if x!='Memory Image':
                if len(check_shared(df, x, 'Memory Image', run)) != params['presentations_per_run']*2/params['mem_to_pres']:
                    msg.append('Wrong number of prev seen images from one or more categories.  ')
                    print(x, check_shared(df, x, 'Memory Image', run))
    # check no composites shown attended AND unattended side, total
    if len(check_shared(df[df['Trial Type']=='Presentation'],'Cued Composite', 'Uncued Composite'))>0:
        msg.append('Overlapping cued and uncued composites. ')
    # check no repeats within composite columns (cued, uncued)
    if check_reps(df['Cued Composite']) + check_reps(df['Uncued Composite']) > 0:
        msg.append('Repeat within cued or uncued composites. ')

    msg.append(validity_check(df, params))

    if len(msg)==1 and msg[0]==None:
        msg.append("All stimulus proportions correct!")
    return(msg)
