<h3>Behavioral Data</h3>

To start exploring the behavioral data, we first ran the code in the `file_check.ipynb` notebook. This code checks the number of participants and the data files that exist for each participant. 

Then, we ran the code in the `compile_behavioral_data` notebook. This code organizes and compiles the raw data from all of the participants in each experiment. It outputs one dataframe with behavioral data for all participants, one dataframe with the full gaze data for all participants, and one dataframe with the gaze data for all participants collected only during times when the presentation images were on screen (labeled by experiment and group); the dataframes are saved to the `../parsed_data` directory as csv files (`full_behavioral.csv`, `full_gaze.csv`, and `full_pres_gaze.csv`). 

Finally, we ran the code in `check_behavioral_data.ipynb` to do some checks on the compiled data before proceeding to the analysis.

Then, we ran the code in `analyze_behavioral_data` to generate statistics on participants' attention and memory performance. Running `analyze_behavioral_data_combined` analyzes the data for each experiment (generating the violin plots and timecourse plots presented in Figures 2, 4, 5, and 6 of our manuscript). Running `analyze_behavioral_data_by_group` analyzes the two participant cohorts in each experiment, separately (generating the corresponding plots shown in the Supplement to our manuscript). 

To explore the behavioral data yourself, you can follow the same steps (compiling the data, then analyzing it). Note that before starting, you will need to unzip any of the gaze files that haze been zipped to reduce file size. The files you will need to unzip are:

- `sustained_attention_experiment/data/group2/19_2019_Oct_15/eye_data/19_7.txt.zip`
- `variable_attention_experiment/data/group2/10_2019_Nov_16/eye_data/10_7.zip` 
- `variable_attention_experiment/data/group2/29_2020_Jan_13/eye_data/29_7.zip` 
- `variable_attention_experiment/data/group2/9_2019_Nov_16/eye_data/9_7.zip`

After unzipping, remove the `.zip` version of each file so only the unzipped version remains. Then, proceed to compile and analyze the data!  
