import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# experiment needs to be the name of the folder containing all sample folders
experiment = '20220301_D2O_H2O_dynamic'
linenums = [21]     #line 21: with RT 11.53 acetylated compound, line 20 is unacetylated compound
directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

# gives a list with all directories in my target/experiment folder
samples = os.listdir(directory)

results = pd.DataFrame()
# iterrate through list of samples and open result file
for sample in samples:
    if os.path.isdir(os.path.join(directory, sample)):
        replicate = sample.split('_')[2].split('.')[0]
        time = sample.split('_')[1]
        if time != 'NCC' and time != 'NSC':
            time = re.sub('\D', '', time)
        mastermix = sample.split('_')[0]
        for root, dirs, files in os.walk(os.path.join(directory, sample)):
            for filename in files:
                if filename == 'epatemp.txt':
                    data = open(os.path.join(directory, sample, 'epatemp.txt'))
                    for i, ln in enumerate(data):
                        if i in linenums:
                            new = ln.split(" ")
                            ion = (list(filter(lambda x: x != '', new))[1]).split('_')[1]
                            peakarea = (list(filter(lambda x: x != '', new))[4])
                            RT = (list(filter(lambda x: x != '', new))[2])
                            results = results.append(
                                {'Mastermix_with': mastermix, 'timepoint_[min]': time, 'replicate': replicate,
                                 'RT': RT, 'Peak_Area': peakarea}, ignore_index=True)

condition = pd.unique(results['Mastermix_with'])
timepoints = pd.unique(results['timepoint_[min]'])

print(results)

calc_results = pd.DataFrame()
for cond in condition:
    for time in timepoints:
        if time != 'NCC' and time != 'NSC':
            calc = results.loc[(results['Mastermix_with'] == cond) & (results['timepoint_[min]'] == time)]
            print(calc)
            try:
                calc_array = (calc['Peak_Area'].to_numpy()).astype(np.int64)
            except Exception:
                print(calc)
            #print(calc_array)
            Std_Peak = np.std(calc_array)
            MW_Peak = np.median(calc_array)
            calc_results = calc_results.append(
                {'Mastermix_with': cond, 'timepoint_[min]': time,
                 'MW_Peak_Area': MW_Peak}, ignore_index=True)
    #print(calc_results)

    x1 = list(calc_results.loc[(calc_results['Mastermix_with'] == cond)].iloc[:, 2])
    y1 = list(calc_results.loc[(calc_results['Mastermix_with'] == cond)].iloc[:, 0])

    plt.errorbar(x1, y1, yerr=Std_Peak, marker='s', alpha=0.7, capsize=10, label=cond)
    plt.title(experiment + ' Compare D2O and H2O')
    plt.xlabel('time [min]')
    plt.ylabel('Peak_Area')
    plt.legend(loc="upper left")
plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'CompareH2OD2O'))
plt.show()







