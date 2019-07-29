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


# Functions for Simple Behavioral Analyses

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
    output: if runs==True -> run-wise proportions for each subject (list of lists)
            if runs!=True -> averaged proportion correct for each subject (list of floats)
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



def ROC_prop(df, rate, attn, novel='matched'):
    '''
    input: subject df
           rating - Familiarity score (float between 1.0 and 4.0)
           attn - at time of encoding (string)

    output: proportion of images encoded at ATTENTION LEVEL
            given a score of RATE or higher, sorted by
            CATEGORY (if category == True)
    '''

    # proportions
    combined = float(df.loc[(df['Attention Level'] == attn) & (df['Familiarity Rating'] >= rate)].shape[0])/(df.loc[(df['Attention Level'] == attn) & (df['Familiarity Rating'] > 0)].shape[0])

    if novel == 'all':
        # all novel images for desired ratings in both categories
        denom_f = df.loc[(df['Attention Level'] == attn) & (df['Familiarity Rating'] > 0)].shape[0]
        denom_p = denom_f

    else:
        if novel   == 'matched':
            f_nov,p_nov = 'Face','Place'
        elif novel == 'opposite':
            p_nov,f_nov = 'Place','Face'

        denom_p = df.loc[(df['Attention Level'] == attn) & (df['Category'] == p_nov) & (df['Familiarity Rating'] > 0)].shape[0]
        denom_f = (df.loc[(df['Attention Level'] == attn) & (df['Category'] == f_nov) & (df['Familiarity Rating'] > 0)].shape[0])

    if df.loc[(df['Attention Level'] == attn) & (df['Category'] == 'Face')].shape[0] > 0:
        face = float(df.loc[(df['Attention Level'] == attn) & (df['Familiarity Rating'] >= rate) & (df['Category'] == 'Face')].shape[0])/denom_f
    else:
        face = np.nan

    if df.loc[(df['Attention Level'] == attn) & (df['Category'] == 'Place')].shape[0] > 0:
        house = float(df.loc[(df['Attention Level'] == attn) & (df['Familiarity Rating'] >= rate) & (df['Category'] == 'Place')].shape[0])/denom_p
    else:
        house = np.nan

    props = [combined, face, house]
    return(props)



def ROC_data(df, novel='matched'):
    '''
    input: subject df
    output: list of three ROC proportion sets (list of dicts): 1) all images, 2) faces, 3) places
    '''

    ratings = [4.0, 3.0, 2.0, 1.0]
    ROC, ROC_f, ROC_h = {},{},{}

    # for each attention level
    for attn in ['Novel', 'None', 'Side', 'Full', 'Category']:
        for idx,roc in enumerate([ROC, ROC_f, ROC_h]):
            roc[attn] = [0]
            #roc[attn] = []

            # for each possible number rating
            for rate in ratings:
                roc[attn].append(ROC_prop(df, rate, attn, novel=novel)[idx])

    return(ROC, ROC_f, ROC_h)



def ROC_plot(ROC_data):
    '''
    input: ROC proportions (dictionary)
    output: displays plot of ROC curve
    '''

    fig, ax = plt.subplots()

    for attn,color in zip(['Category', 'Full', 'None', 'Side'],['purple','blue','orange','red']):
        ax.plot(ROC_data['Novel'], ROC_data[attn], '-o', label=attn, color=color)

    plt.legend(loc='upper left');
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()



def ROC_df(df):

    '''
    input:  full df
    output: list of subject df's with run-wise ROC data
    '''

    subject_list = []

    for sub in df['Subject'].unique():
        subject=[]

        for run in df['Run'].unique():
            subject.append(ROC_data(df[(df['Run']==run) & (df['Subject']==sub)]))
        subject_list.append(subject)

    return(subject_list)



def AUC(x_vals, y_vals):
    '''
    input:
    x_vals - x values for ROC curve, arranged left to right (list of floats)
    y_vals - y values for ROC curve, index matched to x_vals (list of floats)

    output:
    Area under the curve (AUC)
    '''

    AUC = 0

    for i,(x,y) in enumerate(zip(x_vals, y_vals)):
        if i>0:
            x_delt = x - x_vals[i-1]
            y_delt = y - y_vals[i-1]
            AUC += (y_vals[i-1] * x_delt) + (.5 * x_delt * y_delt)

    return(AUC)

