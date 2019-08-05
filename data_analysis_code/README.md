<h3> Behavioral Data </h3>
To start exploring the behavioral data from the experiments, we first ran the code in the `compile_behavioral_data` notebook. This code organizes and compiles the raw behavioral data from all of the participants in each experiment. It outputs a single dataframe for each experiment, containing all of that experiment's behavioral data, into the `../parsed_data` directory. <br />

Then, we ran the code in `analyze_behavioral_data` to generate statistics on participants' memory for attended and unattended images. We also used the code in this notebook to generate the violin plot (Figure 2) and timecourse figures (Figures 4, 5, and 6) shown in our manuscript. <br />

To explore the behavioral data yourself, you can follow these same steps (compiling the data, then analyzing it), or you can start by simply running the code in `analyze_behavioral_data`, since the output from the first step has already been saved for you in this repository.

<h3> Gaze Data </h3>
To start exploring the gaze data from the experiment, and incorporating it into the analysis of the behavioral data, we first ran the code in the `compile_gaze_data_sustained` and `compile_gaze_data_variable` notebooks, respectively. This code organizes and compiles the raw gaze data from all of the participants in each experiment. It outputs a single dataframe for each experiment, containing all of that experiment's gaze data, into the `../parsed_data` directory. <br />

Then, we ran the code in `analyze_gaze_data` to generate statistics on participants' shifts in gaze along the horizontal axis during image viewing, and to plot these gaze shifts with respect to participants' later memory for the images (Figure 3). Further, this code generates our data "check" statistics, where we conduct the same key analyses as in `compile_behavioral_data`, but using only the subset of the data where participants followed our instructions to keep their gaze *between* the images on the screen. <br />

To explore the gaze data yourself, you can follow these same steps (compiling the data, then analyzing it), or you can start by simply running the code in `analyze_gaze_data`, since the output from the first step has already been saved for you in this repository.
