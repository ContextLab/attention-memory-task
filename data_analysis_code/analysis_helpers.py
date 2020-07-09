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

    # list all files in the subject's directory that contain pres or mem run data
    files = [ x for x in os.listdir(subdir) if 'pres' in x or 'mem' in x ]

    # read in the data from each of these files
    df_list = [ pd.read_csv(subdir+'/'+x) for x in files ]

    # concatenate into a single dataframe
    df = pd.concat(df_list, ignore_index=True)

    return(df)


def add_level(df):
    '''
    input: subject dataframe
    output: subject dataframe w/ Attention Level string for each Memory trial row
    '''
    # for each run
    for x in df.Run.unique():

        # select the data only from that run
        mask = df['Run']==x

        # pass the data for that run through run_level to add attention levels to memory images
        df[mask] = run_level(df[mask])

    return(df)


def run_level(df):
    '''
    input: df containing pres and mem from single run
    output: df with string in 'Attention Level' column in each Memory trial row
    '''

    # loop over the memory trials in this run
    for index,row in df[df['Trial Type']=='Memory'].iterrows():

        # obtain the image presented in the memory run
        mem_image = row['Memory Image']

        # obtain the category of the image from its filename
        # (SUN database images -- places -- contain the string 'sun')
        if 'sun' in mem_image:
            mem_image_category = 'Place'
        else:
            mem_image_category = 'Face'

        # add the image category to the memory trial row
        df['Category'][index] = mem_image_category

        # look in the columns for previously presented composites
        for composite in ['Cued Composite', 'Uncued Composite']:

            # if one of the previously seen composites contains the memory image file name (minus the last 4 chars: '.jpg')
            if df[df[composite].str.contains(mem_image[:-4], na=False)].shape[0]!=0:

                # pull the cued category from that row/presentation trial
                cued_cat = df[df[composite].str.contains(mem_image[:-4], na=False)]['Cued Category'].item()

                # if the image category matches the cued category for the presentation trial
                if mem_image_category == cued_cat:

                    # AND the image was presented on the Cued Side
                    if composite == 'Cued Composite':
                        # label "Full" attention
                        attention = "Full"

                    # AND it was presented on the Uncued Side
                    elif composite == 'Uncued Composite':
                        # label "Category" attention
                        attention = "Category"

                # else, if the image category does NOT match the cued category for the trial
                else:
                    # AND it was presented in the Cued location
                    if composite == 'Cued Composite':
                        # labbel "Cued" attention
                        attention = "Side"

                    # AND the image was presented in the Uncued location
                    elif composite == 'Uncued Composite':
                        # label "None" attention
                        attention = "None"

                # add the attention level to the memory trial row
                df['Attention Level'][index] = attention

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


def apply_window(combo, window_length):
    '''
    input:  dataframe of behavioral data from an entire experiment
    output: dataframe of same shape where raw values have been replaced by rolling window mean
    '''

    # select data from memory runs
    data = combo[combo['Trial Type']=='Memory'][['Attention Level','Familiarity Rating','Trial','Subject','Run']]

    # re-structure the data - each row is a trial, each column is an attn level
    df = data.pivot_table(index=['Subject', 'Trial'], columns='Attention Level', values='Familiarity Rating')

    # apply rolling window, for each subject
    window_data = df.groupby(['Subject']).apply(lambda x: x.rolling(window_length, min_periods=1, center=True).mean())

    return(window_data)


def add_nov_label(combo, column_name='Last Cued'):
    '''
    input:  dataframe of participant data, and the name of the column to use for last-cued category info
    output: dataframe with unlabeled novel images
    '''

    # for all 'Novel' images in memory trials, if Category == Last_Cued category, rename 'Novel_Cued'\n",
    combo.loc[(combo['Trial Type']=='Memory') & (combo['Attention Level']=='Novel') & (combo[column_name] == combo['Category']),'Attention Level'] = 'Nov_Cued'

    # for all 'Novel' images in memory trials, if Category != Last_Cued category, rename 'Novel_Cued'\n",
    combo.loc[(combo['Trial Type']=='Memory') & (combo['Attention Level']=='Novel') & (combo[column_name] != combo['Category']),'Attention Level'] = 'Nov_Un'

    return(combo)