def slide_window_plot(data, window_len, overlap):

    # re-label novel face and novel place images in full data
    # change to 'NovelF' and 'NovelP'

    data.loc[(data['Attention Level']=='Novel')
             &(data['Category']=='Face'),'Attention Level'] = 'Novel_F'

    data.loc[(data['Attention Level']=='Novel')
             &(data['Category']=='Place'),'Attention Level'] = 'Novel_P'

    all_subjects = {}

    # within each subject
    for s in data['Subject'].unique():

        sub_runs = {}
        # dictionary for windows in this subject's runs

        face_nov_idx = data[(data['Category']=='Face') &
                      (data['Trial Type']=='Memory') &
                      (data['Attention Level']=='Novel') &
                      (data['Subject']==s)].index

        place_nov_idx = data[(data['Category']=='Face') &
                       (data['Trial Type']=='Memory') &
                       (data['Attention Level']=='Novel') &
                       (data['Subject']==s)].index

        # within each run
        for r in data['Run'].unique():

            run_ratios = []

            # obtain cued category from last presentation in the pres block
            cat = data[(data['Subject'] == s) &
                        (data['Run'] == r)]['Cued Category']

            # grab cued cateogry from last presentation trial
            cued_letter = cat.iloc[-1][0]

            if cued_letter == 'F':
                uncued_letter = 'P'

            if cued_letter == 'P':
                uncued_letter = 'F'

            # get chunk of Attn Levels + Ratings
            level = data[(data['Subject'] == s) & (data['Run'] == r)]['Attention Level']
            rating = data[(data['Subject'] == s) & (data['Run'] == r)]['Familiarity Rating']

            novel_face_index = level[level=='Novel_F'].index
            novel_place_index = level[level=='Novel_P'].index
            memory_index = data[(data['Subject'] == s) & (data['Run'] == r)& (data['Trial Type']=='Memory')].index

            windows = sliding_window(memory_index, window_len, overlap)

            for window in windows:

                face_win  = list(set(novel_face_index) & set(window))
                place_win = list(set(novel_place_index) & set(window))

                if cued_letter == 'F':
                    ratio = rating[face_win].mean()/rating[place_win].mean()
                else:
                    ratio = rating[place_win].mean()/rating[face_win].mean()

                run_ratios.append(ratio)
                # list of cued / uncued ratios for this run (one per window)

            sub_runs['run'+str(r)] = run_ratios

            all_subjects['subj_'+str(s)] = pd.DataFrame.from_dict(sub_runs).T.mean()

    melted = pd.melt(pd.DataFrame(all_subjects).T)

    ax = sns.lineplot(x="variable", y="value", data=melted)

    ax.set(xlabel='Time Window', ylabel='Mean Cued / Uncued Familiarity')
    plt.show()

    # print('Ratio of mean familiarity score for cued category novel images over uncued cateogry novel images, over time.')
    print('Sliding window length: '+ str(window_len)+' with overlap of '+str(overlap)+'. Confidence interval over subject means.')
    print('Total number of trials : 40 ')


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



# def pres_gaze(subdir, eye_df, interval='images'):
#     '''
#     input: subject's experiment df and eye track df
#     output: list of eye data df's
#             each df is either eye data from full pres block, or from single pres trial (interval='images')
#     '''
#
#     pres_gaze = []
#
#     for f in os.listdir(subdir):
#
#         stim=[]
#
#         if 'pres' in f:
#
#             pres_df = pd.read_csv(subdir+'/'+f)
#
#             if interval == 'images':
#                 start = pres_df['Stimulus Onset']
#                 end = pres_df['Stimulus End']
#                 cued_f = pres_df['Cued Face']
#                 cued_p = pres_df['Cued Place']
#                 uncued_f = pres_df['Uncued Face']
#                 uncued_p = pres_df['Uncued Place']
#
#
#             else:
#                 start = pres_df['Stimulus Onset'][0]
#                 end = pres_df['Stimulus End'][9]
#
#             for x,y,cf,cp,uf,up in zip(start,end,cued_f,cued_p,uncued_f,uncued_p):
#                 eye_df['Cued Side']=pres_df.iloc[0]['Cued Side']
#                 eye_df['Cued Category']=pres_df.iloc[0]['Cued Category']
#
#                 eye_df['Cued Face']=cf
#                 eye_df['Cued Place']=cp
#                 eye_df['Uncued Face']=uf
#                 eye_df['Uncued Place']=up
#
#
#                 # eye_df.loc[(eye_df['timestamp']>x) &
#                 #            (eye_df['timestamp']<y) &
#                 #            (eye_df['xRaw_righteye']>0.0) &
#                 #            (eye_df['xRaw_lefteye']>0.0)]['Image']=
#
#                 pres_gaze.append(eye_df.loc[(eye_df['timestamp']>x)&
#                                             (eye_df['timestamp']<y)&
#                                             (eye_df['xRaw_righteye']>0.0) &
#                                             (eye_df['xRaw_lefteye']>0.0)&
#                                             (eye_df['av_x_coord']<59.8)&
#                                             (eye_df['yRaw_lefteye']>0.0)&
#                                             (eye_df['yRaw_righteye']>0.0)&
#                                             (eye_df['av_y_coord']<33.6)])
#                 #stim.append()
#     return(pres_gaze)



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
# 
# def add_gaze(df):
#     for index,row in df.iterrows():
#         if row['Trial Type']=='Memory':
#             mem_image = row['Memory Image']
#             for cue in ['Cued ', 'Uncued ']:
#                 for cat in ['Face', 'Place']:
#                     if df.loc[df[cue+cat] == mem_image].shape[0]!=0:
#                         df['av_x_coord'][index]=df.loc[df[cue+cat] == mem_image]['av_x_coord']
#                         df['Cued Side'][index] = df.loc[df[cue+cat] == mem_image]['Cued Side'].item()
#
#     mem_mask = df['Trial Type']=='Memory'
#     df.loc[mem_mask,'av_x_coord'] = df.loc[mem_mask,'av_x_coord'].fillna(np.nan)
#
#     return(df)



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

    return(fig)



def gaze_box(trial, center, dims):
    '''
    inputs:  center - tuple indicating center of ROI (x,y)
             dims - tuple indicating dimensions of rectangle (width, height)
             trial - dataframe for single presentation trial (or block)

    outputs: box_num - raw number of gazepoints within box (int)
             proportion - proportion of this trial's gaze points within box (float)
             df - dataframe of all gazepoints within the box, including timestamps
    '''

    total_num = trial.shape[0]

    trial = trial[(trial['av_y_coord']>=(center[1]-dims[1]/2))&
                  (trial['av_y_coord']<=(center[1]+dims[1]/2))&
                  (trial['av_x_coord']>=(center[0]-dims[0]/2))&
                  (trial['av_x_coord']<=(center[0]+dims[0]/2))]

    df = trial

    if total_num>0:
        box_num = trial.shape[0]
        proportion = box_num/total_num
    else:
        box_num = np.nan
        proportion = np.nan

    return(box_num, proportion, df)

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
