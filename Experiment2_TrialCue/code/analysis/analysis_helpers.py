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

def add_level(df, trials='block'):
    '''
    input: subject dataframe
    output: subject dataframe w/ Attention Level string for each Memory trial row
    '''
    for x in df.Run.unique():
        mask = df['Run']==x

        if trials == 'block':
            df[mask] = run_level(df[mask])
        elif trials == 'unique':
            df[mask] = run_level_unique(df[mask])

    return(df)


def run_level(df):
    '''
    input: df containing pres and mem from single run
    output: df with string in 'Attention Level' column in each Memory trial row
    '''
    #cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    for index,row in df.iterrows():
        if row['Trial Type']=='Memory':
            mem_image = row['Memory Image']
            for cue in ['Cued ', 'Uncued ']:
                for cat in ['Face', 'Place']:
                    if df.loc[df[cue+cat] == mem_image].shape[0]!=0:
                        cued_cat = df.loc[df[cue+cat] == mem_image]['Cued Category']
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


def run_level_unique(df):
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

def ROC_plot(ROC_data):
    '''
    input: ROC proportions (dictionary)
    output: displays plot of ROC curve
    '''

    fig, ax = plt.subplots()

    for attn in ['Category', 'Full', 'None', 'Side']:
        ax.plot(ROC_data['Novel'], ROC_data[attn], '-o', label=attn)

    plt.legend(loc='upper left');
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


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

def t_tester(df):

    '''
    input : dataframe
    output: ttests for each attention level pairing
    '''

    l = {}
    pair = combinations(df['Attention Level'].unique(),2)

    for i in list(pair):
        if df[df['Attention Level']==i[0]]['Familiarity Rating'].shape[0]==df[df['Attention Level']==i[1]]['Familiarity Rating'].shape[0]:
            p = scipy.stats.ttest_rel(df[df['Attention Level']==i[0]]['Familiarity Rating'],
                              df[df['Attention Level']==i[1]]['Familiarity Rating'])
            l[i]=p

#         else:
#             p = scipy.stats.ttest_ind(df[df['Attention Level']==i[0]]['Familiarity Rating'],
#                   df[df['Attention Level']==i[1]]['Familiarity Rating'])
#             l[i]=p

    return(l)

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

    #print('Ratio of mean familiarity score for cued category novel images over uncued cateogry novel images, over time.')
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



def add_prop(df):
    '''
    input: df containing pres and mem from single run
    output: df with proportion of eye gaze for every image in memory block
    '''

    #cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    df['Image Prop']  = 0.0
    df['Center Prop'] = 0.0

    for index,row in df.iterrows():
        # for every memory trial
        if row['Trial Type']=='Memory':

            mem_image = row['Memory Image']
            mem_level = row['Attention Level']

            if mem_level in ['Full', 'Side']:
                cue = 'Cued '
                for cat in ['Face', 'Place']:
                    if df.loc[df['Cued '+cat] == mem_image].shape[0]!=0:
                        if df.loc[df[cue+cat] == mem_image]['Cued Side'].item()=='<':
                            image_prop = df.loc[df[cue+cat] == mem_image]['Lprop'].item()
                        else:
                            image_prop = df.loc[df[cue+cat] == mem_image]['Rprop'].item()

                        center_prop = df.loc[df[cue+cat] == mem_image]['Cprop'].item()

            elif mem_level in ['Category', 'None']:
                for cat in ['Face', 'Place']:
                    cue = 'Uncued '
                    if df.loc[df['Uncued '+cat] == mem_image].shape[0]!=0:
                        if df.loc[df[cue+cat] == mem_image]['Cued Side'].item()=='>':
                            image_prop = df.loc[df[cue+cat] == mem_image]['Lprop'].item()
                        else:
                            image_prop = df.loc[df[cue+cat] == mem_image]['Rprop'].item()

                        center_prop = df.loc[df[cue+cat] == mem_image]['Cprop'].item()

            else:
                image_prop  = np.nan
                center_prop = np.nan

            df['Image Prop'][index]  = image_prop
            df['Center Prop'][index] = center_prop

#     mem_mask = df['Trial Type']=='Memory'
#     df.loc[mem_mask,'Image Prop'] = df.loc[mem_mask,'Image Prop'].fillna('Novel')
#     df.loc[mem_mask,'Center Prop'] = df.loc[mem_mask,'Center Prop'].fillna('Novel')

    return(df)

def select_trials_2(behav_full, eye_df, width):
    '''
    input:   behavioral df, gaze df, desired width
    output:  trials with gaze within width of center (x axis)
    '''

    df_box = []
    gaze_three = []
    p_df = []

    for sub in eye_df['Subject'].unique():
    # for evey subject

        sub_df=[]

        chunk = eye_df[eye_df['Subject']==sub]
        # select data just for this subject

        for run in chunk['Run'].unique():
    #     # for every run

             for trial in chunk[chunk['Run']==run]['Trial'].unique():
    #         # for every trial

                 new_chunk = chunk[(chunk['Run']==run)&(chunk['Trial']==trial)]
    #             # select just the data for the run and trial

                 if new_chunk.shape[0] > 0 :
    #                 # if there's data for this run and trial

                    two = new_chunk[(abs(new_chunk['av_x_coord']-(59.8/2)) < width)].shape[0] / new_chunk.shape[0]
    #                 # what proportion of gaze points are within +/- 1.5 from center?

                    if two == 1:
                    # if 100%, these are trials we want

                        sub_df.append(pd.concat([behav_full[(behav_full['Subject']==sub) &
                                                 (behav_full['Run']==run) &
                                                  (behav_full['Trial']==trial)&
                                                  (behav_full['Trial Type']=='Presentation')]]))#,

    # #                                             behav_full[(behav_full['Subject']==sub) &
    # #                                             (behav_full['Run']==run) &
    # #                                             (behav_full['Trial Type']=='Memory')]]))

        sub_df.append(behav_full[(behav_full['Subject']==sub) & (behav_full['Trial Type']=='Memory')])

            # sub_df --> list of df's: [1] single good presentations, [2] all memory trials,


        if len(sub_df)>1:
            # if sub_df list has contents...

            sub_df = pd.concat(sub_df)
            df_box.append(sub_df)

            # concat into one df for the subject, then append to df_box
            # df box is a list of single sub df's containing 1) good pres trials and 2) possibly linked memory trials



    new_df_box = []

    for x in df_box:
        listy = list(x['Cued Place']) + list(x['Uncued Place']) + list(x['Cued Face']) + list(x['Uncued Face'])
        new_df_box.append(pd.concat([ x[x['Memory Image'].isin(listy)], x[x['Attention Level']=='Novel']]))
        ans = pd.concat(new_df_box)
        ans.ix[~ans['Memory Image'].str.contains("sun", na=False),'Category']='Face'
        ans.ix[ans['Memory Image'].str.contains("sun", na=False),'Category']='Place'

    return(ans)

