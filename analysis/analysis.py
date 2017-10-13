import seaborn
import os
import pickle


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
# out: boolean
def is_outlier(run, runs):
    pass 

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

def plot_accuracy(mass):
    pass

def plot_memtime(mass):
    pass

# main function
def graph_data(folder):
    dirs = get_subdirectories(folder)

    for dir_name in dirs:
        runs = make_run_dict(get_files(dir_name))
        mass = {'images':[], 'ratings':[], 'cued':[], 'cued_RT':[], 'uncued':[], 'uncued_RT':[]}
        
        # change outliers

        for run in runs:
            if is_outlier(run, runs):
                print("Outlier: " + run)
                runs.pop(run)
            else:
                aggregate(run, runs, mass)
        print(mass)
        #plot_rl(mass)
        #plot_accuracy(mass)
        #plot_memtime(mass)
                
        
graph_data('../data')
        
    

