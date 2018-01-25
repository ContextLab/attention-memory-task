import seaborn
import os
import pickle
import statistics
import pandas as pd



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
        
    fp2.close()
    
def plot_rl(mass):
    df = pd.DataFrame.from_dict(mass, orient='index')
    df = df.T
    df_new = df.replace('None', 'Nan')
    
    return(df_new)

def plot_response(mass, category=False):
    images = mass['images']
    ratings = mass['ratings']
    cued = mass['cued']
    uncued = mass['uncued']


    cued_count = 0
    cued_actual = 0
    
    cued_count_face = 0
    cued_actual_face = 0
    
    cued_count_house = 0
    cued_actual_house = 0
    
    uncued_count = 0
    uncued_actual = 0
    
    uncued_count_face = 0
    uncued_actual_face = 0
    
    uncued_count_house = 0
    uncued_actual_house = 0
    
    unseen_count_face = 0
    unseen_actual_face = 0
    
    unseen_count_house = 0
    unseen_actual_house = 0

    cued_rt = []
    uncued_rt = []
    unseen_rt_face = []
    unseen_rt_house = []
    uncued_rt_face = []
    uncued_rt_house = []    
    cued_rt_face = []
    cued_rt_house = []

    for i in range(len(ratings)):
        image = images[i]
        rt = ratings[i][-1][1]  # this gives reaction time (float)
        score = ratings[i][-1][0]    # this gives rating (int)

        if image in cued:
            if "CFD" in image:
                if (score==2 or score==1) :
                    cued_count_face += 1
                if (score==1 or score==2 or score==3 or score==4):
                    cued_actual_face += 1
                    cued_rt_face.append(rt)
            else:
                if (score==2 or score==1) :
                    cued_count_house += 1
                if (score==1 or score==2 or score==3 or score==4):
                    cued_actual_house += 1
                    cued_rt_house.append(rt)
            
        elif image in uncued:
            if "CFD" in image:
                if (score==2 or score==1) :
                    uncued_count_face += 1
                if (score==1 or score==2 or score==3 or score==4):
                    uncued_actual_face += 1 
                    uncued_rt_face.append(rt)
            else:
                if (score==2 or score==1) :
                    uncued_count_house += 1
                if (score==1 or score==2 or score==3 or score==4):
                    uncued_actual_house += 1
                    uncued_rt_house.append(rt)
        else:
            if "CFD" in image:
                if (score==2 or score==1) :
                    unseen_count_face += 1
                if (score==1 or score==2 or score==3 or score==4):
                    unseen_actual_face += 1 
                    unseen_rt_face.append(rt)
            else:
                if (score==2 or score==1) :
                    unseen_count_house += 1
                if (score==1 or score==2 or score==3 or score==4):
                    unseen_actual_house += 1
                    unseen_rt_house.append(rt)
#             if (score==1 or score==2):
#                 unseen_count= +1
#             #unseen_count += 1
#             unseen_actual += 1
#             unseen_rt.append(rt)
    if category==True:
        #PLOT HOUSES AND FACES SEPARATELY
    
        cued_acc_house = cued_count_house / float(cued_actual_house)
        cued_acc_face = cued_count_face / float(cued_actual_face)
        uncued_acc_face = uncued_count_face / float(uncued_actual_face)
        uncued_acc_house = uncued_count_house / float(uncued_actual_house)
        
        unseen_inacc_house = unseen_count_house / float(unseen_actual_house)
        unseen_inacc_face = unseen_count_face / float(unseen_actual_face)
        
    
        mydict = {'uncued_F':[uncued_acc_face], 'uncued_H':[uncued_acc_house], 'cued_H':[cued_acc_house], 'cued_F': [cued_acc_face], 'novel_H':[unseen_inacc_house], 'novel_F':[unseen_inacc_face]}
        to_plot = pd.DataFrame(mydict)
    
        #sns.barplot(data=[[uncued_acc_face], [uncued_acc_house], [cued_acc_face], [cued_acc_house]])
        #sns.barplot(data=to_plot)
    
    # graph
    
    else:
        #PLOT ALL TOGETHER
        cued_acc = (cued_count_house + cued_count_face)/(cued_actual_house + cued_actual_face)
        uncued_acc = (uncued_count_face+uncued_count_house) / float(uncued_actual_face+uncued_actual_house)
        unseen_acc = (unseen_count_house+unseen_count_face) / float(unseen_actual_house+unseen_actual_face)
        
        mydict = {'uncued':[uncued_acc], 'cued_acc':[cued_acc], 'unseen_acc': [unseen_acc]}
        to_plot = pd.DataFrame(mydict)
    
        #sns.barplot(data=to_plot)
        
    return(to_plot)



    # graph


def calc_roc(mass):
    targets = {}
    lures = {}
    for i in range(len(mass['images'])):
        image =  mass['images'][i]
        if image in mass['cued'] or image in mass['uncued']:
            if mass['ratings'][i][-1][0]:
                targets[image] = mass['ratings'][i][-1][0]
        else:
            if mass['ratings'][i][-1][0]:
                lures[image] = mass['ratings'][i][-1][0]
    t_count = len(targets)
    l_count = len(lures)

    t_one = 0
    t_two = 0
    t_three = 0
    t_four = 0
    for key in targets:
        if targets[key]:
            score = int(targets[key])
            if score == 1:
                t_one += 1
            if score <= 2:
                t_two += 1
            if score <= 3:
                t_three += 1
            if score <= 4:
                t_four += 1

    l_one = 0
    l_two = 0
    l_three = 0
    l_four = 0
    for key in lures:
        if lures[key]:
            score = int(lures[key])
            if score == 1:
                l_one += 1
            if score <= 2:
                l_two += 1
            if score <= 3:
                l_three += 1
            if score <= 4:
                l_four += 1

    points = []
    points.append((0, 0))
    points.append((t_one / float(t_count), l_one / float(l_count)))
    points.append((t_two / float(t_count), l_two / float(l_count)))
    points.append((t_three / float(t_count), l_three / float(l_count)))
    points.append((t_four / float(t_count), l_four / float(l_count)))

    print(points)


# main function
def graph_data(folder):
    dirs = get_subdirectories(folder)

    for dir_name in dirs:
        runs = make_run_dict(get_files(dir_name))
        mass = {'images':[], 'ratings':[], 'cued':[], 'cued_RT':[], 'uncued':[], 'uncued_RT':[]}
        
        # change outliers

        for run in runs:
            aggregate(run, runs, mass)

        #is_outlier(mass, runs)

        calc_roc(mass)

        #plot_rl(mass)
        #plot_response(mass)


def mass_data(folder):
    mass_list = []
    dirs = get_subdirectories(folder)

    for dir_name in dirs:
        runs = make_run_dict(get_files(dir_name))
        mass = {'images':[], 'ratings':[], 'cued':[], 'cued_RT':[], 'uncued':[], 'uncued_RT':[]}

        for run in runs:
            aggregate(run, runs, mass)
            
           
        mass_list.append(mass)   

    return(mass_list)
                
        
#graph_data('../data')
        
    

