# HELPER FUNCTIONS FOR ATTENTION AND MEMORY ANALYSES

import os
import pickle
import pandas as pd
from matplotlib import pyplot as plt
import ast
import json
import re
from datetime import datetime
import time
import hypertools as hyp
import numpy as np
from matplotlib import patches as patches
import seaborn as sb



# BEHAVIORAL DATA ANALYSIS FUNCTIONS

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


# EYE GAZE DATA ANALYSIS FUNCTIONS

class parseFile():
    def __init__(self, file):
        self.file = file
    def parse(self):
        data = open(self.file).read()
        return(data)

def load(path):
    '''
    input: path to directory containing eye track data
    output: raw parsed eye data
    '''

    data = []
    files = [f for f in os.listdir(path)]

    for x in files:
        #if os.path.isfile(path+x):
        newFile = parseFile(path+x)
        data1 = newFile.parse()

        for a,b in zip(['true','false'], ['True', 'False']):
            data1 = data1.replace(a, b)

        data1 = data1.split('\n')
        data1 = [x for x in data1 if "tracker" in x]
        data.extend(data1)

    return(data)


def df_create(data):
    """
    input: raw parsed eye data
    output: dataframe of eye data (screen location in centimeters)
    """

    dict_list = [ast.literal_eval(x) for x in data]
    dict_list = [x['values']['frame'] for x in dict_list if 'frame' in x['values']]

    df = pd.DataFrame(dict_list)

    # right and left eye
    for eye in ['righteye','lefteye']:
        for coord in ['x','y']:
            df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]

    # convert to centimeters
    df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
    df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))

    # convert timestamp
    df['timestamp']=[time.mktime(time.strptime(x[:], "%Y-%m-%d %H:%M:%S.%f")) for x in df['timestamp']]

    return(df)

def pres_gaze(subdir, eye_df, interval='images'):
    '''
    input: subject's experiment df and eye track df
    output: list of eye data df's
            each df is either eye data from full pres block, or from single pres trial (interval='images')
    '''

    pres_gaze = []

    for f in os.listdir(subdir):

        if 'pres' in f:

            pres_df = pd.read_csv(subdir+'/'+f)

            if interval == 'images':
                start = pres_df['Stimulus Onset']
                end = pres_df['Stimulus End']

            else:
                start = pres_df['Stimulus Onset'][0]
                end = pres_df['Stimulus End'][9]

            for x,y in zip(start,end):
                eye_df['Cued Side']=pres_df.iloc[0]['Cued Side']
                eye_df['Cued Category']=pres_df.iloc[0]['Cued Category']
                pres_gaze.append(eye_df.loc[(eye_df['timestamp']>x) &
                                            (eye_df['timestamp']<y) &
                                            (eye_df['xRaw_righteye']>0.0) &
                                            (eye_df['xRaw_lefteye']>0.0)])
    return(pres_gaze)


def gaze_plot(df_list):

    middle = 2048/2.0
    quarter = (1304-744)/4.0

    fig = plt.figure()
    ax1 = fig.add_subplot(111, aspect='equal')

    for x in df_list:
        if x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Place':
            color='green'
        elif x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Face':
            color='blue'
        elif x['Cued Side'].all()=='<' and x['Cued Category'].all()=='Place':
            color='orange'
        else:
            color='red'

        x['Color']=color

        ax1.plot(x['av_x_coord'], x['av_y_coord'], '.', color=color)
        #props.append(x.loc[(x['av_x_coord']>middle-quarter) & (x['av_x_coord']<middle+quarter)])

    rect1 = patches.Rectangle(((59.8/2.0)-8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
    rect2 = patches.Rectangle(((59.8/2.0)+8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')

    # Add the patch to the Axes
    ax1.add_patch(rect1)
    ax1.add_patch(rect2)

    # plt.legend(loc='upper left');
    plt.ylim(0, 33.6)
    plt.xlim(0, 59.8)
    plt.show()