def select_trials(behav_full, eye_df, width):
    '''
    input:   behavioral df, gaze df, desired width
    output:  trials with gaze within width of center (x axis)
    '''

    df_box = []
    gaze_three = []
    p_df = []

    for sub in eye_df['Subject'].unique():
    # for evey subject

        sub_df=[]
        gaze_threes = []
        pres_df = []

        chunk = eye_df[eye_df['Subject']==sub]

        for run in chunk['Run'].unique():
        # for every run

            for trial in range(0,10):
            # for every trial

                new_chunk = chunk[(chunk['Trial']==trial) & (chunk['Run']==run)]

                if new_chunk.shape[0] > 0 :
                    two = new_chunk[(abs(new_chunk['av_x_coord']-(59.8/2)) < 1.5)].shape[0] / new_chunk.shape[0]

                    if two == 1:

                        sub_df.append(pd.concat([behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial']==float(trial))],

                                                behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial Type']=='Memory')]]))

                        pres_df.append(behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial']==float(trial))&
                                                (behav_full['Trial Type']=='Presentation')])

                        gaze_threes.append(eye_df[(eye_df['Subject']==sub) &
                                                 (eye_df['Run']==run) &
                                                 (eye_df['Trial']==trial)])
        if len(sub_df)>0:
            sub_df = pd.concat(sub_df)
            df_box.append(sub_df)
            # df_box has all good trials and any possibly linked memory run

            gaze_threes = pd.concat(gaze_threes)
            gaze_three.append(gaze_threes)
            # gaze threes has gaze data from good trials only

            pres_df = pd.concat(pres_df)
            p_df.append(pres_df)
            # p_df has good presentation trials only


    new_df_box = []

    for x in df_box:
        listy = list(x['Cued Place']) + list(x['Uncued Place']) + list(x['Cued Face']) + list(x['Uncued Face'])
        new_df_box.append(pd.concat([ x[x['Memory Image'].isin(listy)], x[x['Attention Level']=='Novel']]))
        ans = pd.concat(new_df_box)
        ans.ix[~ans['Memory Image'].str.contains("sun", na=False),'Category']='Face'
        ans.ix[ans['Memory Image'].str.contains("sun", na=False),'Category']='Place'

    return(ans)

def eye_read(dir, out_str):
    '''
    input:  directory with gaze data
    output: gaze df, also saves pickle
    '''
    # "/Users/kirstenziman/Documents/attention-memory-task/data/"
    all_gaze = []

    for b in os.listdir(dir):
        print(b)
        dr = dir+b
        initial = eye_intial( dr + "/eye_data/")
        pres = pres_gaze_image(dr, initial, b[0:2])
        subject_gaze = pd.concat([pd.concat(pres[x]) for x in pres.keys()])
        all_gaze.append(subject_gaze)

    df = pd.concat(all_gaze)
    eye_df = df

    # convert to centimeters
    df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
    df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))
    # "/Users/kirstenziman/Documents/attention-memory-task/gaze_May_update.pkl"
    pickle.dump(df, open(out_str, "wb" ))

    return(df)

#####



# EYE GAZE DATA ANALYSIS FUNCTIONS

# class parseFile():
#     def __init__(self, file):
#         self.file = file
#     def parse(self):
#         data = open(self.file).read()
#         return(data)
#
# def load(path):
#     '''
#     input: path to directory containing eye track data
#     output: raw parsed eye data
#     '''
#
#     data = []
#     files = [f for f in os.listdir(path)]
#
#     for x in files:
#         #if os.path.isfile(path+x):
#         newFile = parseFile(path+x)
#         data1 = newFile.parse()
#
#         for a,b in zip(['true','false'], ['True', 'False']):
#             data1 = data1.replace(a, b)
#
#         data1 = data1.split('\n')
#         data1 = [x for x in data1 if "tracker" in x]
#         data.extend(data1)
#
#     return(data)
#
#
# def df_create(data):
#     """
#     input: raw parsed eye data
#     output: dataframe of eye data (screen location in centimeters)
#     """
#
#     dict_list = [ast.literal_eval(x) for x in data]
#     dict_list = [x['values']['frame'] for x in dict_list if 'frame' in x['values']]
#
#     df = pd.DataFrame(dict_list)
#
#     # right and left eye
#     for eye in ['righteye','lefteye']:
#         for coord in ['x','y']:
#             df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]
#
#     # convert to centimeters
#     df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
#     df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))
#
#     # convert timestamp
#     df['timestamp']=[time.mktime(time.strptime(x[:], "%Y-%m-%d %H:%M:%S.%f")) for x in df['timestamp']]
#
#     return(df)
#
#
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


