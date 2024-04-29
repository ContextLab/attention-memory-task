import os
import shutil
import time
import requests
import pandas as pd
import numpy as np
import warnings
import json
import matplotlib as mpl
from matplotlib import pyplot as plt

from tqdm import tqdm
from glob import glob as lsdir
from datetime import datetime

basedir = os.path.split(os.getcwd())[0]
datadir = os.path.join(basedir, 'data')
figdir = os.path.join(basedir, 'paper', 'figs', 'source')

if not os.path.exists(figdir):
    os.makedirs(figdir)

if not os.path.exists(datadir):
    os.makedirs(datadir)

attention_colors = {
    'Attended': '#BE1E2D',
    'Attended category': '#F15A29',
    'Attended location': '#F9ED32',
    'Unattended': '#009444',
    'Novel': '#27AAE1',
    'Face': '#000000',
    'Place': '#000000'
}


def download_data():
    data_url = 'https://www.dropbox.com/s/6w8iemlqjyubn05/data.zip?dl=1'
    data_fname = os.path.join(basedir, 'data.zip')
    checkfile_fname = os.path.join(datadir, 'checkfile.txt')

    if not os.path.exists(data_fname) and not os.path.exists(checkfile_fname):
        print('Downloading data...')
        r = requests.get(data_url, allow_redirects=True)
        open(data_fname, 'wb').write(r.content)

    if os.path.exists(data_fname) and not os.path.exists(checkfile_fname):
        print('Unzipping data...')
        shutil.unpack_archive(data_fname, datadir)
        os.remove(data_fname)

        with open(checkfile_fname, 'w') as f:
            f.write('download complete.')

def parse_behavioral_data(datadir):
    def get_pres_time(image, stim_type, log):
        if type(image) is str:
            image_times = log.loc[log['Info'].apply(lambda x: (image in x) and (stim_type in x) if type(x) is str else False)]
            assert image_times.shape[0] == 4, Exception(f'Image {image} appears the wrong number of times')
            return image_times.iloc[-2]['Time'], image_times.iloc[-1]['Time']
        else:
            return np.nan, np.nan
        
    def add_timing_info(subj_df):
        def timing_helper(x, log):
            image = np.nan
            stim_type = ''
            if image is np.nan:
                image = x['Cued Composite']
                stim_type = 'CUED COMPOSITE'
            if image is np.nan:
                image = x['Memory Image']
                stim_type = 'MEMORY IMAGE'
            
            return get_pres_time(image, stim_type, log)
        
        result = []
        runs = np.unique(subj_df['Run'])
        for i in runs:
            log = pd.read_csv(os.path.join(datadir, subj_df['Subject'].values[0], f'-{i}.log'), delimiter='\t', header=None, names=['Time', 'Event', 'Info'])
            start_time = float(log[log['Info'].apply(lambda x: 'current time: ' in x if type(x) is str else False)]['Info'].values[0].split()[-1])
            
            x = subj_df.query('Run == @i').copy()
            next_times = x.apply(lambda y: timing_helper(y, log), axis=1)

            x['Stimulus Onset'] = [float(t[0]) + start_time for t in next_times]
            x['Stimulus Offset'] = [float(t[1]) + start_time for t in next_times]

            result.append(x.drop('Stimulus End', axis=1))
        return pd.concat(result, ignore_index=True)

    def helper(subjdir):
        subj = os.path.basename(subjdir)

        pres_fnames = lsdir(os.path.join(subjdir, 'pres*.csv'))
        mem_fnames = lsdir(os.path.join(subjdir, 'mem*.csv'))

        pres = pd.concat([pd.read_csv(fname) for fname in pres_fnames], ignore_index=True)
        mem = pd.concat([pd.read_csv(fname) for fname in mem_fnames], ignore_index=True)
        
        df = pd.concat([pres, mem], ignore_index=True).sort_values(['Run']).drop('Unnamed: 0', axis=1)
        df['Subject'] = subj
        df = add_timing_info(df)
        return df

    subjdirs = lsdir(os.path.join(datadir, '*_20??_*_*'))
    data = []
    for subjdir in tqdm(subjdirs):
        data.append(helper(subjdir))

    drop = ['Attention Response Time (s)', 'Attention Level', 'Post Invalid Cue', 'Pre Invalid Cue', 'Attention Button', 'Rating History', 'Category', 'Attention Probe', 'Cue Validity']
    return pd.concat(data, ignore_index=True).drop(drop, axis=1).rename({'Cued Side': 'Cued Location'}, axis=1)