def sig_bars(cat, cats, stat_dict, adjust=0, sign='pos'):
    '''
    input:  left-most category in the significance relations to test, ordered category list, dictionary of significant ttests
    output: parameters for significance line cascade extending from this category to any other categories that are significantly different
    '''

    answer = []

    if sign =='pos':
        # select all positive, left-to-right relationships from this category to each other violin / image category
        cat_keys = [x for x in stat_dict.keys() if cat==x[0] and stat_dict[x]['t']>0]
        colors = ['r','m','c','y','g','b']

    if sign == 'neg':
        # select all negative left-to-right relationships from this category to each other violin / image category
        cat_keys = [x for x in stat_dict.keys() if cat==x[0] and stat_dict[x]['t']<0]
        colors = ['b','g','y','c','m','r']

    if len(cat_keys)==0:
    # if there aren't any relationships for this sign (pos or neg), make a line with no width, no length, etc
        answer =  [{'y':0, 'x_min': 0, 'x_max':0, 'width': 0, 'next':0, 'color': 'w', 'categories':np.nan}]

    elif len(cat_keys)>0:
    # if there are relationships for this sign

        for iteration in range(0,len(cat_keys)):
        # for each relationship

            # select the ttest info for the relationship from stat_dict
            ttest  = stat_dict[cat_keys[iteration]]

            # use the ttest p-value to assign the width of the line that will show this relationship
            if   ttest['p'] < .001:
                linewidth = 7
            elif ttest['p'] < .01:
                linewidth = 5
            elif ttest['p'] < .05:
                linewidth = 3
            elif ttest['p'] <= .0551:
                linewidth = 1
            else:
                linewidth = 0

            # at first, assign all lines the same height (this gets adjusted later when we plot)
            y_val = 8

            # assign min x value: minimum x value is .09 + .167*location_of_the_first_category
            xmin = .09 + (.167 * cats.index(cat))

            # assign max x value:  .09 + .167 * location_of_the_second_category
            xmax = .09 + cats.index(cat_keys[iteration][1])*.167

            # append each line to the output as a dictionary containing all of the line parameters
            # (line width, the categories it is drawn between, etc.)
            answer.append( {'y': y_val, 'x_min': xmin, 'x_max': xmax, 'width': linewidth, 'next': cat_keys[iteration][1],
                       'color' : colors[cats.index(cat_keys[iteration][0])], 'categories': cat_keys[iteration]})
                        # 'next' is the category that we have just drawn the line to, from the starting category
                        # when we make a left-to-right cascade, it tells us the next category to look at

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
    :param a: some distribution of data a
    :param b: some distribution of data b
    :return: the effect size according to cohens D calculation
    '''
    Na = len(a) # number
    Nb = len(b)
    Ma = mean(a) # mean
    Mb = mean(b)
    Sa = stdev(a) # standard dev
    Sb = stdev(b)

    # pooled standard dev for 2 distributions
    pooledSd = sqrt( ((Na-1)*na**2 + (Mb-1)*Ma**2)/(Na + Ma -2) )
    cohen = (Ma-Mb)/pooledSd

    return(cohen)

# def cohen_d(a, b):
#     '''
#     input  : two lists of data
#     output : cohens d statistic
#     '''
#
#     cohen_d = (mean(a) - mean(b)) / (sqrt((stdev(a) ** 2 + stdev(b) ** 2) / 2))
#
#     return(cohen_d)


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


def pres_gaze_from_df(behavioral_df, eye_df):
    '''
    input: participant's behavioral df
           participant's eye track df
    output: single df of gaze data for this participant, when pres images on screen
    '''
    # empty lists for pres_gaze and no_gaze (runs w/ very few recorded datapoints)
    pres_gaze = []
    no_gaze = []

    # for each presentation row in the behavioral df
    for idx,x in behavioral_df[behavioral_df['Trial Type']=='Presentation'].iterrows():

        # select times when visual stimuli appear & disappear
        start,end = x['Stimulus Onset'],x['Stimulus End']

        # select gaze data from interval stim was on screen
        chunk = eye_df.loc[(eye_df['timestamp']>=start) & (eye_df['timestamp']<=end)]

        # add trial and run numbers
        chunk['Trial'] = np.nan
        chunk['Run']   = np.nan
        chunk['Trial'] = x['Trial']
        chunk['Run']   = x['Run']

        # add start times to separate row
        chunk['Behavior_Image_Start'] = start

        # if there are fewer than five gazepoints, also add this chunk to no_gaze
        if chunk.shape[0] <5:
            no_gaze.append(chunk)

        # append the gaze data for each trial to a list
        pres_gaze.append(chunk)

    # concat data from all runs and trials
    pres_gaze = pd.concat(pres_gaze)
    # no_gaze = pd.concat(no_gaze)

    return(pres_gaze, no_gaze)


def pres_gaze_from_path(subdir, eye_df):
    '''
    input: path to participant's data directory
           participants eye track df
    output: single df of gaze data for this participant, when pres images on screen
    '''

    pres_gaze = []

    # for each file in this subject directory
    for f in os.listdir(subdir):

        # for every behavioral data file from a presentation run
        if 'pres' in f:

            # read in the presentation data
            pres_df = pd.read_csv(subdir+'/'+f)

            # pull the stimulus start and end times from this run
            start = pres_df['Stimulus Onset']
            end = pres_df['Stimulus End']

            # loop through the start and end times and pull gazepoints that fall within them
            trial = 0
            for on,off in zip(start, end):

                chunk = eye_df.loc[(eye_df['timestamp']>=on) & (eye_df['timestamp']<=off)]

                chunk['Trial'] = trial
                chunk['Run']   = f[-5] # run number from filename ('pres#.csv')

                # append the gaze data for each trial to a list
                pres_gaze.append(chunk)

                trial+=1

    # concat data from all runs and trials
    pres_gaze = pd.concat(pres_gaze)

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