# # def pres_gaze(subdir, eye_df, interval='images'):
# #     '''
# #     input: subject's experiment df and eye track df
# #     output: list of eye data df's
# #             each df is either eye data from full pres block, or from single pres trial (interval='images')
# #     '''
# #
# #     pres_gaze = []
# #
# #     for f in os.listdir(subdir):
# #
# #         stim=[]
# #
# #         if 'pres' in f:
# #
# #             pres_df = pd.read_csv(subdir+'/'+f)
# #
# #             if interval == 'images':
# #                 start = pres_df['Stimulus Onset']
# #                 end = pres_df['Stimulus End']
# #                 cued_f = pres_df['Cued Face']
# #                 cued_p = pres_df['Cued Place']
# #                 uncued_f = pres_df['Uncued Face']
# #                 uncued_p = pres_df['Uncued Place']
# #
# #
# #             else:
# #                 start = pres_df['Stimulus Onset'][0]
# #                 end = pres_df['Stimulus End'][9]
# #
# #             for x,y,cf,cp,uf,up in zip(start,end,cued_f,cued_p,uncued_f,uncued_p):
# #                 eye_df['Cued Side']=pres_df.iloc[0]['Cued Side']
# #                 eye_df['Cued Category']=pres_df.iloc[0]['Cued Category']
# #
# #                 eye_df['Cued Face']=cf
# #                 eye_df['Cued Place']=cp
# #                 eye_df['Uncued Face']=uf
# #                 eye_df['Uncued Place']=up
# #
# #
# #                 # eye_df.loc[(eye_df['timestamp']>x) &
# #                 #            (eye_df['timestamp']<y) &
# #                 #            (eye_df['xRaw_righteye']>0.0) &
# #                 #            (eye_df['xRaw_lefteye']>0.0)]['Image']=
# #
# #                 pres_gaze.append(eye_df.loc[(eye_df['timestamp']>x)&
# #                                             (eye_df['timestamp']<y)&
# #                                             (eye_df['xRaw_righteye']>0.0) &
# #                                             (eye_df['xRaw_lefteye']>0.0)&
# #                                             (eye_df['av_x_coord']<59.8)&
# #                                             (eye_df['yRaw_lefteye']>0.0)&
# #                                             (eye_df['yRaw_righteye']>0.0)&
# #                                             (eye_df['av_y_coord']<33.6)])
# #                 #stim.append()
# #     return(pres_gaze)
#
#
#
# def gaze_plot(df_list):
#
#     middle = 2048/2.0
#     quarter = (1304-744)/4.0
#
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, aspect='equal')
#
#     for x in df_list:
#         if x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Place':
#             color='green'
#         elif x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Face':
#             color='blue'
#         elif x['Cued Side'].all()=='<' and x['Cued Category'].all()=='Place':
#             color='orange'
#         else:
#             color='red'
#
#         x['Color']=color
#
#         ax1.plot(x['av_x_coord'], x['av_y_coord'], '.', color=color)
#         #props.append(x.loc[(x['av_x_coord']>middle-quarter) & (x['av_x_coord']<middle+quarter)])
#
#     rect1 = patches.Rectangle(((59.8/2.0)-8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
#     rect2 = patches.Rectangle(((59.8/2.0)+8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
#
#     # Add the patch to the Axes
#     ax1.add_patch(rect1)
#     ax1.add_patch(rect2)
#
#     # plt.legend(loc='upper left');
#     plt.ylim(0, 33.6)
#     plt.xlim(0, 59.8)
#     plt.show()
#
#     return(fig)
#
#
#
# def gaze_box(trial, center, dims):
#     '''
#     inputs:  center - tuple indicating center of ROI (x,y)
#              dims - tuple indicating dimensions of rectangle (width, height)
#              trial - dataframe for single presentation trial (or block)
#
#     outputs: box_num - raw number of gazepoints within box (int)
#              proportion - proportion of this trial's gaze points within box (float)
#              df - dataframe of all gazepoints within the box, including timestamps
#     '''
#
#     total_num = trial.shape[0]
#
#     trial = trial[(trial['av_y_coord']>=(center[1]-dims[1]/2))&
#                   (trial['av_y_coord']<=(center[1]+dims[1]/2))&
#                   (trial['av_x_coord']>=(center[0]-dims[0]/2))&
#                   (trial['av_x_coord']<=(center[0]+dims[0]/2))]
#
#     df = trial
#
#     if total_num>0:
#         box_num = trial.shape[0]
#         proportion = box_num/total_num
#     else:
#         box_num = np.nan
#         proportion = np.nan
#
#     return(box_num, proportion, df)

# HELPER FUNCTIONS FOR ATTENTION AND MEMORY ANALYSES




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

def add_level(df, trials='block'):
    '''
    input: subject dataframe
    output: subject dataframe w/ Attention Level string for each Memory trial row
    '''
    for x in df.Run.unique():
        mask = df['Run']==x

        if trials == 'block':
            df[mask] = run_level(df[mask])
        elif trials == 'unique':
            df[mask] = run_level_unique(df[mask])

    return(df)


def run_level(df):
    '''
    input: df containing pres and mem from single run
    output: df with string in 'Attention Level' column in each Memory trial row
    '''
    #cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    for index,row in df.iterrows():
        if row['Trial Type']=='Memory':
            mem_image = row['Memory Image']
            for cue in ['Cued ', 'Uncued ']:
                for cat in ['Face', 'Place']:
                    if df.loc[df[cue+cat] == mem_image].shape[0]!=0:
                        cued_cat = df.loc[df[cue+cat] == mem_image]['Cued Category']
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


def run_level_unique(df):
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

def ROC_plot(ROC_data):
    '''
    input: ROC proportions (dictionary)
    output: displays plot of ROC curve
    '''

    fig, ax = plt.subplots()

    for attn in ['Category', 'Full', 'None', 'Side']:
        ax.plot(ROC_data['Novel'], ROC_data[attn], '-o', label=attn)

    plt.legend(loc='upper left');
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


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

def t_tester(df):

    '''
    input : dataframe
    output: ttests for each attention level pairing
    '''

    l = {}
    pair = combinations(df['Attention Level'].unique(),2)

    for i in list(pair):
        if df[df['Attention Level']==i[0]]['Familiarity Rating'].shape[0]==df[df['Attention Level']==i[1]]['Familiarity Rating'].shape[0]:
            p = scipy.stats.ttest_rel(df[df['Attention Level']==i[0]]['Familiarity Rating'],
                              df[df['Attention Level']==i[1]]['Familiarity Rating'])
            l[i]=p

#         else:
#             p = scipy.stats.ttest_ind(df[df['Attention Level']==i[0]]['Familiarity Rating'],
#                   df[df['Attention Level']==i[1]]['Familiarity Rating'])
#             l[i]=p

    return(l)

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

    #print('Ratio of mean familiarity score for cued category novel images over uncued cateogry novel images, over time.')
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

