# This code calculates the peak area of the main ions belonging to DBP -> Target ion at certain RT's
# ions: 250-254
# at 3 different retention times (or 2 RTs -> set RT2 to zero in the method to skip the third peak)
# the input data file has 15 lines (20-35) with ions and their respoonses
# 1) calc the sum of all ion peaks belonging to DBP in every sample per RT -> calc the mean value over all replicates
# 2) calc the concentration Response/ Peakarea according to calibration 20230711

##TODO: instead of plotting x1,y1 and y2,y2 together it could be changed to a loop. the problem was that the inset plot does not behave like the main plot. Only one dataset was plottet instead of both.

import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

from adjust_timepoints import adjust_timepoints
from cleanup import cleanup

# time to plot figure 1 with DBP concentrations
def plotshit(x1, y1, y1error, x2, y2, y2error, pltname, yaxis, condition1, condition2):
    plt.errorbar(x1, y1, yerr=y1error, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)  # plot the errorbar
    plt.plot(x1, y1, linewidth=0.6)  # plot the simple line
    plt.scatter(x1, y1, marker='s', alpha=0.7, label='20% D2O ')  # plot the datapoint dots

    plt.errorbar(x2, y2, yerr=y2error, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)  # plot the errorbar
    plt.plot(x2, y2, linewidth=0.6)  # plot the simple line
    plt.scatter(x2, y2, marker='s', alpha=0.7, label='80% D2O ')  # plot the datapoint dots

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title(experiment + '\n' + pltname)
    plt.xlabel('Time [min]')
    plt.ylabel(yaxis)
    plt.legend(loc="upper left")
    plt.tight_layout()

    # create inset axes
    axins = ax.inset_axes([0.7, 0.33, 0.2, 0.2])         #first two numbers give the position of the small plot in the plot, the second two numbers give the relative size

    axins.errorbar(x1, y1, yerr=y1error, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)   #plot the errorbar
    axins.plot(x1, y1, linewidth=0.6)  #plot the simple line
    axins.scatter(x1, y1, marker='s', alpha=0.7)      #plot the datapoint dots

    axins.errorbar(x2, y2, yerr=y1error, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)   #plot the errorbar
    axins.plot(x2, y2, linewidth=0.6)  #plot the simple line
    axins.scatter(x2, y2, marker='s', alpha=0.7)      #plot the datapoint dots

    axins.set_xlim(-0.5, 3)     # location of subpart of the plot that should be zoomed in
    axins.set_ylim(-0.5, 42)  # location of subpart of the plot that should be zoomed in
    axins.set_xticks(np.arange(0, 4, 1))

    # mark the zoomed region
    mark_inset(ax, axins, loc1=2, loc2=3, fc="none", ec="0.5")

    return(ax)

np.set_printoptions(precision=10)

# experiment needs to be the name of the folder containing all sample folders
experiment = '20230711'
line_DBP_ion = [x for x in range(31, 36)]     #line 31 till 36 ion peak data belonging to acetylated DBP at RT 3
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
                        if i in line_DBP_ion:
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

print(results)

results.dropna(inplace=True, how='any')

#calc the sum of all DBP ion peak in each repl
calc_DBP = results.groupby(['Mastermix_with', 'timepoint_[min]', 'replicate']).agg({'Peak_Area': ['sum']})
calc_DBP = cleanup(calc_DBP)
calc_DBP.columns = ['Mastermix_with', 'timepoint_[min]', 'replicate', 'Peak_Area_sum']

#calc the mean of all DBP ion peak per timepoint
calc_DBP = calc_DBP.groupby(['Mastermix_with', 'timepoint_[min]']).agg({'Peak_Area_sum': ['mean', 'std']})
calc_DBP = cleanup(calc_DBP)
print(calc_DBP)
calc_DBP.columns = ['Mastermix_with', 'timepoint_[min]', 'Peak_Area_mean', 'Peak_Area_std']
print(calc_DBP)

#calc concentration according to calibration
calc_DBP['DBP_[µM]'] = (calc_DBP['Peak_Area_mean'] / 34190)
calc_DBP['DBP_[µM]_Std'] = (calc_DBP['Peak_Area_std'] / 34190)

conditions = pd.unique(calc_DBP['Mastermix_with'])

calc_E20 = calc_DBP.loc[(calc_DBP['Mastermix_with'] == 'E20')]
x1 = np.array(calc_E20['timepoint_[min]'].values)
y1 = np.array(calc_E20['DBP_[µM]'].values)
y1error = np.array(calc_E20['DBP_[µM]_Std'].values)

calc_E80 = calc_DBP.loc[(calc_DBP['Mastermix_with'] == 'E80')]
x2 = np.array(calc_E80['timepoint_[min]'].values)
y2 = np.array(calc_E80['DBP_[µM]'].values)
y2error = np.array(calc_E80['DBP_[µM]_Std'].values)

plotshit(x1, y1, y1error, x2, y2, y2error, 'Formed DBP [µM]', 'DBP [µM]', 'E20', 'E80')
#plt.savefig('simple' + '_D2O_H2O_product_amount' + '.svg')
plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Produced_DBP'))
#calc_results_DBP.to_csv(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Formed product, MM with H2O'), index=False)
plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Produced_DBP' + '.svg'))

plt.show()





