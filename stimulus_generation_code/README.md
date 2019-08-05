This directory contains the code needed to generate the stimuli used in our experiment from the raw images (subsampled from the SUN and FERET databases, cited below).

To generate our stimuli from scratch, first unzip `AM_STIM_ORIG`, `AM_STIM_BW`, and `COMPOSITES`. Then, you can run the code in `process_images.m` using Matlab (we used Matlab version R2017a) which will take the images from `AM_STIM_ORIG/SCENES_ORIG` and `AM_STIM_ORIG/FACES_ORIG`, process them (grayscale, resize, adjust intensity, equalize contrast), and write them out to `AM_STIM_BW/SCENES_ORIG` and `AM_STIM_BW/FACES_ORIG`, respectively.<br />

Then, run the code in `create_composites.m` which will read in the images in `AM_STIM_BW/SCENES_ORIG` and `AM_STIM_BW/FACES_ORIG`, compile them into composite images, and output them into `COMPOSITES`.

<h3>Acknowledgments</h3>
Thanks to Megan deBettencourt for providing the image processing script available in this repository (stimulus_generation_code/process_images.m) and recommending stimulus sets. <br /><br />

FACE STIMULI: J. Xiao, J. Hays, K. Ehinger, A. Oliva, and A. Torralba. SUN Database: Large-scale Scene Recognition from Abbey to Zoo. IEEE Conference on Computer Vision and Pattern Recognition (CVPR)

SCENE STIMULI: P. Jonathon Phillips, Harry Wechsler, Jeffrey Huang, Patrick J. Rauss: The FERET database and evaluation procedure for face-recognition algorithms. Image Vision Comput. 16(5): 295-306 (1998)