def add_level(df, trials='block'):
    '''
    input: subject dataframe
    output: subject dataframe w/ Attention Level string for each Memory trial row
    '''
    for x in df.Run.unique():
        mask = df['Run']==x

        if trials == 'block':
            df[mask] = run_level(df[mask])
        elif trials == 'unique':
            df[mask] = run_level_unique(df[mask])

    return(df)


def run_level(df):
    '''
    input: df containing pres and mem from single run
    output: df with string in 'Attention Level' column in each Memory trial row
    '''
    #cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    for index,row in df.iterrows():
        if row['Trial Type']=='Memory':
            mem_image = row['Memory Image']
            for cue in ['Cued ', 'Uncued ']:
                for cat in ['Face', 'Place']:
                    if df.loc[df[cue+cat] == mem_image].shape[0]!=0:
                        cued_cat = df.loc[df[cue+cat] == mem_image]['Cued Category']
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


def run_level_unique(df):
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

def ROC_plot(ROC_data):
    '''
    input: ROC proportions (dictionary)
    output: displays plot of ROC curve
    '''

    fig, ax = plt.subplots()

    for attn in ['Category', 'Full', 'None', 'Side']:
        ax.plot(ROC_data['Novel'], ROC_data[attn], '-o', label=attn)

    plt.legend(loc='upper left');
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


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

def t_tester(df):

    '''
    input : dataframe
    output: ttests for each attention level pairing
    '''

    l = {}
    pair = combinations(df['Attention Level'].unique(),2)

    for i in list(pair):
        if df[df['Attention Level']==i[0]]['Familiarity Rating'].shape[0]==df[df['Attention Level']==i[1]]['Familiarity Rating'].shape[0]:
            p = scipy.stats.ttest_rel(df[df['Attention Level']==i[0]]['Familiarity Rating'],
                              df[df['Attention Level']==i[1]]['Familiarity Rating'])
            l[i]=p

#         else:
#             p = scipy.stats.ttest_ind(df[df['Attention Level']==i[0]]['Familiarity Rating'],
#                   df[df['Attention Level']==i[1]]['Familiarity Rating'])
#             l[i]=p

    return(l)

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

    #print('Ratio of mean familiarity score for cued category novel images over uncued cateogry novel images, over time.')
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



def add_prop(df):
    '''
    input: df containing pres and mem from single run
    output: df with proportion of eye gaze for every image in memory block
    '''

    #cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    df['Image Prop']  = 0.0
    df['Center Prop'] = 0.0

    for index,row in df.iterrows():
        # for every memory trial
        if row['Trial Type']=='Memory':

            mem_image = row['Memory Image']
            mem_level = row['Attention Level']

            if mem_level in ['Full', 'Side']:
                cue = 'Cued '
                for cat in ['Face', 'Place']:
                    if df.loc[df['Cued '+cat] == mem_image].shape[0]!=0:
                        if df.loc[df[cue+cat] == mem_image]['Cued Side'].item()=='<':
                            image_prop = df.loc[df[cue+cat] == mem_image]['Lprop'].item()
                        else:
                            image_prop = df.loc[df[cue+cat] == mem_image]['Rprop'].item()

                        center_prop = df.loc[df[cue+cat] == mem_image]['Cprop'].item()

            elif mem_level in ['Category', 'None']:
                for cat in ['Face', 'Place']:
                    cue = 'Uncued '
                    if df.loc[df['Uncued '+cat] == mem_image].shape[0]!=0:
                        if df.loc[df[cue+cat] == mem_image]['Cued Side'].item()=='>':
                            image_prop = df.loc[df[cue+cat] == mem_image]['Lprop'].item()
                        else:
                            image_prop = df.loc[df[cue+cat] == mem_image]['Rprop'].item()

                        center_prop = df.loc[df[cue+cat] == mem_image]['Cprop'].item()

            else:
                image_prop  = np.nan
                center_prop = np.nan

            df['Image Prop'][index]  = image_prop
            df['Center Prop'][index] = center_prop

#     mem_mask = df['Trial Type']=='Memory'
#     df.loc[mem_mask,'Image Prop'] = df.loc[mem_mask,'Image Prop'].fillna('Novel')
#     df.loc[mem_mask,'Center Prop'] = df.loc[mem_mask,'Center Prop'].fillna('Novel')

    return(df)

def select_trials_2(behav_full, eye_df, width):
    '''
    input:   behavioral df, gaze df, desired width
    output:  trials with gaze within width of center (x axis)
    '''

    df_box = []
    gaze_three = []
    p_df = []

    for sub in eye_df['Subject'].unique():
    # for evey subject

        sub_df=[]

        chunk = eye_df[eye_df['Subject']==sub]
        # select data just for this subject

        for run in chunk['Run'].unique():
    #     # for every run

             for trial in chunk[chunk['Run']==run]['Trial'].unique():
    #         # for every trial

                 new_chunk = chunk[(chunk['Run']==run)&(chunk['Trial']==trial)]
    #             # select just the data for the run and trial

                 if new_chunk.shape[0] > 0 :
    #                 # if there's data for this run and trial

                    two = new_chunk[(abs(new_chunk['av_x_coord']-(59.8/2)) < width)].shape[0] / new_chunk.shape[0]
    #                 # what proportion of gaze points are within +/- 1.5 from center?

                    if two == 1:
                    # if 100%, these are trials we want

                        sub_df.append(pd.concat([behav_full[(behav_full['Subject']==sub) &
                                                 (behav_full['Run']==run) &
                                                  (behav_full['Trial']==trial)&
                                                  (behav_full['Trial Type']=='Presentation')]]))#,

    # #                                             behav_full[(behav_full['Subject']==sub) &
    # #                                             (behav_full['Run']==run) &
    # #                                             (behav_full['Trial Type']=='Memory')]]))

        sub_df.append(behav_full[(behav_full['Subject']==sub) & (behav_full['Trial Type']=='Memory')])

            # sub_df --> list of df's: [1] single good presentations, [2] all memory trials,


        if len(sub_df)>1:
            # if sub_df list has contents...

            sub_df = pd.concat(sub_df)
            df_box.append(sub_df)

            # concat into one df for the subject, then append to df_box
            # df box is a list of single sub df's containing 1) good pres trials and 2) possibly linked memory trials



    new_df_box = []

    for x in df_box:
        listy = list(x['Cued Place']) + list(x['Uncued Place']) + list(x['Cued Face']) + list(x['Uncued Face'])
        new_df_box.append(pd.concat([ x[x['Memory Image'].isin(listy)], x[x['Attention Level']=='Novel']]))
        ans = pd.concat(new_df_box)
        ans.ix[~ans['Memory Image'].str.contains("sun", na=False),'Category']='Face'
        ans.ix[ans['Memory Image'].str.contains("sun", na=False),'Category']='Place'

    return(ans)