def eye_initial(path):
    ''' reads in raw eye gaze data
        outputs eye gaze dataframe, timestamps in UTC
    '''

    data = []

    # for each gaaze file in this paraticipant's gaze directory
    for x in os.listdir(path):

        # parse the file
        newFile = parseFile(path+x)
        data1 = newFile.parse()

        # replace true/false with Python friendly True/False
        for a,b in zip(['true','false'], ['True', 'False']):
            data1 = data1.replace(a, b)

        # select eye tracking rows (ignore occasional "heartbeat" rows; we did not monitor heart rate)
        data1 = data1.split('\n')

        # data1 is a list of rows from this file
        data1 = [x for x in data1 if "tracker" in x]

        # convert strings to python
        data1 = [ast.literal_eval(x) for x in data1]

        # select the ones that have gaze values
        data1 = [x['values']['frame'] for x in data1 if 'values' in x and 'frame' in x['values']]


        # convert list of relevant gaze dicts to a dataframe
        data1 = pd.DataFrame(data1)
        run_num = re.findall(r'\d+', x)

        # find run nums
        if len(run_num)==1:
            run_num = run_num[0]
        elif len(run_num)==2:
            run_num=run_num[1]

        # assign run_num column
        data1['Run'] = run_num

        # append this df to data; data is a list of df's
        data.append(data1)

    # df is be a big, concatenated df
    df = pd.concat(data)
    df = df.reset_index(drop=True)

    # extract raw average gaze values
    for eye in ['righteye','lefteye']:
        for coord in ['x','y']:
            df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]

    # average x coord and y coord values from right and left eyes
    df['av_x_coord'] = df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1)
    df['av_y_coord'] = df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1)
    # timestamp conversion
    df['timestamp']=[datetime.timestamp(datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f" )) for x in df['timestamp']]

    return(df)


# def eye_initial(path):
#     ''' reads in raw eye gaze data
#         outputs eye gaze dataframe, timestamps in UTC
#     '''
#
#     data = []
#
#     for x in os.listdir(path):
#         newFile = parseFile(path+x)
#         data1 = newFile.parse()
#
#         # replace with Python friendly True/False
#         for a,b in zip(['true','false'], ['True', 'False']):
#             data1 = data1.replace(a, b)
#
#         # select eye tracking rows (ignore occasional "heartbeat" rows; we did not monitor heart rate)
#         data1 = data1.split('\n')
#         data1 = [x for x in data1 if "tracker" in x]
#
#         l = len(data1)
#         if l ==0:
#             print(x + ' no gazepoints')
#         elif l < 10:
#             print(x + ' less than ten points')
#         elif l < 20:
#             print(x + ' less than twenty points')
#         elif l < 30:
#             print(x + ' less than thirty points')
#
#         data.extend(data1)
#
#     # evaluate each row and subselect the frame data
#     dict_list = [ast.literal_eval(x) for x in data]
#     dict_list = [x['values']['frame'] for x in dict_list if 'values' in x and 'frame' in x['values']]
#     df = pd.DataFrame(dict_list)
#
#     # label the raw average gaze values
#     for eye in ['righteye','lefteye']:
#         for coord in ['x','y']:
#             df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]
#
#     # take the averages
#     df['av_x_coord'] = df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1)
#     df['av_y_coord'] = df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1)
#     df['timestamp']=[datetime.timestamp(datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f" )) for x in df['timestamp']]
#     #df['timestamp']=[time.mktime(time.strptime(x[:], "%Y-%m-%d %H:%M:%S.%f")) for x in df['timestamp']]
#
#     return(df)


# Log File Parsing Functions

def list_logs(data_dir):
    '''
    input : path to participant data directory  (str)
    output: participant's full behavioral log   (df)
    '''

    participant = []
    for f in os.listdir(data_dir):

        if f !='--1.log' and ('.log' in f):

            with open(data_dir+f) as file:

                    lines = file.read().splitlines()
                    lines = [[lines[x]] for x in range(0, len(lines))]
                    #lines.insert(0,['DATA'])

                    log_file = pd.DataFrame(lines).reset_index()

                    s = data_dir.split('/')[-2]
                    log_file['Subject'] = s.split('_')[0]
                    log_file['Run'] = int(f.split('.')[-2][-1])
                    log_file['TIME'],log_file['WARNING'],log_file['MESSAGE'] = log_file[0].str.split('\t', 4).str
                    log_file = log_file.fillna('NAN VALUE')
                    log_file['TIME'] = log_file['TIME'].str.replace(' ','')
                    log_file['TIME'] = log_file['TIME'].astype(float, errors='ignore')

                    a = log_file[log_file[0].str.contains('current')][0].str.split(' ', expand=True)
                    log_file['TIME'] = log_file[['TIME']].applymap(lambda x: np.nan if isinstance(x, str) else float(x))

                    participant.append(log_file)

    participant = pd.concat(participant)
    return(participant)
