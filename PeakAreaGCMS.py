# Calculations based on TIC at certain RT's
# this code is for TIC (peak area at specific time points)
# This code calculates the peak area and the corresponding DBP concentration per time point according to a calibration. Considered is only acetlyated product!
# The code can also determine the consumed substrate per timepoint by substracting the amount of remaining product compared to NCC
# The input datafile has 6 lines: DPB at RT1,2,3 (line 20,21,22) and TBP at RT1,2,3 (line 23,24,25)

import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from adjust_timepoints import adjust_timepoints

np.set_printoptions(precision=10)

# experiment needs to be the name of the folder containing all sample folders
experiment = '20230613_E80_peakarea'
line_DBP_TBP = [20, 23]     #line 22: with RT 11.55 acetylated DBP, line 20, 21 is unacetylated DBP
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
                        if i in line_DBP_TBP:
                            new = ln.split(" ")
                            ion = (list(filter(lambda x: x != '', new))[1]).split('_')[1]
                            peakarea = (list(filter(lambda x: x != '', new))[4])
                            RT = (list(filter(lambda x: x != '', new))[2])
                            if i == 22 or i == 21 or i == 20:
                                substance = 'DBP'
                            else:
                                substance = 'TBP'
                            results = results.append(
                                {'Mastermix_with': mastermix, 'timepoint_[min]': time, 'replicate': replicate,
                                 'RT': RT, 'Peak_Area': peakarea, 'Substance': substance}, ignore_index=True)

# adjust the timepoints to [min] as unit in dataframe
adjust_timepoints(results)

#delete all entries with RT=0
results['Peak_Area'] = pd.to_numeric(results['Peak_Area'], errors='coerce')
results = results.dropna()
#Extract NCC value for calculation
NCC_TBP_df = results.loc[(results['Substance'] == 'TBP') & (results['timepoint_[min]'] == 'NCC')]
NCC_TBP = NCC_TBP_df['Peak_Area'].mean()
#get rid of all dump control samples NCC and NSC lol
results = results.loc[(results['timepoint_[min]'] != 'NCC') & (results['timepoint_[min]'] != 'NSC')]

condition = pd.unique(results['Mastermix_with'])
timepoints = pd.unique(results['timepoint_[min]'])

results.dropna(inplace=True, how='any')

for cond in condition:
    calc_results_DBP = pd.DataFrame()
    calc_results_TBP = pd.DataFrame()

    ## y = 4E+06x
    ## linear_reg_RT3 = 4E+06 * x with R^2 =0.98 -> experiment/calibration: 20230511
    ##function to calc the concentration based on the regression and the peak area
    def calc_concentration(arr):
        output = np.empty(len(arr))
        for i, y in enumerate(arr):
            result = y / 4E+06
            output[i] = result
        return output

    for time in timepoints:
        if time != 'NCC' and time != 'NSC':

            calc_DBP = results.loc[(results['Mastermix_with'] == cond) & (results['timepoint_[min]'] == time) & (results['Substance'] == 'DBP')]
            if len(calc_DBP) > 0:
                peak_area_array = (calc_DBP['Peak_Area'].to_numpy()).astype(np.int64)
                MW_Peak_DBP = calc_DBP['Peak_Area'].mean()
                Std_Peak_DBP = calc_DBP['Peak_Area'].std()

                conc_array = calc_concentration(peak_area_array)
                sum_of_conc = np.sum(conc_array).astype(float)
                MW_conc_DBP = sum_of_conc / float(conc_array.size)
                Std_conc_DBP = np.std(conc_array)
                calc_results_DBP = calc_results_DBP.append(
                    {'Mastermix_with': cond, 'timepoint_[min]': time,
                     'MW_PeakArea_DBP': MW_Peak_DBP, 'Std_PeakArea_DBP': Std_Peak_DBP, 'MW_conc_DBP': MW_conc_DBP, 'Std_conc_DBP': Std_conc_DBP}, ignore_index=True)

            calc_TBP = results.loc[(results['Mastermix_with'] == cond) & (results['timepoint_[min]'] == time) & (results['Substance'] == 'TBP')]
            if len(calc_TBP) > 0:
                MW_peak_area_TBP = calc_TBP['Peak_Area'].mean()
                Std_peak_area_TBP = calc_TBP['Peak_Area'].std()
                MW_prozent_TBP = (MW_peak_area_TBP / NCC_TBP)
                MW_conc_TBP = MW_prozent_TBP * Init_Substrate_conc
                Std_prozent_TBP = (Std_peak_area_TBP / NCC_TBP)
                Std_prozent_TBP = Std_prozent_TBP * Init_Substrate_conc
                calc_results_TBP = calc_results_TBP.append(
                    {'Mastermix_with': cond, 'timepoint_[min]': time,
                     'MW_PeakArea_TBP': MW_peak_area_TBP, 'Std_PeakArea_TBP': Std_peak_area_TBP, 'MW_conc_TBP': MW_conc_TBP, 'Std_prozent_TBP': Std_prozent_TBP}, ignore_index=True)

# order the df by the timepoints ascending
    calc_results_DBP = calc_results_DBP.sort_values(by='timepoint_[min]')
    calc_results_TBP = calc_results_TBP.sort_values(by='timepoint_[min]')
    calc_results_DBP.dropna()
    print(calc_results_DBP)
    print(calc_results_TBP)

# time to plot figure 1 with DBP concentrations
def plotshit(x1, y1, y1error, pltname, yaxis):
    #x1 = list(calc_results_DBP.loc[(calc_results_DBP['Mastermix_with'] == cond)].iloc[:, 5])
    #y1 = list(calc_results_DBP.loc[(calc_results_DBP['Mastermix_with'] == cond)].iloc[:, 1])
    #y1error = list(calc_results_DBP.loc[(calc_results_DBP['Mastermix_with'] == cond)].iloc[:, 4])

    plt.errorbar(x1, y1, yerr=y1error, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)   #plot the errorbar
    plt.plot(x1, y1, linewidth=0.6)  #plot the simple line
    plt.scatter(x1, y1, marker='s', alpha=0.7, label='MM w ' + cond)   #plot the datapoint dots

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title(experiment +'\n' + pltname)
    plt.xlabel('Time [min]')
    plt.ylabel(yaxis)
    plt.legend(loc="upper left")
    plt.tight_layout()


plotshit(list(calc_results_DBP.loc[(calc_results_DBP['Mastermix_with'] == cond)].iloc[:, 5]), list(calc_results_DBP.loc[(calc_results_DBP['Mastermix_with'] == cond)].iloc[:, 1]), list(calc_results_DBP.loc[(calc_results_DBP['Mastermix_with'] == cond)].iloc[:, 4]), 'Produced DBP', 'Concentration [µM]')
#plt.savefig('simple' + '_D2O_H2O_product_amount' + '.svg')
calc_results_DBP.to_csv(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Formed product, MM with H2O'), index=False)
plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Produced_DBP'))
plt.show()

plotshit(list(calc_results_TBP.loc[(calc_results_TBP['Mastermix_with'] == cond)].iloc[:, 5]), list(calc_results_TBP.loc[(calc_results_TBP['Mastermix_with'] == cond)].iloc[:, 1]), list(calc_results_TBP.loc[(calc_results_TBP['Mastermix_with'] == cond)].iloc[:, 4]), 'Remaining TBP', 'Concentration [µM]')
#plt.savefig('simple' + '_D2O_H2O_product_amount' + '.svg')
#calc_results_TBP.to_csv(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Formed product, MM with H2O'), index=False)
plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'Remaining_TBP'))
plt.show()





