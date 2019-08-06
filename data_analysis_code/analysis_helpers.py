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
import scipy
from statistics import mean, stdev
from math import sqrt



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
                        df['Cued Category'][index] = cued_cat

    mem_mask = df['Trial Type']=='Memory'
    df.loc[mem_mask,'Attention Level'] = df.loc[mem_mask,'Attention Level'].fillna('Novel')

    return(df)


# Functions for behavioral analyses and plotting

def success_prop(df):
    '''
    input:   subject's dataframe
    output:  proportion of correct attention probe responses
    '''
    success = df[(df['Attention Probe']=='x') & (df['Attention Button']==1.0)].shape[0] + df[(df['Attention Probe']=='o') & (df['Attention Button']==3.0)].shape[0]
    fail    = df[(df['Attention Probe']=='x') & (df['Attention Button']==3.0)].shape[0] + df[(df['Attention Probe']=='o') & (df['Attention Button']==1.0)].shape[0]
    prop    = float(success / (success + fail))
    return(prop)



def attn_success(dataframe, runs=False):
    '''
    input:  behavioral data, full experiment (pandas dataframe)
    output: if runs==True -> run-wise proportions of correct attention probe responses for each subject (list of lists)
            if runs!=True -> averaged proportion of correct responses for each subject (list of floats)
    '''

    prop = []
    for sub in dataframe['Subject'].unique():

        if runs == False:
            df = dataframe[dataframe['Subject']==sub]
            prop.append(success_prop(df))

        else:
            sub_props=[]
            for run in range(0,8):
                df = dataframe[(dataframe['Subject']==sub) & (dataframe['Run']==run)]
                sub_props.append(success_prop(df))
            prop.append(sub_props)

    return(prop)


def apply_window(combo, window_length):
    '''
    input:  dataframe of behavioral data from an entire experiment
    output: dataframe of same shape where raw values have been replaced by rolling window mean
    '''

    # select data from memory runs
    data = combo[combo['Trial Type']=='Memory'][['Attention Level','Familiarity Rating','Trial','Subject','Run']]

    # re strucutre data - each row is a trial, each col is an attn level
    df = data.pivot_table(index=['Subject','Run','Trial'],
                          columns='Attention Level',
                         values='Familiarity Rating')

    # apply rolling window, for each run in each subject
    window_data = df.groupby(['Subject','Run']).apply(lambda x: x.rolling(window_length, min_periods=1, center = True).mean())

    return(window_data)


def add_nov_label(combo, column_name='Cued Category'):
    '''
    input:  dataframe of participant data, and the name of the column to use for cue info
            for exp1 use 'Cued Category' (cue for that block)
            for exp2 use 'Last Cued'     (last cue from presentation block)
    output: dataframe where novel images are labeled by cued or uncued category
    '''

    combo.loc[combo['Attention Level']=='Novel','Attention Level'] = 'Nov_Un'

    for snuffle in ['Face','Place']:

        # for all 'Novel', if image in cued category, rename 'Novel_Cued'
        combo.loc[(combo['Trial Type']=='Memory') & (combo[column_name]==snuffle) & (combo['Category']==snuffle)
                  & (combo['Attention Level'].isin(['Nov_Un','Novel','Nov_Cued'])),
                     'Attention Level'] = 'Nov_Cued'

        combo.loc[(combo['Trial Type']=='Memory')
                  & (combo[column_name]!=snuffle)
                  & (combo['Category']==snuffle)
                  & (combo['Attention Level'].isin(['Novel','Nov_Un','Nov_Cued'])),
                     'Attention Level'] = 'Nov_Un'
    return(combo)



