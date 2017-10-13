import seaborn
import os
import pickle
import statistics



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
    pass

def plot_response(mass):
    images = mass['images']
    ratings = mass['ratings']
    cued = mass['cued']
    uncued = mass['uncued']


    cued_count = 0
    cued_actual = 0
    uncued_count = 0
    uncued_actual = 0
    unseen_count = 0
    unseen_actual = 0

    cued_rt = []
    uncued_rt = []
    unseen_rt = []

    for i in range(len(ratings)):
        image = images[i]
        rt = ratings[i][-1][1]
        score = ratings[i][-1][0]

        if image in cued:
            if score <= 2:
                cued_count += 1
            cued_actual += 1
            cued_rt.append(rt)
        elif image in uncued:
            if score <= 2:
                uncued_count += 1
            uncued_actual += 1
            uncued_rt.append(rt)
        else:
            if score >= 3:
                unseen_count +1
            unseen_actual += 1
            unseen_rt.append(rt)

    cued_acc = cued_count / float(cued_actual)
    uncued_acc = uncued_count / float(uncued_actual)
    unseen_acc = unseen_count / float(unseen_actual)


    # graph


# main function
def graph_data(folder):
    dirs = get_subdirectories(folder)

    for dir_name in dirs:
        runs = make_run_dict(get_files(dir_name))
        mass = {'images':[], 'ratings':[], 'cued':[], 'cued_RT':[], 'uncued':[], 'uncued_RT':[]}
        
        # change outliers

        for run in runs:
            aggregate(run, runs, mass)

        is_outlier(mass, runs)
        print(mass)
        #plot_rl(mass)
        #plot_response(mass)
                
        
graph_data('../data')
        
    

