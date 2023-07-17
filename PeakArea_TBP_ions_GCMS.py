# This code calculates the peak area of the main ions belonging to TBP -> Target ion at certain RT's
# ions: 328-335
# at 3 different retention times (or 2 RTs -> set RT2 to zero in the method to skip the third peak)
# the input data file has 24 lines (20-44) with ions and their respoonses
# 1) calc the sum of all ion peaks belonging to TBP in NCC -> calc the mean value over all replicates
# 2) calc the sum of all ion peaks belonging to TBP in each sample -> calc the mean of the peak areas over all replicates
# 3) compare the mean peak area value with NCC to calc remaining substrate

import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from adjust_timepoints import adjust_timepoints
from cleanup import cleanup

# time to plot figure 1 with DBP concentrations
def plotshit(x1, y1, y1error, pltname, yaxis, condition):
    plt.errorbar(x1, y1, yerr=y1error, marker='', capsize=3, capthick=0.5, ls='-', color='black',
                 linewidth=0.5)  # plot the errorbar
    plt.plot(x1, y1, linewidth=0.6)  # plot the simple line
    plt.scatter(x1, y1, marker='s', alpha=0.7, label='MM w ' + condition)  # plot the datapoint dots

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title(experiment + '\n' + pltname)
    plt.xlabel('Time [min]')
    plt.ylabel(yaxis)
    plt.legend(loc="upper left")
    plt.tight_layout()

np.set_printoptions(precision=10)

# experiment needs to be the name of the folder containing all sample folders
experiment = '20230613_E20_TBP_con'
line_TBP_ion = [x for x in range(20, 44)]     #line 20 till 44 ion peak data belonging to TBP for every ion at every RT use: range(20, 44), 36 till 43 belongs to acetylated peak to consider only acetylated TBP peak use: range(36, 44)
Init_Substrate_conc = 210           # initiale substrate concentration in µM
directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

# set font globally to 'times new roman'
plt.rcParams["font.family"] = "Times New Roman"

# gives a list with all directories in my target/experiment folder
samples = os.listdir(directory)

results = pd.DataFrame()
# iterrate through list of samples and open result file
for sample in samples:
    if os.path.isdir(os.path.join(directory, sample)):
        replicate = sample.split('_')[2].split('.')[0]
        time = sample.split('_')[1]
        mastermix = sample.split('_')[0]
        for root, dirs, files in os.walk(os.path.join(directory, sample)):
            for filename in files:
                if filename == 'epatemp.txt':
                    data = open(os.path.join(directory, sample, 'epatemp.txt'))
                    for i, ln in enumerate(data):
                        if i in line_TBP_ion:
                            new = ln.split(" ")
                            try:
                                RT_No = (list(filter(lambda x: x != '', new))[1]).split('_')[2]
                            except IndexError:
                                print(sample)
                            peakarea = (list(filter(lambda x: x != '', new))[4])
                            RT = (list(filter(lambda x: x != '', new))[2])
                            results = results.append(
                                {'Mastermix_with': mastermix, 'timepoint_[min]': time, 'replicate': replicate,
                                 'RT_[min]': RT, 'Peak_Area': peakarea, 'RT': RT_No}, ignore_index=True)

# adjust the timepoints to [min] as unit in dataframe
adjust_timepoints(results)


#delete all entries with RT=0
results['Peak_Area'] = pd.to_numeric(results['Peak_Area'], errors='coerce')
results = results.dropna()
#Extract NCC value for calculation
NCC_TBP_df = results.loc[(results['timepoint_[min]'] == 'NCC')]
NCC_TBP_df = NCC_TBP_df.groupby(['Mastermix_with', 'timepoint_[min]', 'replicate']).agg({'Peak_Area': ['sum']})
NCC_TBP_df = NCC_TBP_df.reset_index()
NCC_TBP_df.columns = ['Mastermix_with', 'timepoint_[min]', 'replicate', 'Peak_Area_sum']
NCC_TBP_mean = NCC_TBP_df['Peak_Area_sum'].mean()
#get rid of all dump control samples NCC and NSC lol
results = results.loc[(results['timepoint_[min]'] != 'NCC') & (results['timepoint_[min]'] != 'NSC')]

#print(NCC_TBP_mean)
#print(results)

results.dropna(inplace=True, how='any')

#calc the sum of all TBP ion peak in each repl
calc_TBP = results.groupby(['Mastermix_with', 'timepoint_[min]', 'replicate']).agg({'Peak_Area': ['sum']})
calc_TBP = cleanup(calc_TBP)
calc_TBP.columns = ['Mastermix_with', 'timepoint_[min]', 'replicate', 'Peak_Area_sum']


#calc the mean of all TBP ion peak per timepoint
calc_TBP = calc_TBP.groupby(['Mastermix_with', 'timepoint_[min]']).agg({'Peak_Area_sum': ['mean', 'std']})
calc_TBP = cleanup(calc_TBP)
print(calc_TBP)
calc_TBP.columns = ['Mastermix_with', 'timepoint_[min]', 'Peak_Area_mean', 'Peak_Area_std']
print(calc_TBP)

#calc the remaining TBP concentration according to the initial TBP concentration
calc_TBP['TBP_[µM]'] = (calc_TBP['Peak_Area_mean'] / NCC_TBP_mean) * Init_Substrate_conc
calc_TBP['TBP_[µM]_Std'] = (calc_TBP['Peak_Area_std'] / NCC_TBP_mean) * Init_Substrate_conc

print(calc_TBP)

x1 = np.array(calc_TBP['timepoint_[min]'].values)
y1 = np.array(calc_TBP['TBP_[µM]'].values)
y1error = np.array(calc_TBP['TBP_[µM]_Std'].values)

condition = pd.unique(results['Mastermix_with'])

for cond in condition:
    plotshit(x1, y1, y1error, 'Remaining TBP [µM]]', 'Concentration [µM]', condition)
    #plt.savefig('simple' + '_D2O_H2O_product_amount' + '.svg')
    plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Remaining_TBP'))
    #calc_results_DBP.to_csv(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Formed product, MM with H2O'), index=False)
    #plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Produced_DBP'))
    plt.show()





