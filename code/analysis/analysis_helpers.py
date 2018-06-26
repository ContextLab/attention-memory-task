import seaborn
import os
import pickle
#import statistics
import pandas as pd
import numpy as np


# SINGLE SUBJECT ANALYSIS
# pseudo code

# in: main directory name (../data)
# out: list of subdirectories
def get_subdirectories(a_dir):
    return [a_dir + '/' + name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

# in: directory name
# out: list of .pkl files within directory
def get_files(dir_name):
    files = [dir_name + '/' + f for f in os.listdir(dir_name) if f.endswith('.pkl')]
    return files

def rand_split(subject):
    a = [x for x in subject['images'] if x[0:3]!='sun']
    b = [x for x in subject['images'] if x[0:3]=='sun']
    return({'place_rands':b, 'face_rands':a})

# in: list of .pkl files within directory
# out: dict that maps mem_items.pkl to corresponding previous_items.pkl
def make_run_dict(files):
    runs = {}

    for f in files:
        if f.endswith('mem_items.pkl'):
            runs[f] = f[0:-13] + 'previous_items.pkl'

    return runs

# in: run is the name of mem_items.pkl, runs[run] is the name of corresponding previous_items.pkl
#     mass is the aggregate data
# out: none, prints if outlier
def is_outlier(mass, runs):

    cued_avg = sum(mass['cued_RT']) / len(mass['cued_RT'])
    uncued_avg = sum(mass['uncued_RT']) / len(mass['uncued_RT'])
    cued_sd = 3 * statistics.stdev(mass['cued_RT'])
    uncued_sd = 3 * statistics.stdev(mass['uncued_RT'])

    for run in runs:
        with open(run, 'rb') as fp:
            prev = pickle.load(fp)
            print(prev)
            cued = sum(prev['cued_RT']) / len(prev['cued_RT'])
            uncued = sum(prev['uncued_RT']) / len(prev['uncued_RT'])
            if cued > cued_avg + cued_sd or cued < cued_avg - cued_sd or uncued > uncued_avg + uncued_sd or uncued < uncued_avg - uncued_sd:
                print("Outlier in " + runs[run])

        fp.close()


# in: dict of runs mem_items: previous_items
# out: none, modifies mass dictionary
def aggregate(run, runs, mass):
    with open(run, 'rb') as fp1:
        mem = pickle.load(fp1)

        mass['images'].extend(mem['images'])
        mass['ratings'].extend(mem['ratings'])

    fp1.close()

    with open(runs[run], 'rb') as fp2:
        prev = pickle.load(fp2)

        mass['cued'].extend(prev['cued'])
        mass['cued_RT'].extend(prev['cued_RT'])
        mass['uncued'].extend(prev['uncued'])
        mass['uncued_RT'].extend(prev['uncued_RT'])
        mass['cue_tuples'].extend(prev['cue_tuples'])

    fp2.close()

def plot_rl(mass):
    df = pd.DataFrame.from_dict(mass, orient='index')
    df = df.T
    df_new = df.replace('None', 'Nan')

    return(df_new)

def idx_substring(the_list, substring, loud=False):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
        else:
            return None

def flatten(the_list):
    return([val for sublist in the_list for val in sublist])

def mass_data(folder, sub_dir=None):
    mass_list = []

    if sub_dir==None:
        dirs = get_subdirectories(folder)
    else:
        dirs = sub_dir

    for dir_name in dirs:
        runs = make_run_dict(get_files(dir_name))
        mass = {'images':[], 'ratings':[], 'cued':[], 'cued_RT':[], 'uncued':[], 'uncued_RT':[], 'cue_tuples':[]}

        for run in runs:
            aggregate(run, runs, mass)

        mass_list.append(mass)

    return(mass_list)


def rating_pull(tuple_rating_list):
    '''
    pulls subject's rating out of rating tuple
    '''
    if len(tuple_rating_list)>1:
        return(tuple_rating_list)[1][0]
    else:
        return(tuple_rating_list)[0][0]

def cat_check(row):
    if row['cat'] == row['cued_cat'] :
        return('attended')
    elif row['cued_cat'] == 'novel':
        return('novel')
    else:
        return('unattended')

def cat_loc_check(row):
    if row['location'] == 'attended':
        if row['category']=='attended' :
            return('both')
        if row['category']=='unattended':
            return('side')

    if row['location'] == 'unattended':
        if row['category']=='attended' :
            return('category')
        if row['category']=='unattended':
            return('none')

    if row['location'] == 'novel':
        return('novel')

def rep_seen(row):
    if row['familiarity'] in [1.0,2.0]:
        return('no')
    else:
        return('yes')


# Prep ROC data
def ROC_data(rec, category = False):

    labels_a = ['both','none','novel','side','category']

    if category==True:
        ROC = {}

        for x in ['Face','Location']:

            labels = [x+'_'+a for a in labels_a]

            for typ,attn in zip(labels,labels_a):
                ROC[typ] = [0]

                for x in [1.0, 2.0, 3.0, 4.0]:

                    num_cases = rec.loc[(rec['familiarity'] <=x) & rec['attention level'].isin([attn]) & rec['cat'].isin([typ[0]])].shape[0]

                    if num_cases>0:
                        ROC[typ].append(num_cases/float(rec.loc[rec['attention level'].isin([attn]) & rec['cat'].isin([typ[0]])].shape[0]))

                    else:
                        ROC[typ].append(0)

                ROC[typ].append(1)


    else:
        ROC = {'both':[0],'none':[0], 'novel':[0],'side':[0],'category':[0]}

        for typ in labels_a:
            nums = []

            for x in [1.0, 2.0, 3.0, 4.0]:

                num_cases = rec.loc[(rec['familiarity'] <=x) & rec['attention level'].isin([typ])].shape[0]
                #print(num_cases)

                if num_cases>0:
                    ROC[typ].append(num_cases/float(rec.loc[rec['attention level'].isin([typ])].shape[0]))

                else:
                    ROC[typ].append(0)

            ROC[typ].append(1)

    return(ROC)

def arrange_RTs(pres,sub_data):
    df_pres1 = pres[pres['is_cued_RT']==1]
    df_pres2 = pres[pres['is_cued_RT']==2]

    cued_RT = [y['cued_RT'] for y in sub_data]
    cued_RT = [val for sublist in cued_RT for val in sublist]


    uncued_RT = [y['uncued_RT'] for y in sub_data]
    uncued_RT = [val for sublist in uncued_RT for val in sublist]


    ser1 = pd.Series(cued_RT, index=df_pres1.index)
    ser2 = pd.Series(uncued_RT, index=df_pres2.index)
    df_pres1['RT'] = ser1
    df_pres2['RT'] = ser2

    prezzies=[df_pres1,df_pres2]
    pres=pd.concat(prezzies).reset_index(drop=True)
    return(pres)



def pr(row):

    if row['cue_tuples'][0]=='cue_R' and row['cue_tuples'][2]==0:
        return(1)

    elif row['cue_tuples'][0]=='cue_R' and row['cue_tuples'][2]==1:
        return(2)

    elif row['cue_tuples'][0]=='cue_L':
        return(2)

    else:
        return(0)

def is_valid(row):

    if row['cue_tuples'][2]==0:
        return('valid')
    else:
        return('invalid')


def mass_df(mass, typ = 'pres'):
    full_rec = []
    full_pres = []

    for s in mass:

        cue_tup = []
        cue_side = []
        cat = []

        cue_count = 0
        uncue_count = 0

        rec = pd.DataFrame({'images':s['images'],'familiarity':[rating_pull(x) for x in s['ratings']]})
        pres = pd.DataFrame({'cued':s['cued'],'uncued':s['uncued'],'cue_tuples':s['cue_tuples']})

        for im in rec['images']:

            if len(pres[pres['cued'].str.contains(im[:-4])])>0:

                obj = pres[pres['cued'].str.contains(im[:-4])]['cue_tuples']
                cue_tup.append(obj[obj.index[0]][1])
                cue_side.append('attended')
                cue_count +=1

            elif len(pres[pres['uncued'].str.contains(im[:-4])])>0:
                obj = pres[pres['uncued'].str.contains(im[:-4])]['cue_tuples']
                cue_tup.append(obj[obj.index[0]][1])
                cue_side.append('unattended')
                uncue_count +=1

            else:
                cue_tup.append('novel')
                cue_side.append('novel')

            if im.startswith('00'):
                cat.append('F')

            else:
                cat.append('L')

        rec['cued_cat']= cue_tup
        rec['location'] = cue_side
        rec['cat'] = cat
        rec['category'] = rec.apply(lambda row: cat_check(row),axis=1)
        rec['attention level'] = rec.apply(lambda row: cat_loc_check(row),axis=1)
        rec['report familiar'] = rec.apply(lambda row: rep_seen(row),axis=1)


        full_rec.append(rec)
        full_pres.append(pres)


    rec = pd.concat(full_rec).reset_index(drop=True)
    pres = pd.concat(full_pres).reset_index(drop=True)

    if typ == 'pres':
        return(pres)
    else:
        return(rec)

# def idx_substring(the_list, substring, loud=False):
#     for i, s in enumerate(the_list):
#         if substring in s:
#             return i
#         else:
#             return('no')

def img_split(image_list, cat = False):
    '''
    splits overlay image filenames into filenames of the original, single images

    input : list of image filenames
    output : list of image filenames OR two lists, separated by category

    '''

    split = [words for segments in image_list for words in segments.split('_')]
    a = [word+'.jpg' for word in split if word[-3:]!='jpg']
    b = [word for word in split if word[-3:]=='jpg']
    glom = a+b

    if cat == False:
        return(glom)

    else:
        return({'face_im':a, 'place_im':b})

def halfsies(mass):
    '''
    selects subs who have seen equal proportion of cued and uncued in memory trials
    '''
    halfsies = []
    for s in mass:

        cued_split = img_split(s['cued'])
        uncued_split = img_split(s['uncued'])

        u1 = set(s['images']).intersection(set(cued_split))
        u2 = set(s['images']).intersection(set(uncued_split))

        conglom = cued_split+uncued_split

        k = s['images']
        u3 = [x for x in k if x not in conglom]
        u4 = [x for x in k if x in conglom]


        for index,img in enumerate(s['images']):
            one = [words for segments in s['cued'] for words in segments.split('_')]


        if len(u1)+len(u2) == len(u3):
            halfsies.append(s)
    return(halfsies)

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

def reject_outliers(data, m=2):
    '''
    rejects stat reject_outliers
    '''
    return data[abs(data - np.mean(data)) < m * np.std(data)]



## GRAVEYARD ##

#graph_data('../data')

# def plot_response(mass, category=False):
#     images = mass['images']
#     ratings = mass['ratings']
#     cued = mass['cued']
#     uncued = mass['uncued']
#
#
#     cued_count = 0
#     cued_actual = 0
#
#     cued_count_face = 0
#     cued_actual_face = 0
#
#     cued_count_house = 0
#     cued_actual_house = 0
#
#     uncued_count = 0
#     uncued_actual = 0
#
#     uncued_count_face = 0
#     uncued_actual_face = 0
#
#     uncued_count_house = 0
#     uncued_actual_house = 0
#
#     unseen_count_face = 0
#     unseen_actual_face = 0
#
#     unseen_count_house = 0
#     unseen_actual_house = 0
#
#     cued_rt = []
#     uncued_rt = []
#     unseen_rt_face = []
#     unseen_rt_house = []
#     uncued_rt_face = []
#     uncued_rt_house = []
#     cued_rt_face = []
#     cued_rt_house = []
#
#     for i in range(len(ratings)):
#         image = images[i]
#         rt = ratings[i][-1][1]  # this gives reaction time (float)
#         score = ratings[i][-1][0]    # this gives rating (int)
#
#         if image in cued:
#             if "CFD" in image:
#                 if (score==2 or score==1) :
#                     cued_count_face += 1
#                 if (score==1 or score==2 or score==3 or score==4):
#                     cued_actual_face += 1
#                     cued_rt_face.append(rt)
#             else:
#                 if (score==2 or score==1) :
#                     cued_count_house += 1
#                 if (score==1 or score==2 or score==3 or score==4):
#                     cued_actual_house += 1
#                     cued_rt_house.append(rt)
#
#         elif image in uncued:
#             if "CFD" in image:
#                 if (score==2 or score==1) :
#                     uncued_count_face += 1
#                 if (score==1 or score==2 or score==3 or score==4):
#                     uncued_actual_face += 1
#                     uncued_rt_face.append(rt)
#             else:
#                 if (score==2 or score==1) :
#                     uncued_count_house += 1
#                 if (score==1 or score==2 or score==3 or score==4):
#                     uncued_actual_house += 1
#                     uncued_rt_house.append(rt)
#         else:
#             if "CFD" in image:
#                 if (score==2 or score==1) :
#                     unseen_count_face += 1
#                 if (score==1 or score==2 or score==3 or score==4):
#                     unseen_actual_face += 1
#                     unseen_rt_face.append(rt)
#             else:
#                 if (score==2 or score==1) :
#                     unseen_count_house += 1
#                 if (score==1 or score==2 or score==3 or score==4):
#                     unseen_actual_house += 1
#                     unseen_rt_house.append(rt)
# #             if (score==1 or score==2):
# #                 unseen_count= +1
# #             #unseen_count += 1
# #             unseen_actual += 1
# #             unseen_rt.append(rt)
#     if category==True:
#         #PLOT HOUSES AND FACES SEPARATELY
#
#         cued_acc_house = cued_count_house / float(cued_actual_house)
#         cued_acc_face = cued_count_face / float(cued_actual_face)
#         uncued_acc_face = uncued_count_face / float(uncued_actual_face)
#         uncued_acc_house = uncued_count_house / float(uncued_actual_house)
#
#         unseen_inacc_house = unseen_count_house / float(unseen_actual_house)
#         unseen_inacc_face = unseen_count_face / float(unseen_actual_face)
#
#
#         mydict = {'uncued_F':[uncued_acc_face], 'uncued_H':[uncued_acc_house], 'cued_H':[cued_acc_house], 'cued_F': [cued_acc_face], 'novel_H':[unseen_inacc_house], 'novel_F':[unseen_inacc_face]}
#         to_plot = pd.DataFrame(mydict)
#
#         #sns.barplot(data=[[uncued_acc_face], [uncued_acc_house], [cued_acc_face], [cued_acc_house]])
#         #sns.barplot(data=to_plot)
#
#     # graph
#
#     else:
#         #PLOT ALL TOGETHER
#         cued_acc = (cued_count_house + cued_count_face)/(cued_actual_house + cued_actual_face)
#         uncued_acc = (uncued_count_face+uncued_count_house) / float(uncued_actual_face+uncued_actual_house)
#         unseen_acc = (unseen_count_house+unseen_count_face) / float(unseen_actual_house+unseen_actual_face)
#
#         mydict = {'uncued':[uncued_acc], 'cued_acc':[cued_acc], 'unseen_acc': [unseen_acc]}
#         to_plot = pd.DataFrame(mydict)
#
#         #sns.barplot(data=to_plot)
#
#     return(to_plot)
#
#
#
#     # graph
#
#
# def calc_roc(mass):
#     targets = {}
#     lures = {}
#     for i in range(len(mass['images'])):
#         image =  mass['images'][i]
#         if image in mass['cued'] or image in mass['uncued']:
#             if mass['ratings'][i][-1][0]:
#                 targets[image] = mass['ratings'][i][-1][0]
#         else:
#             if mass['ratings'][i][-1][0]:
#                 lures[image] = mass['ratings'][i][-1][0]
#     t_count = len(targets)
#     l_count = len(lures)
#
#     t_one = 0
#     t_two = 0
#     t_three = 0
#     t_four = 0
#     for key in targets:
#         if targets[key]:
#             score = int(targets[key])
#             if score == 1:
#                 t_one += 1
#             if score <= 2:
#                 t_two += 1
#             if score <= 3:
#                 t_three += 1
#             if score <= 4:
#                 t_four += 1
#
#     l_one = 0
#     l_two = 0
#     l_three = 0
#     l_four = 0
#     for key in lures:
#         if lures[key]:
#             score = int(lures[key])
#             if score == 1:
#                 l_one += 1
#             if score <= 2:
#                 l_two += 1
#             if score <= 3:
#                 l_three += 1
#             if score <= 4:
#                 l_four += 1
#
#     points = []
#     points.append((0, 0))
#     points.append((t_one / float(t_count), l_one / float(l_count)))
#     points.append((t_two / float(t_count), l_two / float(l_count)))
#     points.append((t_three / float(t_count), l_three / float(l_count)))
#     points.append((t_four / float(t_count), l_four / float(l_count)))
#
#     print(points)
#
#
# # main function
# def graph_data(folder):
#     dirs = get_subdirectories(folder)
#
#     for dir_name in dirs:
#         runs = make_run_dict(get_files(dir_name))
#         mass = {'images':[], 'ratings':[], 'cued':[], 'cued_RT':[], 'uncued':[], 'uncued_RT':[]}
#
#         # change outliers
#
#         for run in runs:
#             aggregate(run, runs, mass)
#
#
#         calc_roc(mass)
#
#
#
