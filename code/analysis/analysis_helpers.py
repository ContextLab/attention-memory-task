# HELPER FUNCTIONS FOR ATTENTION AND MEMORY ANALYSES

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

        ROC[attn] = [0, 1]

        # for each possible number rating
        for rate in ratings:

            # proportion of images in that attn level rated this rating or higher
            num = df.loc[(df['Attention Level'] == attn) & (df['Familiarity Rating'] >= rate)].shape[0]
            denom = df.loc[df['Attention Level'] == attn].shape[0]
            ROC[attn].append(float(num)/denom)

        ROC[attn].sort()

        # proportions of various attention-level images, by rating, on y-axis
        # proportions of novel images, by rating, on x-axis
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
