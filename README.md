# Overview

This repository contains the experiment and analysis code for a psychology experiment exploring the relationship between covert attention and recognition memory.  

![attn task image](figs/attn_task.png)

# Installation

Add instructions

# Running the task

After full installation, running the task is simple!

To run a behavioral participant, simply open attention_memory.py in Psychopy, hit the green "run" button in the code viewer, and enter the subejct ID and run#!  For run #, always enter 0 unless you have a very specific reason to desire fewer than the total number of runs indicated in params dictionary, without changing params itself (this is NOT recommended for normal use).  The self-paced instructions and practice rounds will display sequentially for the subject as long as practice=True (the default setting).

To incorporate eye tracking, simply set up your eye tracker to record timestamps using your machines universal clock, then use our anlysis code to match your those timestamps to salient points in the experiment.Our code is compatible with EyeTribe developer kit, but all lines that require changing to accommodate other systems are commented as such :)

For fMRI....

for EEG...

to run one trial at a time, independent of the specific modality... 


# Analyzing data

Provide sample data, code, and instructions

# Acknowledgements

This code is adapted from the Posner code provided by Github user CypressA.