def select_trials(behav_full, eye_df, width):
    '''
    input:   behavioral df, gaze df, desired width
    output:  trials with gaze within width of center (x axis)
    '''

    df_box = []
    gaze_three = []
    p_df = []

    for sub in eye_df['Subject'].unique():
    # for evey subject

        sub_df=[]
        gaze_threes = []
        pres_df = []

        chunk = eye_df[eye_df['Subject']==sub]

        for run in chunk['Run'].unique():
        # for every run

            for trial in range(0,10):
            # for every trial

                new_chunk = chunk[(chunk['Trial']==trial) & (chunk['Run']==run)]

                if new_chunk.shape[0] > 0 :
                    two = new_chunk[(abs(new_chunk['av_x_coord']-(59.8/2)) < 1.5)].shape[0] / new_chunk.shape[0]

                    if two == 1:

                        sub_df.append(pd.concat([behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial']==float(trial))],

                                                behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial Type']=='Memory')]]))

                        pres_df.append(behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial']==float(trial))&
                                                (behav_full['Trial Type']=='Presentation')])

                        gaze_threes.append(eye_df[(eye_df['Subject']==sub) &
                                                 (eye_df['Run']==run) &
                                                 (eye_df['Trial']==trial)])
        if len(sub_df)>0:
            sub_df = pd.concat(sub_df)
            df_box.append(sub_df)
            # df_box has all good trials and any possibly linked memory run

            gaze_threes = pd.concat(gaze_threes)
            gaze_three.append(gaze_threes)
            # gaze threes has gaze data from good trials only

            pres_df = pd.concat(pres_df)
            p_df.append(pres_df)
            # p_df has good presentation trials only


    new_df_box = []

    for x in df_box:
        listy = list(x['Cued Place']) + list(x['Uncued Place']) + list(x['Cued Face']) + list(x['Uncued Face'])
        new_df_box.append(pd.concat([ x[x['Memory Image'].isin(listy)], x[x['Attention Level']=='Novel']]))
        ans = pd.concat(new_df_box)
        ans.ix[~ans['Memory Image'].str.contains("sun", na=False),'Category']='Face'
        ans.ix[ans['Memory Image'].str.contains("sun", na=False),'Category']='Place'

    return(ans)

def eye_read(dir, out_str):
    '''
    input:  directory with gaze data
    output: gaze df, also saves pickle
    '''
    # "/Users/kirstenziman/Documents/attention-memory-task/data/"
    all_gaze = []

    for b in os.listdir(dir):
        print(b)
        dr = dir+b
        initial = eye_intial( dr + "/eye_data/")
        pres = pres_gaze_image(dr, initial, b[0:2])
        subject_gaze = pd.concat([pd.concat(pres[x]) for x in pres.keys()])
        all_gaze.append(subject_gaze)

    df = pd.concat(all_gaze)
    eye_df = df

    # convert to centimeters
    df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
    df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))
    # "/Users/kirstenziman/Documents/attention-memory-task/gaze_May_update.pkl"
    pickle.dump(df, open(out_str, "wb" ))

    return(df)

#####



# EYE GAZE DATA ANALYSIS FUNCTIONS

# class parseFile():
#     def __init__(self, file):
#         self.file = file
#     def parse(self):
#         data = open(self.file).read()
#         return(data)
#
# def load(path):
#     '''
#     input: path to directory containing eye track data
#     output: raw parsed eye data
#     '''
#
#     data = []
#     files = [f for f in os.listdir(path)]
#
#     for x in files:
#         #if os.path.isfile(path+x):
#         newFile = parseFile(path+x)
#         data1 = newFile.parse()
#
#         for a,b in zip(['true','false'], ['True', 'False']):
#             data1 = data1.replace(a, b)
#
#         data1 = data1.split('\n')
#         data1 = [x for x in data1 if "tracker" in x]
#         data.extend(data1)
#
#     return(data)
#
#
# def df_create(data):
#     """
#     input: raw parsed eye data
#     output: dataframe of eye data (screen location in centimeters)
#     """
#
#     dict_list = [ast.literal_eval(x) for x in data]
#     dict_list = [x['values']['frame'] for x in dict_list if 'frame' in x['values']]
#
#     df = pd.DataFrame(dict_list)
#
#     # right and left eye
#     for eye in ['righteye','lefteye']:
#         for coord in ['x','y']:
#             df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]
#
#     # convert to centimeters
#     df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
#     df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))
#
#     # convert timestamp
#     df['timestamp']=[time.mktime(time.strptime(x[:], "%Y-%m-%d %H:%M:%S.%f")) for x in df['timestamp']]
#
#     return(df)
#
#
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