def parse_gaze_data(datadir):
    def multi_get(d, keys):
        if type(d) is list:
            x = [multi_get(i, keys) for i in d]
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')  # ignore typecast deprecation warning
                return pd.DataFrame.from_dict(x)

        if type(keys) is dict:
            return {k: multi_get(d, v) for k, v in keys.items()}

        vals = []
        for k in keys:
            if type(k) is list:
                vals.append(multi_get(d, k))
            elif k in d:
                d = d[k]
            else:
                return np.nan
        if len(vals) == 0:
            return d
        else:
            try:
                if len(vals) == 0 or np.isnan(vals).all():
                    return np.nan
                return np.nanmean(vals)
            except:
                return vals
    
    gaze_dict = {'Time': ['values', 'frame', 'timestamp'],
             'x': ['values', 'frame', 'avg', 'x'],
             'y': ['values', 'frame', 'avg', 'y'],
            'Pupil size': [['values', 'frame', 'lefteye', 'psize'], ['values', 'frame', 'righteye', 'psize']]}

    str2unix = lambda t: time.mktime(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timetuple()) if type(t) is str else -1
    
    def helper(subjdir):
        subj = os.path.basename(subjdir)

        gaze_data_files = lsdir(os.path.join(subjdir, 'eye_data', '*_*'))
        gaze_data = []
        for g in gaze_data_files:
            with open(g, 'r') as f:
                content = f.readlines()
                
                data = []
                for line in content:
                    try:
                        data.append(json.loads(line))
                    except:
                        pass # ignore lines that can't be parsed as json
            
            df = multi_get(data, gaze_dict)
            df['Subject'] = subj
            df['Run'] = int(os.path.basename(g).split('_')[1])

            # convert x and y values to cm
            if df.shape[0] > 0:
                df['x'] = df['x'] * (59.8 / 2048)
                df['y'] = df['y'] * (33.6 / 1152)            

                # drop missing or invalid data (pupil size <= 0, x or y off screen)
                gaze_data.append(df.query('`Pupil size` > 0 & x > 0 & y > 0 & x < 59.8 & y < 33.6').dropna(how='all', axis=0))

        # drop missing or invalid data (pupil size <= 0, x or y <= 0)
        df = pd.concat(gaze_data, axis=0, ignore_index=True).dropna(how='all', axis=0)

        try:
            df['Time'] = df['Time'].apply(str2unix)
        except:
            pass
        return df

    subjdirs = lsdir(os.path.join(datadir, '*_20??_*_*'))
    data = []
    for subjdir in tqdm(subjdirs):
        data.append(helper(subjdir))
    return pd.concat(data, ignore_index=True)


# kz edited one line of code in this function
def intersect_image(xs, ys):
    #im_len = 6.7 * (52.96 / 59.8)
    im_len = 6.7 * (59.8 / 52.96) +2
    
    # ^ I think this conversion factor should be flipped? 
    # 52.96 / 59.8  -->  59.8 / 52.96
    
    # here is the way I see it:
    
    # image_length_in_cm  = 6.7 DVA  *  ( 59.8 cm / 52.96 DVA )
    # the DVA on the top and bottom cancel out, leaving just cm
    
    # NOTE: I also add an additional 2 centimeters 
    # BECAUSE: I want to detect any gazepoints within a bounding box of 1cm around the image 
    # thus, I add two centimeters, one for each side 
    # (e.g. the horizontal length is the original length plus 1 cm on the left and 1 cm on the right)
    # also see visualization in jupyter notebook
    
    y = (33.6 - im_len) / 2
    
