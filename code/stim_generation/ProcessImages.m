% ProcessImages.m
%
% This script does various processing steps to raw image files
%   - read
%   - grayscale
%   - resize
%   - adjust intensity
%   - equalize contrast
%   - writes to a new directory, with a new name
%
%
% Written by NTB 2009
% Edited by MdB 6/2011

%% constants

imgformat = 'jpg';  %reading:   format of image
numrows = 256;      %resize:    number of rows
numcols = 256;      %resize:    number of columns
low_bound = .02;    %intenisty: lower bound of intensity
upper_bound = .98;  %intensity: upper bound of intensity
ntilesrows = 4;     %contrast:  number of tile rows
ntilescols = 4;     %contrast:  number of tile cols
nbins = 512;        %contrast:  number of bins for histogrm
cliplimit = .01;    %contrast:  limit of contrast enhancement


%% set up directories

% where raw files are located 
old_root_dir = '/Users/kirstenziman/Desktop/SUN_places/';
% where new files will be written 
new_root_dir = '/Users/kirstenziman/Desktop/SUN_places_pre/';
% subfolders containing image files
folders =  {'sunindoor550','sunoutdoor550'};
 

%% image processing loop 
imageCounter = 0;
for folder=1:length(folders) % loop through each folder 
    fprintf('---------------------------- Processing Folder %s, Folder # %d of %d ---------------------------- \n',folders{folder},folder,length(folders));

    % file directories
    old_folder = fullfile(old_root_dir,folders{folder});
    new_folder = fullfile(new_root_dir,[folders{folder}]); 
    assert(strcmp(old_folder,new_folder)==0,'you might overwrite your images!!');
    
    if(~(exist(new_folder,'dir')>0));mkdir(new_folder);end 
    
    % image list within folder
    img_files = dir(old_folder);
    img_files = img_files(3:size(img_files,1),:); %remove . and ..
    if (strcmp(img_files(1).name,'.DS_Store')) %sometimes appears
        img_files = img_files(2:end);
    end
    numImages = size(img_files,1);
    fprintf('---------------------------- %d Images within Folder  ---------------------------- \n',numImages);
        

    for index = 1:size(img_files,1) % loop through each image in the folder 
        imageCounter = imageCounter+1;
        orig_image = imread(fullfile(old_folder,img_files(index).name),imgformat);
        
        % grayscale
        if(size(size(orig_image),2)>2)
            gray_image = rgb2gray(orig_image);
        else
            gray_image = orig_image;
        end
        
        % resize
        imresize_image = imresize(gray_image,[numrows numcols]);
        
        % adjust intensity
        imad_image = imadjust(imresize_image, [low_bound upper_bound], []);
        
        % contrast-limited adaptive histogram equalization 
        imad_eq_image = adapthisteq(imad_image, 'NumTiles', [ntilesrows ntilescols], 'NBins', nbins, 'ClipLimit', cliplimit);
        
        % write image
        imwrite(imad_eq_image, [new_folder '/' img_files(index).name], 'jpg');
        
    end % end image loop
end % end folder loop 