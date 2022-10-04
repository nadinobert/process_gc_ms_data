import os, sys

experiment = '20220301_practical C-DBT'
directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

# gives a list with all directories in my target/experiment folder
samples = os.listdir(directory)

for sample in samples:
    if os.path.isdir(os.path.join(directory, sample)):
        for root, dirs, files in os.walk(os.path.join(directory, sample)):
            print(directory)
            print(sample)
            if sample[0:4] == 'DBT_':
                sample_new1 = sample.split('_')[1] + '_' + sample.split('_')[2]
                sample_new2 = sample_new1.replace('-', '_')
                os.rename(os.path.join(root), os.path.join(root, sample_new2))
                #os.rename(directory, sample_new2)