#     x1 = (59.8 / 2) - 4.5 - im_len
#     x2 = (59.8 / 2) + 4.5
    
    # kz replaced with these lines (edits #2, #3)
    x1 = (59.8 / 2) - 3.5 - im_len
    x2 = (59.8 / 2) + 3.5
    
    # ^ in these lines, I now subtract 3.5 as opposed to 4.5
    # since we are adding a 1cm bounding box around the image, the edge is now 1 cm closer to center
    # thus the nearest edge we want to detect is 3.5 as opposed to 4.5 centimeters away

    xs = np.array(xs)
    ys = np.array(ys)

    return ((xs > x1) & (xs < x1 + im_len) & (ys > y) & (ys < y + im_len)).any(), ((xs > x2) & (xs < x2 + im_len) & (ys > y) & (ys < y + im_len)).any()


# kz added six lines of code to this function
def add_intersection(behavioral, gaze):
    subjs = behavioral['Subject'].unique()
    for subj in tqdm(subjs):
        stimuli = behavioral.query('Subject == @subj and `Trial Type` == "Presentation"')
        for i, stim in stimuli.iterrows():
            start = stim['Stimulus Onset']
            end = stim['Stimulus Offset']
            gz = gaze.query('Subject == @subj and Time >= @start and Time <= @end')
            if gz.shape[0] > 0:
                behavioral.loc[i, 'Left intersection'], behavioral.loc[i, 'Right intersection']  = intersect_image(gz['x'], gz['y'])
                behavioral.loc[i, 'Intersection detected'] = behavioral.loc[i, 'Left intersection'] or behavioral.loc[i, 'Right intersection']
                behavioral.loc[i, 'Attended intersection'] = (behavioral.loc[i, 'Left intersection'] and behavioral.loc[i, 'Cued Location'] == '<') or (behavioral.loc[i, 'Right intersection'] and behavioral.loc[i, 'Cued Location'] == '>')
    
            # kz added the six lines below: store number of gaze datapoints in this trial to dataframe before returning 
            behavioral.loc[i, 'gaze_datapoints']  = gz.shape[0]
            behavioral.loc[i, 'unique_gaze_datapoints']  = gz.drop_duplicates().shape[0]
            
            gz_dropped = gz.drop_duplicates()
            
            behavioral.loc[i, 'first_second'] = gz_dropped[(gz_dropped['Time']>= start) & (gz_dropped['Time']< start+1)].shape[0]
            behavioral.loc[i, 'second_second'] = gz_dropped[(gz_dropped['Time']>= start+1) & (gz_dropped['Time']< start+2)].shape[0]
            behavioral.loc[i, 'third_second'] = gz_dropped[(gz_dropped['Time']>= start+2) & (gz_dropped['Time']<= end)].shape[0]
            
    
    return behavioral


def add_order_column(df):
    df['Order'] = df['Stimulus Onset'].argsort()
    return df


def image_finder(image, stimuli):
    kind = 'Place' if image[:3] == 'sun' else 'Face'
    cues = {k: stimuli[k].apply(lambda x: image in x if type(x) is str else False) for k in ['Cued Face', 'Cued Place', 'Uncued Face', 'Uncued Place']}
    matches = np.sum([v.values for v in cues.values()], axis=0).astype(bool)
    
    if len(matches) > 0 and np.any(matches):
        side = 'Left' if stimuli.loc[matches]['Cued Location'].values[0] == '<' else 'Right'
        category = stimuli.loc[matches]['Cued Category'].values[0]
    else:
        side = None
        category = None
    
    return kind, cues, matches, side, category


