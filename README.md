# Overview

This repository contains the [Psychopy](http://psychopy.org/) code, data, and analyses for the two psychology experiments reported in [our manuscript](https://psyarxiv.com/2ps6e), <i>Feature-based and location-based volitional covert attention are mediated by different mechanisms and affect memory at different timescales.</i>

# Paradigm

There are two versions of the experiment: a block design version (Sustained Attention Experiment), and a trial-wise cuing version (Variable Attention Experiment). Both begin with an initial practice task to orient the participant to the task instructions, then a Presentation block.

In <b>Presentation blocks</b>, the subject views ten pairs of composite image stimuli (overlayed images of faces and scenes) like the one shown below, presented on the right and left of the screen. The subject is cued to attend one part of the composites presented on a particular side, while keeping their eyes fixated at center (that is, they should employ covert attention). After each image pair, a letter ('x' or 'o') appears on screen and the subject presses a button (1 or 3, respectively) to indicate which letter they see.<br />

In <b>Memory blocks</b>, the subject views 40 single, non-composite images, and rates each image as being "familiar" or "unfamiliar" on a scale of 1-4. The images shown are 50% novel images and 50% images previously seen in the most recent Presentation block (with an equal proportion of previously seen images pulled from each presentation side - R/L - and each image category - face/place).

 
 # Full Paradigm Schematic
 
<center><img style="display: inline" src="paradigm_figure/paradigm_and_key.jpg" alt="Paradigm" width="800"> </center>

# Directory Organization

The `sustained_attention_experiment` and `variable_attention_experiment` directories contain the code for running the experiments, as well as the raw participant data for each experiment (in the `code` and `data` subdirectories, respectively). This raw data is read in by code in the `data_analysis_code` directory, which organizes and compiles it, outputting the parsed data files into the `parsed_data` directory. Then, different code from the `data analysis` directory loads in the preprocessed data (from `parsed_data`) and analyzes it, generating the statistics and figures from the paper. Specifically, the statistics and figures pretaining to participants' behavioral responses (Figures 2, 4, 5, and 6) are generated in `data_analysis_code/analyze_behavioral_data.ipynb`, and the statistics and figure incorporating participants' gaze data (Figure 3) are generated in `data_analysis_code/analyze_gaze_data.ipynb`.

Lastly, the `stimulus_generation` directory contains the code to process the single images and to create the composite image stimuli that appear in the experiments, and the paradigm figure directory simply contains an image of the schematic displayed above. 

# Running the task

To run a behavioral participant, first unzip `stim.zip` so you can access all of the stimuli for the experiment. Then, simply open attention_memory.py in Psychopy (in either the `sustained_attention_experiment` or `variable_attention_experiment` directory, as desired), hit the green "run" button in the code viewer, and enter the subejct ID and run#! Make sure to set `practice = True` if you would like the participant to complete the practice trials before beginning (we strongly recommend this).

Note that the subject name or number can be arbitrarily chosen by the experimenter (any number or string), just be careful not to enter a subject number that exists in the data you've already collected.

The run number indicates which run to display next. If the subject is just beginning the experiment, the run # should be 0. A run number of 0 will initiate the experiment on the first run, and loop over presentation and memory runs until the total number of desired runs (outlined in the parameters in attention_memory.py) has been presented, pausing after each memory block for eye tracker recalibration. 

Note that at the time of data collection, our participants sat 60cm from the screen (the distance at whick the Eye Tribe eye tracker has 0.1 degrees visual angle root mean squared error) and our Psychopy monitor center was set to the original default settings (including the assumed 57cm viewing distance). Thus, to replicate the experiment exactly, you may either: 1.) use our exact code and place participants 60cm from the screen, while leaving the default monitor settings, or, 2.) change the stimulus sizes in visual angle directly to match those in the paper (in `sustained_attention_experiment/attention_memory.py` and `variable_attention_experiment/attention_memory.py`), then change your monitor center settings to reflect a distance of 60 cm.


# Acknowledgements
Thanks to Megan deBettencourt for providing the image processing script available in this repository (stimulus_generation_code/process_images.m) and recommending stimulus sets. 


FACE STIMULI:
J. Xiao, J. Hays, K. Ehinger, A. Oliva, and A. Torralba.
SUN Database: Large-scale Scene Recognition from Abbey to Zoo.
IEEE Conference on Computer Vision and Pattern Recognition (CVPR)

SCENE STIMULI:
P. Jonathon Phillips, Harry Wechsler, Jeffrey Huang, Patrick J. Rauss: The FERET database and evaluation procedure for face-recognition algorithms. Image Vision Comput. 16(5): 295-306 (1998)

