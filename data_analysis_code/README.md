<h3>Behavioral Data</h3>

To start exploring the behavioral data, we first ran the code in the `compile_behavioral_data` notebook. This code organizes and compiles the raw behavioral data from all of the participants in each experiment. It outputs one dataframe with behavioral data for all participants, one dataframe with the full gaze data for all participants, and one dataframe with the gaze data for all participants only at times when the presentation images are on screen (labeled by experiment and group); the dataframes are saved to the `../parsed_data` directory as csv files (full_behavioral.csv, full_gaze.csv, and full_pres_gaze.csv).

Then, we ran the code in `analyze_behavioral_data` to generate statistics on participants' memory for attended and unattended images. Running `analyze_behavioral_data_combined` analyzes all of the data together. Running `analyze_behavioral_data_by_group` analyzes the data from the two test groups in each experiment, separately. We also used the code in these analysis notebooks to generate the violin plot figure (Figure 2) and timecourse figures (Figures 4, 5, and 6) shown in our manuscript, as well as the "by group" plots provided in the Appendix.

To explore the behavioral data yourself, you can follow these same steps (compiling the data, then analyzing it), or you can start by simply running the code in the analysis notebooks, since the output from the first step has already been saved for you.

<h3>Gaze Data</h3>
To start exploring the gaze data, and incorporating it into the analysis of the behavioral data, we first ran the code in the `compile_gaze_data_sustained` and `compile_gaze_data_variable` notebooks, respectively. This code organizes and compiles the raw gaze data from all of the participants in each experiment. It outputs a single dataframe for each experiment, containing all of that experiment's gaze data, into the `../parsed_data` directory. </p>

Then, we ran the code in `analyze_gaze_data` to generate statistics on participants' shifts in gaze along the horizontal axis during image viewing, and to plot these gaze shifts with respect to participants' later memory for the images (Figure 3). Further, this code generates our data "check" statistics, where we conduct the same key analyses as in `compile_behavioral_data`, but using only the subset of the data where participants followed our instructions to keep their gaze *between* the images on the screen.

To explore the gaze data yourself, you can follow these same steps (compiling the data, then analyzing it), or you can start by simply running the code in `analyze_gaze_data`, since the output from the first step has already been saved for you.


Order of operations:

+ Compile behavioral and gaze data
+ behavioral checks
+ gaze checks

+ main behavioral analyses
+ main gaze analyses

<<<<<<< HEAD
+ compare across groups, etc
=======
+ compare across groups, etc
>>>>>>> 6d729aa13dc8cd666332aa6ba2aaf15520192cd3
