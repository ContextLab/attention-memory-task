%% create composite image
%  written 1/24/18 - KZ

%% variables and path names

main_dir = '/Users/kirstenziman/Desktop/comp_test/';

subdir_1 = 'test1/';
subdir_2 = 'test2/';

% file extension of image files
file_ext = '.jpg';

% list of files in each subdir
file_list_1 = dir(fullfile(strcat(main_dir,subdir_1, '*', file_ext)));
file_list_2 = dir(fullfile(strcat(main_dir,subdir_2, '*', file_ext)));

%% change this line to iterate over the desired number of stimuli 

% loop over subdir images

for x = 1:numel(file_list_1);
% for im1,im2 = zip(file_list_1, file_ilst_2)
    
    % get each file path
    path1 = strcat(file_list_1(x).folder, '/', file_list_1(x).name);
    path2 = strcat(file_list_2(x).folder, '/', file_list_2(x).name);
    
    % load each image
    im1 = imread(path1);
    im2 = imread(path2);
    
    % make composite of the loaded images
    composite = imfuse(im1, im2, 'blend','Scaling','joint');
    
    % composite image filename (combo of original file names)
    comp_name = strcat('/Users/kirstenziman/Desktop/composites/', file_list_1(x).name(1:length(file_list_1(x).name)-length(file_ext)), '_', file_list_2(x).name(1:length(file_list_2(x).name)-length(file_ext)), file_ext);
    
    % save composite
    imwrite(composite, comp_name);
    
end