def add_behavioral_labels(df):
    subjs = df['Subject'].unique()
    labled_stimuli = pd.DataFrame(index=df.index, columns=['Attended', 'Attended category', 'Attended location', 'Unattended'], dtype=float)

    for subj in tqdm(subjs):
        stimuli = df.query('Subject == @subj and `Trial Type` == "Presentation"')
        probes = df.query('Subject == @subj and `Trial Type` == "Memory"')

        for i, probe in probes.iterrows():
            kind, cues, match, side, category = image_finder(probe['Memory Image'], stimuli)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                df.loc[i, 'Category'] = kind
                df.loc[i, 'Cued Location'] = side
                df.loc[i, 'Cued Category'] = category

                if side is None:
                    df.loc[i, 'Attention'] = 'Novel'
                elif np.any(cues['Cued Place']):
                    if category == 'Place':
                        df.loc[i, 'Attention'] = 'Attended'
                    else:
                        df.loc[i, 'Attention'] = 'Attended location'
                elif np.any(cues['Uncued Place']):
                    if category == 'Place':
                        df.loc[i, 'Attention'] = 'Attended category'
                    else:
                        df.loc[i, 'Attention'] = 'Unattended'
                elif np.any(cues['Cued Face']):
                    if category == 'Face':
                        df.loc[i, 'Attention'] = 'Attended'
                    else:
                        df.loc[i, 'Attention'] = 'Attended location'
                elif np.any(cues['Uncued Face']):
                    if category == 'Face':
                        df.loc[i, 'Attention'] = 'Attended category'
                    else:
                        df.loc[i, 'Attention'] = 'Unattended'
                else:
                    df.loc[i, 'Attention'] = 'Novel'
                
                # fill in familiarity rating if there's a match
                if np.any(match):
                    idx = np.where(match)[0][0]
                    labled_stimuli.loc[stimuli.index[idx], df.loc[i, 'Attention']] = probe['Familiarity Rating']

    return pd.concat([df, labled_stimuli], axis=1)


def count_same_cues(current, all):
    previous = all.query('Subject == @current.Subject and `Trial Type` == "Presentation" and ((Run == @current.Run and Order <= @current.Order) or Run < @current.Run)').sort_values(by=['Run', 'Order'], ascending=False)
    if len(previous) == 0:
        return np.nan, np.nan, np.nan
    else:
        same_location = 0
        same_category = 0
        same_both = 0

        mismatched_location = False
        mismatched_category = False
        mismatched_both = False

        for _, row in previous.iterrows():
            if not mismatched_location and row['Cued Location'] == current['Cued Location']:
                same_location += 1
            else:
                mismatched_location = True

            if not mismatched_category and row['Cued Category'] == current['Cued Category']:
                same_category += 1
            else:
                mismatched_category = True
            
            if not mismatched_both and (row['Cued Location'] == current['Cued Location']) and (row['Cued Category'] == current['Cued Category']):
                same_both += 1
            else:
                mismatched_both = True

            if mismatched_both and mismatched_category and mismatched_location:
                break
        
        if same_both == 0:
            pass
        return same_location, same_category, same_both


def add_cue_counts(df):
    df['Location sequence length'] = np.nan
    df['Category sequence length'] = np.nan
    df['Same cue sequence length'] = np.nan

    for i, row in tqdm(df.query('`Trial Type` == "Presentation"').iterrows()):
        df.loc[i, 'Location sequence length'] , df.loc[i, 'Category sequence length'], df.loc[i, 'Same cue sequence length'] = count_same_cues(row, df)
    
    return df


def recency(x, tau=2, eps=0.05, max_pos=9):
    if type(x) is not np.ndarray:
        x = np.array(x)

    y = 1 - np.exp(-x/tau)

    if type(y) is np.ndarray:
       y[y <= 0] = eps
    elif y <= 0:
       y = eps
    
    return y


def nearest_cues(current, all, **kwargs):
    previous = all.query('Subject == @current.Subject and `Trial Type` == "Presentation" and Run == @current.Run').sort_values(by=['Run', 'Order'], ascending=False)
    if len(previous) == 0:
        return np.nan, np.nan, np.nan

    same_category = previous['Cued Category'] == current['Category']

    nearest_match = np.where(same_category)[0]
    if len(nearest_match) == 0:
        closest = np.nan
        number_of_matches = 0
        recency_weighted_number_of_matches = 0
    else:
        closest = np.min(nearest_match) + 1
        number_of_matches = np.sum(same_category)
        recency_weighted_number_of_matches = max([min([np.sum(recency(nearest_match, **kwargs)) / sum(recency(9 - np.arange(previous.shape[0]), **kwargs)), 1]), 0])
    
    return closest, number_of_matches, recency_weighted_number_of_matches


def add_cue_recency_info(df):
    df['Distance to nearest same-category cue'] = np.nan
    df['Number of same-category cues'] = np.nan
    df['Recency-weighted number of same-category cues'] = np.nan

    for i, row in tqdm(df.query('`Trial Type` == "Memory"').iterrows()):
        df.loc[i, 'Distance to nearest same-category cue'], df.loc[i, 'Number of same-category cues'], df.loc[i, 'Recency-weighted number of same-category cues'] = nearest_cues(row, df)
    return df

