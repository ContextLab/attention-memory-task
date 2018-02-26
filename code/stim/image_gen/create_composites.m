%% create composite image
%  written 1/24/18 - KZ

%% variables and path names

main_dir = '/Users/kirstenziman/Desktop/360_stim_new/';

subdir_1 = 'faces/';
subdir_2 = 'scenes/';

% file extension of image files
file_ext = '.jpg';

% list of files in each subdir
file_list_1 = dir(fullfile(strcat(main_dir,subdir_1, '*', file_ext)));
file_list_2 = dir(fullfile(strcat(main_dir,subdir_2, '*', file_ext)));

%% if not splitting female / male and indoor / outdoor

for x = 1:length(file_list_1);
    path1 = strcat(file_list_1(x).folder, '/', file_list_1(x).name);
    path2 = strcat(file_list_2(x).folder, '/', file_list_2(x).name);

    im1 = imread(path1);
    im2 = imread(path2);

    composite = imfuse(im1, im2, 'blend','Scaling','joint');

    % composite image filename (combo of original file names)
    comp_name = strcat('/Users/kirstenziman/Desktop/composites_new/', file_list_1(x).name(1:length(file_list_1(x).name)-length(file_ext)), '_', file_list_2(x).name);
    
    % save composite
    imwrite(composite, comp_name);
    
end

%% split file lists 

% file_list_1a = file_list_1(1:numel(file_list_1)/2);
% file_list_1b = file_list_1((numel(file_list_1)/2)+1:numel(file_list_1));
% file_list_2a = file_list_2(1:numel(file_list_2)/2);
% file_list_2b = file_list_2((numel(file_list_2)/2)+1:numel(file_list_2));

%% loop over feamle faces

% for x=[1:numel(file_list_1a)];
%         
%     path1 = strcat(file_list_1a(x).folder, '/', file_list_1a(x).name);
% 
%     if x <= numel(file_list_1a)/2 ;
%         path2 = strcat(file_list_2a(x).folder, '/', file_list_2a(x).name);
%         name2 = file_list_2a(x).name(1:length(file_list_2a(x).name)-length(file_ext))
%     else
%         path2 = strcat(file_list_2b(x-numel(file_list_1a)/2).folder, '/', file_list_2b(x-numel(file_list_1a)/2).name);
%         name2 = file_list_2b(x-numel(file_list_1a)/2).name(1:length(file_list_2b(x-numel(file_list_1a)/2).name)-length(file_ext))
%     end
%     
%     % load each image
%     im1 = imread(path1);
%     im2 = imread(path2);
%     
%     % make composite of the loaded images
%     composite = imfuse(im1, im2, 'blend','Scaling','joint');
%     
%     % composite image filename (combo of original file names)
%     comp_name = strcat('/Users/kirstenziman/Desktop/composites_new/', file_list_1(x).name(1:length(file_list_1a(x).name)-length(file_ext)), '_', name2, file_ext);
%     
%     % save composite
%     imwrite(composite, comp_name);
% 
% end


%% loop over male faces

for x=[1:numel(file_list_1b)]
        
    path1 = strcat(file_list_1b(x).folder, '/', file_list_1b(x).name)

    if x <= numel(file_list_1b)/2 
        path2 = strcat(file_list_2a(x+numel(file_list_1a)/2).folder, '/', file_list_2a(x+numel(file_list_1a)/2).name)
        name2 = file_list_2a(x+numel(file_list_1a)/2).name(1:length(file_list_2a(x+numel(file_list_1a)/2).name)-length(file_ext))
    else
        path2 = strcat(file_list_2b(x).folder, '/', file_list_2b(x).name)
        name2 = file_list_2b(x).name(1:length(file_list_2b(x).name)-length(file_ext))
    end
    
    % load each image
    im1 = imread(path1);
    im2 = imread(path2);
    
    % make composite of the loaded images
    composite = imfuse(im1, im2, 'blend','Scaling','joint');
    
    % composite image filename (combo of original file names)
    comp_name = strcat('/Users/kirstenziman/Desktop/composites_even/', file_list_1b(x).name(1:length(file_list_1b(x).name)-length(file_ext)), '_', file_list_2(x).name(1:length(file_list_2(x).name)-length(file_ext)));
    
    % save composite
    imwrite(composite, comp_name);
    
end