# # def pres_gaze(subdir, eye_df, interval='images'):
# #     '''
# #     input: subject's experiment df and eye track df
# #     output: list of eye data df's
# #             each df is either eye data from full pres block, or from single pres trial (interval='images')
# #     '''
# #
# #     pres_gaze = []
# #
# #     for f in os.listdir(subdir):
# #
# #         stim=[]
# #
# #         if 'pres' in f:
# #
# #             pres_df = pd.read_csv(subdir+'/'+f)
# #
# #             if interval == 'images':
# #                 start = pres_df['Stimulus Onset']
# #                 end = pres_df['Stimulus End']
# #                 cued_f = pres_df['Cued Face']
# #                 cued_p = pres_df['Cued Place']
# #                 uncued_f = pres_df['Uncued Face']
# #                 uncued_p = pres_df['Uncued Place']
# #
# #
# #             else:
# #                 start = pres_df['Stimulus Onset'][0]
# #                 end = pres_df['Stimulus End'][9]
# #
# #             for x,y,cf,cp,uf,up in zip(start,end,cued_f,cued_p,uncued_f,uncued_p):
# #                 eye_df['Cued Side']=pres_df.iloc[0]['Cued Side']
# #                 eye_df['Cued Category']=pres_df.iloc[0]['Cued Category']
# #
# #                 eye_df['Cued Face']=cf
# #                 eye_df['Cued Place']=cp
# #                 eye_df['Uncued Face']=uf
# #                 eye_df['Uncued Place']=up
# #
# #
# #                 # eye_df.loc[(eye_df['timestamp']>x) &
# #                 #            (eye_df['timestamp']<y) &
# #                 #            (eye_df['xRaw_righteye']>0.0) &
# #                 #            (eye_df['xRaw_lefteye']>0.0)]['Image']=
# #
# #                 pres_gaze.append(eye_df.loc[(eye_df['timestamp']>x)&
# #                                             (eye_df['timestamp']<y)&
# #                                             (eye_df['xRaw_righteye']>0.0) &
# #                                             (eye_df['xRaw_lefteye']>0.0)&
# #                                             (eye_df['av_x_coord']<59.8)&
# #                                             (eye_df['yRaw_lefteye']>0.0)&
# #                                             (eye_df['yRaw_righteye']>0.0)&
# #                                             (eye_df['av_y_coord']<33.6)])
# #                 #stim.append()
# #     return(pres_gaze)
#
#
#
# def gaze_plot(df_list):
#
#     middle = 2048/2.0
#     quarter = (1304-744)/4.0
#
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, aspect='equal')
#
#     for x in df_list:
#         if x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Place':
#             color='green'
#         elif x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Face':
#             color='blue'
#         elif x['Cued Side'].all()=='<' and x['Cued Category'].all()=='Place':
#             color='orange'
#         else:
#             color='red'
#
#         x['Color']=color
#
#         ax1.plot(x['av_x_coord'], x['av_y_coord'], '.', color=color)
#         #props.append(x.loc[(x['av_x_coord']>middle-quarter) & (x['av_x_coord']<middle+quarter)])
#
#     rect1 = patches.Rectangle(((59.8/2.0)-8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
#     rect2 = patches.Rectangle(((59.8/2.0)+8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
#
#     # Add the patch to the Axes
#     ax1.add_patch(rect1)
#     ax1.add_patch(rect2)
#
#     # plt.legend(loc='upper left');
#     plt.ylim(0, 33.6)
#     plt.xlim(0, 59.8)
#     plt.show()
#
#     return(fig)
#
#
#
# def gaze_box(trial, center, dims):
#     '''
#     inputs:  center - tuple indicating center of ROI (x,y)
#              dims - tuple indicating dimensions of rectangle (width, height)
#              trial - dataframe for single presentation trial (or block)
#
#     outputs: box_num - raw number of gazepoints within box (int)
#              proportion - proportion of this trial's gaze points within box (float)
#              df - dataframe of all gazepoints within the box, including timestamps
#     '''
#
#     total_num = trial.shape[0]
#
#     trial = trial[(trial['av_y_coord']>=(center[1]-dims[1]/2))&
#                   (trial['av_y_coord']<=(center[1]+dims[1]/2))&
#                   (trial['av_x_coord']>=(center[0]-dims[0]/2))&
#                   (trial['av_x_coord']<=(center[0]+dims[0]/2))]
#
#     df = trial
#
#     if total_num>0:
#         box_num = trial.shape[0]
#         proportion = box_num/total_num
#     else:
#         box_num = np.nan
#         proportion = np.nan
#
#     return(box_num, proportion, df)
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



def add_prop(df):
    '''
    input: df containing pres and mem from single run
    output: df with proportion of eye gaze for every image in memory block
    '''

    #cued_cat = df[df['Trial Type']=='Presentation']['Cued Category'].tolist()[0]

    df['Image Prop']  = 0.0
    df['Center Prop'] = 0.0

    for index,row in df.iterrows():
        # for every memory trial
        if row['Trial Type']=='Memory':

            mem_image = row['Memory Image']
            mem_level = row['Attention Level']

            if mem_level in ['Full', 'Side']:
                cue = 'Cued '
                for cat in ['Face', 'Place']:
                    if df.loc[df['Cued '+cat] == mem_image].shape[0]!=0:
                        if df.loc[df[cue+cat] == mem_image]['Cued Side'].item()=='<':
                            image_prop = df.loc[df[cue+cat] == mem_image]['Lprop'].item()
                        else:
                            image_prop = df.loc[df[cue+cat] == mem_image]['Rprop'].item()

                        center_prop = df.loc[df[cue+cat] == mem_image]['Cprop'].item()

            elif mem_level in ['Category', 'None']:
                for cat in ['Face', 'Place']:
                    cue = 'Uncued '
                    if df.loc[df['Uncued '+cat] == mem_image].shape[0]!=0:
                        if df.loc[df[cue+cat] == mem_image]['Cued Side'].item()=='>':
                            image_prop = df.loc[df[cue+cat] == mem_image]['Lprop'].item()
                        else:
                            image_prop = df.loc[df[cue+cat] == mem_image]['Rprop'].item()

                        center_prop = df.loc[df[cue+cat] == mem_image]['Cprop'].item()

            else:
                image_prop  = np.nan
                center_prop = np.nan

            df['Image Prop'][index]  = image_prop
            df['Center Prop'][index] = center_prop

#     mem_mask = df['Trial Type']=='Memory'
#     df.loc[mem_mask,'Image Prop'] = df.loc[mem_mask,'Image Prop'].fillna('Novel')
#     df.loc[mem_mask,'Center Prop'] = df.loc[mem_mask,'Center Prop'].fillna('Novel')

    return(df)