def sig_bars(cat, cats, stat_dict, adjust=0):
    '''
    input:  left-most category, ordered category list, dictionary of significant ttests
    output: parameters for first significance line in descending cascade
    '''

    answer = []

    colors = ['r','m','c','y','g','b']

    cat_keys = [x for x in stat_dict.keys() if cat==x[0] and stat_dict[x]['t']>0]
    # select all positive, sig, left-to-right relationships with that category

    if len(cat_keys)==0:
        answer =  [{'y':0, 'x_min': 0, 'x_max':0, 'width': 0, 'next':0, 'color': 'w', 'categories':np.nan}]

    elif len(cat_keys)>0:
        # if any exist

        for iteration in range(0,len(cat_keys)):

            # return info for all of them
            #t_sign = stat_dict[cat_keys[iteration]]['t']
            ttest  = stat_dict[cat_keys[iteration]]

            # line params for this line

            if   ttest['p'] < .001:
                linewidth = 4
            elif ttest['p'] < .01:
                linewidth = 3
            elif ttest['p'] < .05:
                linewidth = 2
            elif ttest['p'] < .056:
                linewidth = 1
            else:
                linewidth = 0

            first = .09
            y_val = (-cats.index(cat)/len(cats))+ 5 - adjust
            xmin = .09 + (.167 * cats.index(cat))
            xmax = .09 + cats.index(cat_keys[iteration][1])*.167
            second_cat = cat_keys[iteration][1]

            answer.append( {'y': y_val, 'x_min': xmin, 'x_max': xmax, 'width': linewidth, 'next': second_cat,
                       'color' : colors[cats.index(cat_keys[iteration][0])], 'categories': cat_keys[iteration]})

    return(answer)


def sig_bars_neg(cat, cats, stat_dict, adjust=0):
    '''
    input:  left-most category, ordered category list, dictionary of significant ttests
    output: parameters for first significance line in descending cascade
    '''

    answer = []
    colors = ['b','g','y','c','m','r']

    #colors = ['r','m','c','y','g','b']

    cat_keys = [x for x in stat_dict.keys() if cat==x[0] and stat_dict[x]['t']<0]
    # select all positive, sig, left-to-right relationships with that category

    if len(cat_keys)==0:
        answer =  [{'y':0, 'x_min': 0, 'x_max':0, 'width': 0, 'next':0, 'color': 'w', 'categories':np.nan}]

    elif len(cat_keys)>0:
        # if any exist

        for iteration in range(0,len(cat_keys)):

            # return info for all of them
            #t_sign = stat_dict[cat_keys[iteration]]['t']
            ttest  = stat_dict[cat_keys[iteration]]

            # line params for this line

            if   ttest['p'] < .001:
                linewidth = 4
            elif ttest['p'] < .01:
                linewidth = 3
            elif ttest['p'] < .05:
                linewidth = 2
            elif ttest['p'] < .059:
                linewidth = 1

            first = .09
            y_val = (-cats.index(cat)/len(cats))+ 5 - adjust
            xmax = .09 + (.167 * cats.index(cat))
            xmin = .09 + cats.index(cat_keys[iteration][1])*.167
            second_cat = cat_keys[iteration][1]

            answer.append( {'y': y_val, 'x_min': xmin, 'x_max': xmax, 'width': linewidth, 'next': second_cat,
                       'color' : colors[cats.index(cat_keys[iteration][0])], 'categories': cat_keys[iteration]})

    return(answer)


def ranges(nums):
    """
    input  : a set of numbers (floats or ints)
    output : list of tuples, one tuple for each string of consecutively increasing numbers in nums
             each tuple contains two numbers: the first and last values from each consecutively incresing string
    """
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))


def timepoint_ttest(data, columns, related=True):
    '''
    input  : dataframe of timecourse-formatted behavioral data
             list with two strings, indicating which columns to compare
    output : dataframe with column containing moment-by-moment pvals
    '''

    data['timepoint_ttest']   = np.nan
    data['timepoint_t_truth'] = np.nan
    data['timepoint_t_value'] = np.nan

    for trial in data['Trial'].unique():

        a = list(data[(data['Trial']==trial) & (data['Attention Level']==columns[0])]['value'])
        b = list(data[(data['Trial']==trial) & (data['Attention Level']==columns[1])]['value'])

        if related == False:
            stat = scipy.stats.ttest_ind(a,b)
        else:
            stat = scipy.stats.ttest_rel(a,b)

        if stat.pvalue <.05:
            data.loc[(data['Attention Level'].isin(columns))
                   & (data['Trial']==trial),'timepoint_ttest'] = stat.pvalue
            data.loc[(data['Attention Level'].isin(columns))
                   & (data['Trial']==trial),'timepoint_tvalue'] = stat.statistic
            data.loc[(data['Attention Level'].isin(columns))
                   & (data['Trial']==trial),'timepoint_t_truth'] = True
        else:
            data.loc[(data['Attention Level'].isin(columns))
                   & (data['Trial']==trial),'timepoint_t_truth'] = False
            data.loc[(data['Attention Level'].isin(columns))
                   & (data['Trial']==trial),'timepoint_tvalue'] = stat.statistic
            data.loc[(data['Attention Level'].isin(columns))
                   & (data['Trial']==trial),'timepoint_ttest'] = stat.pvalue

        #print(scipy.stats.ttest_ind(a,b))

    return(data)


