This directory contains the full experiment code and data from the Sustained Attention Experiment. 

<h3>Experiment Code</h3>
The main experiment code is written in `attention_memory_experiment.py` and the functions the experiment calls on (to do things like display images and record responses) are written in `experiment_helpers.py`. A full description of the experimental paradigm can be found in [our manuscript](https://psyarxiv.com/2ps6e), beginning with a description of the pre-task instructions and practice rounds on page 4. <br />

To run the experiment, you will first want to unzip `../stim.zip` so that you can access the image stimuli for the experiment. Then, you should open `attention_memory.py` in Psychopy, make sure `Practice` is set to `True`, if you would like the participant to see the instructions and complete practice runs, and hit the green run button in the psychopy window. For the first run, you may enter whatever participant number you like, but should enter run# 0. For the subsequent runs of the same participant, you should enter the same participant number, but increase the run number by one.<br />

<h3>Data</h3>
When you run the experiment, the code will create a directory in the `data` directory with the participant number and the year, month, and day on which the participant is being tested in the directory name (`##_YYYY_MMM_DD`). The participant's data from the experiment will automatically save out into this directory as they complete the task. <br />

By the end of the experiment, the participant will have three main file types in their directory: two pickle (`.pkl`) files containing the pre and post questionnaire data, respectively; csv files containing all of the information from the presentation trials the participant has completed (`pres#.csv`); csv files containing information from the memory trials the participant has completed (`mem#.csv`); an `initial_df.csv` file containing every stimulus that the participant saw over the course of the experiment, (in temporal order), and `buttons_full.csv` which contains every key press response made by the participant at any time during the experiment.