def select_trials_2(behav_full, eye_df, width):
    '''
    input:   behavioral df, gaze df, desired width
    output:  trials with gaze within width of center (x axis)
    '''

    df_box = []
    gaze_three = []
    p_df = []

    for sub in eye_df['Subject'].unique():
    # for evey subject

        sub_df=[]

        chunk = eye_df[eye_df['Subject']==sub]
        # select data just for this subject

        for run in chunk['Run'].unique():
    #     # for every run

             for trial in chunk[chunk['Run']==run]['Trial'].unique():
    #         # for every trial

                 new_chunk = chunk[(chunk['Run']==run)&(chunk['Trial']==trial)]
    #             # select just the data for the run and trial

                 if new_chunk.shape[0] > 0 :
    #                 # if there's data for this run and trial

                    two = new_chunk[(abs(new_chunk['av_x_coord']-(59.8/2)) < width)].shape[0] / new_chunk.shape[0]
    #                 # what proportion of gaze points are within +/- 1.5 from center?

                    if two == 1:
                    # if 100%, these are trials we want

                        sub_df.append(pd.concat([behav_full[(behav_full['Subject']==sub) &
                                                 (behav_full['Run']==run) &
                                                  (behav_full['Trial']==trial)&
                                                  (behav_full['Trial Type']=='Presentation')]]))#,

    # #                                             behav_full[(behav_full['Subject']==sub) &
    # #                                             (behav_full['Run']==run) &
    # #                                             (behav_full['Trial Type']=='Memory')]]))

        sub_df.append(behav_full[(behav_full['Subject']==sub) & (behav_full['Trial Type']=='Memory')])

            # sub_df --> list of df's: [1] single good presentations, [2] all memory trials,


        if len(sub_df)>1:
            # if sub_df list has contents...

            sub_df = pd.concat(sub_df)
            df_box.append(sub_df)

            # concat into one df for the subject, then append to df_box
            # df box is a list of single sub df's containing 1) good pres trials and 2) possibly linked memory trials



    new_df_box = []

    for x in df_box:
        listy = list(x['Cued Place']) + list(x['Uncued Place']) + list(x['Cued Face']) + list(x['Uncued Face'])
        new_df_box.append(pd.concat([ x[x['Memory Image'].isin(listy)], x[x['Attention Level']=='Novel']]))
        ans = pd.concat(new_df_box)
        ans.ix[~ans['Memory Image'].str.contains("sun", na=False),'Category']='Face'
        ans.ix[ans['Memory Image'].str.contains("sun", na=False),'Category']='Place'

    return(ans)