# kz edited out three lines and added one line to this function
def load_data():
    download_data()
    
    sustained_behavioral = parse_behavioral_data(os.path.join(datadir, 'sustained'))
    variable_behavioral = parse_behavioral_data(os.path.join(datadir, 'variable'))

    gaze_fname = os.path.join(datadir, 'gaze_data.pkl')
    if os.path.exists(gaze_fname):
        sustained_gaze, variable_gaze = pd.read_pickle(gaze_fname)
    else:
        sustained_gaze = parse_gaze_data(os.path.join(datadir, 'sustained'))
        variable_gaze = parse_gaze_data(os.path.join(datadir, 'variable'))
        pd.to_pickle((sustained_gaze, variable_gaze), gaze_fname)
    
    sustained_behavioral = add_intersection(sustained_behavioral, sustained_gaze)
    variable_behavioral = add_intersection(variable_behavioral, variable_gaze)

    gaze_columns = ['Intersection detected', 'Attended intersection', 'Left intersection', 'Right intersection']
    sustained_behavioral[gaze_columns] = sustained_behavioral[gaze_columns].fillna(False)
    variable_behavioral[gaze_columns] = variable_behavioral[gaze_columns].fillna(False)

    # patch up variable_behavioral
    variable_behavioral['Cued Face'] = variable_behavioral['Cued Composite'].apply(lambda x: x.split('_')[0] + '.jpg' if type(x) is str else x)
    variable_behavioral['Cued Place'] = variable_behavioral['Cued Composite'].apply(lambda x: x.split('_')[1] if type(x) is str else x)
    variable_behavioral['Uncued Face'] = variable_behavioral['Uncued Composite'].apply(lambda x: x.split('_')[0] + '.jpg'  if type(x) is str else x)
    variable_behavioral['Uncued Place'] = variable_behavioral['Uncued Composite'].apply(lambda x: x.split('_')[1] if type(x) is str else x)

    with warnings.catch_warnings():  # ignore FutureWarning about adding keys
        warnings.simplefilter("ignore")
        sustained_behavioral = sustained_behavioral.groupby(['Subject', 'Run', 'Trial Type']).apply(add_order_column).reset_index(drop=True)
        variable_behavioral = variable_behavioral.groupby(['Subject', 'Run', 'Trial Type']).apply(add_order_column).reset_index(drop=True)
    
    sustained_behavioral = add_behavioral_labels(sustained_behavioral)
    variable_behavioral = add_behavioral_labels(variable_behavioral)

    sustained_behavioral = add_cue_counts(sustained_behavioral)
    variable_behavioral = add_cue_counts(variable_behavioral)

    sustained_behavioral = add_cue_recency_info(sustained_behavioral)
    variable_behavioral = add_cue_recency_info(variable_behavioral)
    
    # kz added these lines
    sustained = sustained_behavioral[~sustained_behavioral['Intersection detected']]
    variable = variable_behavioral[~variable_behavioral['Intersection detected']]

    # kz commented the six lines below: let's just return the full data for now
    
    # sustained = sustained_behavioral[~sustained_behavioral['Attended intersection']]
    # variable = variable_behavioral[~variable_behavioral['Attended intersection']]

    # with warnings.catch_warnings():
       # warnings.simplefilter('ignore')
       # sustained['Category-matched recent cue'] = sustained['Distance to nearest same-category cue'] > 0
       # variable['Category-matched recent cue'] = variable['Distance to nearest same-category cue'] > 0

    # kz edited the line below : let's just return the full data for now
    
    return sustained_gaze, variable_gaze, sustained_behavioral, variable_behavioral

    #return sustained, variable, sustained_gaze, variable_gaze, sustained_behavioral, variable_behavioral


def plot_colorbar(cmap, fname=None):
    fig, ax = plt.subplots(figsize=(0.2, 2))
    norm = plt.Normalize(vmin=-1, vmax=1)
    mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='vertical')
    ax.axis('off')

    if fname is not None:
        fig.savefig(os.path.join(figdir, fname + '.pdf'), bbox_inches='tight')