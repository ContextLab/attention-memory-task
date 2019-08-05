%% create composite image
%  written 1/24/18 - KZ

%% variables and path names

main_dir = 'AM_STIM_BW/';

subdir_1 = 'FACES_ORIG/';
subdir_2 = 'SCENES_ORIG/';

% file extension of image files
file_ext = '.jpg';

% list of files in each subdir
file_list_1 = dir(fullfile(strcat(main_dir,subdir_1, '*', file_ext)));
file_list_2 = dir(fullfile(strcat(main_dir,subdir_2, '*', file_ext)));

%% overlay images

for x = 1:length(file_list_1);
    path1 = strcat(file_list_1(x).folder, '/', file_list_1(x).name);
    path2 = strcat(file_list_2(x).folder, '/', file_list_2(x).name);

    im1 = imread(path1);
    im2 = imread(path2);

    % create composite image
    composite = imfuse(im1, im2, 'blend','Scaling','joint');

    % composite image filename (combo of original file names)
    comp_name = strcat('COMPOSITES/', file_list_1(x).name(1:length(file_list_1(x).name)-length(file_ext)), '_', file_list_2(x).name);

    % save composite
    imwrite(composite, comp_name);

end