def select_trials(behav_full, eye_df, width):
    '''
    input:   behavioral df, gaze df, desired width
    output:  trials with gaze within width of center (x axis)
    '''

    df_box = []
    gaze_three = []
    p_df = []

    for sub in eye_df['Subject'].unique():
    # for evey subject

        sub_df=[]
        gaze_threes = []
        pres_df = []

        chunk = eye_df[eye_df['Subject']==sub]

        for run in chunk['Run'].unique():
        # for every run

            for trial in range(0,10):
            # for every trial

                new_chunk = chunk[(chunk['Trial']==trial) & (chunk['Run']==run)]

                if new_chunk.shape[0] > 0 :
                    two = new_chunk[(abs(new_chunk['av_x_coord']-(59.8/2)) < 1.5)].shape[0] / new_chunk.shape[0]

                    if two == 1:

                        sub_df.append(pd.concat([behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial']==float(trial))],

                                                behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial Type']=='Memory')]]))

                        pres_df.append(behav_full[(behav_full['Subject']==int(sub)) &
                                                 (behav_full['Run']==float(run)) &
                                                  (behav_full['Trial']==float(trial))&
                                                (behav_full['Trial Type']=='Presentation')])

                        gaze_threes.append(eye_df[(eye_df['Subject']==sub) &
                                                 (eye_df['Run']==run) &
                                                 (eye_df['Trial']==trial)])
        if len(sub_df)>0:
            sub_df = pd.concat(sub_df)
            df_box.append(sub_df)
            # df_box has all good trials and any possibly linked memory run

            gaze_threes = pd.concat(gaze_threes)
            gaze_three.append(gaze_threes)
            # gaze threes has gaze data from good trials only

            pres_df = pd.concat(pres_df)
            p_df.append(pres_df)
            # p_df has good presentation trials only


    new_df_box = []

    for x in df_box:
        listy = list(x['Cued Place']) + list(x['Uncued Place']) + list(x['Cued Face']) + list(x['Uncued Face'])
        new_df_box.append(pd.concat([ x[x['Memory Image'].isin(listy)], x[x['Attention Level']=='Novel']]))
        ans = pd.concat(new_df_box)
        ans.ix[~ans['Memory Image'].str.contains("sun", na=False),'Category']='Face'
        ans.ix[ans['Memory Image'].str.contains("sun", na=False),'Category']='Place'

    return(ans)

def eye_read(dir, out_str):
    '''
    input:  directory with gaze data
    output: gaze df, also saves pickle
    '''
    # "/Users/kirstenziman/Documents/attention-memory-task/data/"
    all_gaze = []

    for b in os.listdir(dir):
        print(b)
        dr = dir+b
        initial = eye_intial( dr + "/eye_data/")
        pres = pres_gaze_image(dr, initial, b[0:2])
        subject_gaze = pd.concat([pd.concat(pres[x]) for x in pres.keys()])
        all_gaze.append(subject_gaze)

    df = pd.concat(all_gaze)
    eye_df = df

    # convert to centimeters
    df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
    df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))
    # "/Users/kirstenziman/Documents/attention-memory-task/gaze_May_update.pkl"
    pickle.dump(df, open(out_str, "wb" ))

    return(df)

#####



# EYE GAZE DATA ANALYSIS FUNCTIONS

# class parseFile():
#     def __init__(self, file):
#         self.file = file
#     def parse(self):
#         data = open(self.file).read()
#         return(data)
#
# def load(path):
#     '''
#     input: path to directory containing eye track data
#     output: raw parsed eye data
#     '''
#
#     data = []
#     files = [f for f in os.listdir(path)]
#
#     for x in files:
#         #if os.path.isfile(path+x):
#         newFile = parseFile(path+x)
#         data1 = newFile.parse()
#
#         for a,b in zip(['true','false'], ['True', 'False']):
#             data1 = data1.replace(a, b)
#
#         data1 = data1.split('\n')
#         data1 = [x for x in data1 if "tracker" in x]
#         data.extend(data1)
#
#     return(data)
#
#
# def df_create(data):
#     """
#     input: raw parsed eye data
#     output: dataframe of eye data (screen location in centimeters)
#     """
#
#     dict_list = [ast.literal_eval(x) for x in data]
#     dict_list = [x['values']['frame'] for x in dict_list if 'frame' in x['values']]
#
#     df = pd.DataFrame(dict_list)
#
#     # right and left eye
#     for eye in ['righteye','lefteye']:
#         for coord in ['x','y']:
#             df[coord+'Raw_'+eye] = [df[eye][row]['raw'][coord] for row in df.index.values]
#
#     # convert to centimeters
#     df['av_x_coord'] = (59.8/2048)*(df[['xRaw_righteye', 'xRaw_lefteye']].mean(axis=1))
#     df['av_y_coord'] = (33.6/1152)*(df[['yRaw_righteye', 'yRaw_lefteye']].mean(axis=1))
#
#     # convert timestamp
#     df['timestamp']=[time.mktime(time.strptime(x[:], "%Y-%m-%d %H:%M:%S.%f")) for x in df['timestamp']]
#
#     return(df)
#
#
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


# # def pres_gaze(subdir, eye_df, interval='images'):
# #     '''
# #     input: subject's experiment df and eye track df
# #     output: list of eye data df's
# #             each df is either eye data from full pres block, or from single pres trial (interval='images')
# #     '''
# #
# #     pres_gaze = []
# #
# #     for f in os.listdir(subdir):
# #
# #         stim=[]
# #
# #         if 'pres' in f:
# #
# #             pres_df = pd.read_csv(subdir+'/'+f)
# #
# #             if interval == 'images':
# #                 start = pres_df['Stimulus Onset']
# #                 end = pres_df['Stimulus End']
# #                 cued_f = pres_df['Cued Face']
# #                 cued_p = pres_df['Cued Place']
# #                 uncued_f = pres_df['Uncued Face']
# #                 uncued_p = pres_df['Uncued Place']
# #
# #
# #             else:
# #                 start = pres_df['Stimulus Onset'][0]
# #                 end = pres_df['Stimulus End'][9]
# #
# #             for x,y,cf,cp,uf,up in zip(start,end,cued_f,cued_p,uncued_f,uncued_p):
# #                 eye_df['Cued Side']=pres_df.iloc[0]['Cued Side']
# #                 eye_df['Cued Category']=pres_df.iloc[0]['Cued Category']
# #
# #                 eye_df['Cued Face']=cf
# #                 eye_df['Cued Place']=cp
# #                 eye_df['Uncued Face']=uf
# #                 eye_df['Uncued Place']=up
# #
# #
# #                 # eye_df.loc[(eye_df['timestamp']>x) &
# #                 #            (eye_df['timestamp']<y) &
# #                 #            (eye_df['xRaw_righteye']>0.0) &
# #                 #            (eye_df['xRaw_lefteye']>0.0)]['Image']=
# #
# #                 pres_gaze.append(eye_df.loc[(eye_df['timestamp']>x)&
# #                                             (eye_df['timestamp']<y)&
# #                                             (eye_df['xRaw_righteye']>0.0) &
# #                                             (eye_df['xRaw_lefteye']>0.0)&
# #                                             (eye_df['av_x_coord']<59.8)&
# #                                             (eye_df['yRaw_lefteye']>0.0)&
# #                                             (eye_df['yRaw_righteye']>0.0)&
# #                                             (eye_df['av_y_coord']<33.6)])
# #                 #stim.append()
# #     return(pres_gaze)
#
#
#
# def gaze_plot(df_list):
#
#     middle = 2048/2.0
#     quarter = (1304-744)/4.0
#
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, aspect='equal')
#
#     for x in df_list:
#         if x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Place':
#             color='green'
#         elif x['Cued Side'].all()=='>' and x['Cued Category'].all()=='Face':
#             color='blue'
#         elif x['Cued Side'].all()=='<' and x['Cued Category'].all()=='Place':
#             color='orange'
#         else:
#             color='red'
#
#         x['Color']=color
#
#         ax1.plot(x['av_x_coord'], x['av_y_coord'], '.', color=color)
#         #props.append(x.loc[(x['av_x_coord']>middle-quarter) & (x['av_x_coord']<middle+quarter)])
#
#     rect1 = patches.Rectangle(((59.8/2.0)-8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
#     rect2 = patches.Rectangle(((59.8/2.0)+8-3.5,(33.6/2)-3.5),7,7,linewidth=1,edgecolor='black',facecolor='none')
#
#     # Add the patch to the Axes
#     ax1.add_patch(rect1)
#     ax1.add_patch(rect2)
#
#     # plt.legend(loc='upper left');
#     plt.ylim(0, 33.6)
#     plt.xlim(0, 59.8)
#     plt.show()
#
#     return(fig)
#
#
#
# def gaze_box(trial, center, dims):
#     '''
#     inputs:  center - tuple indicating center of ROI (x,y)
#              dims - tuple indicating dimensions of rectangle (width, height)
#              trial - dataframe for single presentation trial (or block)
#
#     outputs: box_num - raw number of gazepoints within box (int)
#              proportion - proportion of this trial's gaze points within box (float)
#              df - dataframe of all gazepoints within the box, including timestamps
#     '''
#
#     total_num = trial.shape[0]
#
#     trial = trial[(trial['av_y_coord']>=(center[1]-dims[1]/2))&
#                   (trial['av_y_coord']<=(center[1]+dims[1]/2))&
#                   (trial['av_x_coord']>=(center[0]-dims[0]/2))&
#                   (trial['av_x_coord']<=(center[0]+dims[0]/2))]
#
#     df = trial
#
#     if total_num>0:
#         box_num = trial.shape[0]
#         proportion = box_num/total_num
#     else:
#         box_num = np.nan
#         proportion = np.nan
#
#     return(box_num, proportion, df)