def cohen_d(a, b):
    '''
    input  : two lists of data
    output : cohens d statistic
    '''

    cohen_d = (mean(a) - mean(b)) / (sqrt((stdev(a) ** 2 + stdev(b) ** 2) / 2))

    return(cohen_d)



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
    '''
    input: raw parsed eye data
    output: dataframe of eye data (screen location in centimeters)
    '''

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


def pres_gaze_image(subdir, eye_df, subject):
    '''
    input: subject's experiment df and eye track df
    output: list of eye tracking df's, one for each presentation trial
    '''

    pres_gaze = {'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[]}

    for f in os.listdir(subdir):
        if 'pres' in f:

            num = f[-5]
            pres_df = pd.read_csv(subdir+'/'+f)
            start = pres_df['Stimulus Onset']
            end = pres_df['Stimulus End'] #+pres_df['Attention Reaction Time (s)'][9]
            eye_df['Run']=num
            eye_df['Subject'] = subject

            trial = 0
            for on,off in zip(start, end):
                eye_df['Trial']=trial
                pres_gaze[str(num)].append(eye_df.loc[(eye_df['timestamp']>on) &
                                            (eye_df['timestamp']<off) &
                                            (eye_df['xRaw_righteye']>0.0) &
                                            (eye_df['xRaw_lefteye']>0.0)])
                trial+=1

    return(pres_gaze)


def add_gaze(df):

    '''
    input: df containing pres and mem from single run
    output: df with string in 'Attention Level' column in each Memory trial row
    '''

    for index,row in df.iterrows():
        if row['Trial Type']=='Memory':
            mem_image = row['Memory Image']
            for cue in ['Cued ', 'Uncued ']:
                for cat in ['Face', 'Place']:
                    if df.loc[df[cue+cat] == mem_image].shape[0]!=0:
                        df['av_x_coord'][index]=df.loc[df[cue+cat] == mem_image]['av_x_coord']
                        df['Cued Side'][index] = df.loc[df[cue+cat] == mem_image]['Cued Side'].item()

    mem_mask = df['Trial Type']=='Memory'
    df.loc[mem_mask,'av_x_coord'] = df.loc[mem_mask,'av_x_coord'].fillna(np.nan)

    return(df)


def eye_intial(path):
    ''' reads in raw eye gaze data
        outputs eye gaze dataframe, timestamps in GMT
    '''

    data = []

    for x in os.listdir(path):
        newFile = parseFile(path+x)
        data1 = newFile.parse()

        for a,b in zip(['true','false'], ['True', 'False']):
            data1 = data1.replace(a, b)

        data1 = data1.split('\n')
        data1 = [x for x in data1 if "tracker" in x]
        data.extend(data1)

    dict_list = [ast.literal_eval(x) for x in data]
    dict_list = [x['values']['frame'] for x in dict_list if 'values' in x and 'frame' in x['values']]
    df = pd.DataFrame(dict_list)

    for eye in ['righteye','lefteye']:
        for coord in ['x','y']:
            df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]

    df['av_x_coord'] = df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1)
    df['av_y_coord'] = df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1)
    df['timestamp']=[time.mktime(time.strptime(x[:], "%Y-%m-%d %H:%M:%S.%f")) for x in df['timestamp']]

    return(df)
