import seaborn
import os
import pickle
#import statistics
import pandas as pd
import numpy as np
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
    outputs: lists images shared between the columns
    '''

    if type(x)==int:

        mask = df['Run']==x
        return(list_compare(list(images(df.loc[mask,col1])), list(images(df.loc[mask,col2]))))

    else:
        return(list_compare(list(images(df[col1])), list(images(df[col2]))))

def validity_check(df, params):
    '''
    inputs: dataframe, parameters
    outputs: message about validity percentage (empty list or list containing string)
    '''
    num_valid = sum(list(df['Cue Validity']))

    msg = []

    if len(df.Run.unique())<params['runs']:
        msg = ["It looks like there is test data here! (Fewer than expected # of runs).  "]

    if len(msg)==0:
        if num_valid != params['presentations_per_run']*params['runs']*(100-params['invalid_cue_percentage'])/100:
            if len(df.Run.unique())==params['runs']:
                msg.append('Incorrect number of invalid attention circles.  ')

    return(msg)

def check_rep_interal(mass):
    '''
    checks for repeats within cued, uncued, and mem lists
    '''
    for s in mass:
        for x in [s['cued'],s['uncued'],s['images']]:
            if not len(x) == len(set(x)):
                print('cure repeat, internal')

        if len([x for x in s['cued'] if x in s['uncued']]):
            print('Cue repeat, external')

def ROC(df, plot=True):
    '''
    input: subject df
    output: ROC plot or ROC data dict
    '''

    ratings = [1.0, 2.0, 3.0, 4.0]
    ROC = {}

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    # for each attention level
    for attn in ['Novel', 'None','Side','Full','Category']:
        ROC[attn] = [0]

        # for each possible number rating
        for idx in range(len(ratings)):

            # proportion of times they rated that attn level & proportion of Novel that got that rating
            num = df.loc[(df['Attention Level'] == attn) & df['Familiarity Rating'].isin(ratings[:idx+1])].shape[0]
            denom = df.loc[df['Attention Level'] == attn].shape[0]
            ROC[attn].append(float(num)/denom)

        ROC[attn].append(1)

        if attn != 'Novel':
            ax1.plot(ROC['Novel'], ROC[attn], '-o', label=attn)

    if plot:
        plt.legend(loc='upper left');
        plt.ylim(0, 1)
        plt.xlim(0, 1)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    else:
        return(ROC)

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
        if check_reps(df[x]) > 0:
            msg.append('Internal repetition in '+x+'.  ')
        for run in range(params['runs']):
            if x!='Memory Image':
                if len(check_shared(df, x, 'Memory Image', run)) != params['presentations_per_run']*2/params['mem_to_pres']:
                    msg.append('Wrong number of prev seen images from one or more categories.  ')
                    print(x, check_shared(df, x, 'Memory Image', run))
    msg.append(validity_check(df, params))

    if len(msg)==0:
        msg = "All stimulus proportions correct! :)"

    return(msg)

# Functions for Simple Behavioral Analyses

def add_level(df):
    '''
    input: subject dataframe
    output: subject dataframe w/ Attention Level string for each Memory trial row
    '''

    for x in df.Run.unique():
        mask = df['Run']==x
        df[mask] = run_level(df[mask])

    return(df)

def run_level(df):
    '''
    input: df containing pres and mem from single run
    output: df with string in 'Attention Level' column in each Memory trial row
    '''

    cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    for index,row in df.iterrows():

        if row['Trial Type']=='Memory':
            mem_image = row['Memory Image']
            # for mem_image in df[df['Trial Type']=='Memory']['Memory Image'].tolist():
            # loop over rows in memory chunk and pull memory image from each

            for cue in ['Cued ', 'Uncued ']:
                for cat in ['Face', 'Place']:
                    if df.loc[df[cue+cat] == mem_image].shape[0]!=0:
                        if cat == cued_cat:
                            df['Category'][index]=cued_cat
                            if cue == 'Cued ':
                                attention = "Full"
                            elif cue == 'Uncued ':
                                attention = "Category"
                        else:
                            df['Category'][index]=cat
                            if cue == 'Uncued ':
                                attention = "None"
                            elif cue == 'Cued ':
                                attention = "Side"
                        df['Attention Level'][index] = attention

    mem_mask = df['Trial Type']=='Memory'
    df.loc[mem_mask,'Attention Level'] = df.loc[mem_mask,'Attention Level'].fillna('Novel')

    return(df)
