import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from cleanup import cleanup
from plot_break import figure_break
from plot_zoom import figure_zoom
from plot_simple import figure_simple
from adjust_timepoints import adjust_timepoints


#TODO delete RT2 (11.1 min) in approaches with TBP substrate -> unsure what sis is
#TODO: set up function for plotting
#TODO: find a better way to define y-axis-range muss das definiert werden? nimmt er nicht eh immer den besten ausschnitt?

def process_sample_name(directory, sample):
    if os.path.isdir(os.path.join(directory, sample)):
        replicate = sample.split('_')[2].split('.')[0]
        time = sample.split('_')[1]
        mastermix = sample.split('_')[0]
        return replicate, time, mastermix
    else:
        return None, None, None

def extract_peakarea(line, sample):
    fields = line.split(" ")
    fieldsList = list(filter(lambda x: x != '', fields))
    try:
        ion = (fieldsList[1]).split('_')[1]
    except Exception:
        print(sample)
    RT = (fieldsList[1]).split('_')[2]
    peakarea = fieldsList[4]
    try:
        peakarea = float(peakarea)
    except Exception:
        peakarea = np.nan
    return (ion, RT, peakarea)


# set font globally to 'times new roman'
plt.rcParams["font.family"] = "Times New Roman"

# experiment needs to be the name of the folder containing all sample folders
experiment = '20230711_E20'
global tested_substrate
tested_substrate = 'TBP'
equ_MMw_H2O = 0.2
equ_MMw_D2O = 0.2

if tested_substrate == 'TBP':
    ion_types = {250: 'DD1', 251: 'DD1', 252: 'DD2', 253: 'DD2'}
    #linenums = range(21, 33)    #linenums represents the rows in the text file with related data
    linenums = list(range(21, 25)) + list(range(26, 30)) + list(range(31, 35))      #adjusted for new evaluation method considering ion 251-254 for quantification
if tested_substrate == 'TCP':
    ion_types = {162: 'DD1', 163: 'DD1', 164: 'DD2', 165: 'DD2'}
    linenums = range(21, 29)
if tested_substrate == 'TeCB':
    ion_types = {180: 'DD1', 181: 'DD1', 182: 'DD2', 183: 'DD2'}
    linenums = range(21, 25)

directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

# gives a list with all directories in my target/experiment folder
samples = os.listdir(directory)

results = pd.DataFrame()

# iterrate through list of samples and append result file
for sample in samples:
    replicate, time, mastermix = process_sample_name(directory, sample)
    if all(x is not None for x in (replicate, time, mastermix)):
        for root, dirs, files in os.walk(os.path.join(directory, sample)):
            for filename in files:
                if filename == 'epatemp.txt':
                    data = open(os.path.join(directory, sample, 'epatemp.txt'))
                    odd = True
                    oddPeakArea = 0
                    for i, line in enumerate(data):
                        if i in linenums:
                            ion, RT, peakarea = extract_peakarea(line, sample)
                            if odd:
                                oddPeakArea = peakarea
                            else:
                                evenPeakArea = peakarea
                                deuteriumDegree = evenPeakArea / (oddPeakArea + evenPeakArea)
                                if not np.isnan(deuteriumDegree):
                                    results = results.append(
                                    {'Mastermix_with': mastermix, 'timepoint_[min]': time, 'replicate': replicate,
                                     'ion': int(ion), 'quotient': deuteriumDegree, 'RT': RT}, ignore_index=True)
                            odd = not odd

# add the ionpair assignment to dataframe
results['ion_type'] = results.apply(lambda row: ion_types[row['ion']], axis=1)

# adjust the timepoints to [min] as unit in dataframe
adjust_timepoints(results)

#get rid of all dump control samples
results = results.loc[(results['timepoint_[min]'] != 'NCC') & (results['timepoint_[min]'] != 'NSC')]

#calc df contains data for fiure 1, 2 and 3 (Single figures for each RT)
#calc2 df contains data for figure 4 (Average of all RTs)
#via aggr function different calulations can be applied to a certain column like calculate mean or std from specific group
calc = results.groupby(['Mastermix_with', 'timepoint_[min]', 'RT', 'ion_type']).agg({'quotient': ['mean', 'std', 'count']})
calc2 = results.groupby(['Mastermix_with', 'timepoint_[min]', 'ion_type']).agg({'quotient': ['mean', 'std', 'count']})

# selects all data of calculated DD1 and DD2 from cleaned df for figure 1, 2 and 3
# select all data of calculated DD1 and DD2 from cleaned df for figure 4
calc_DD1 = cleanup(calc).loc[cleanup(calc)['ion_type'] == 'DD1']
calc_DD2 = cleanup(calc).loc[cleanup(calc)['ion_type'] == 'DD2']
calc_MW = cleanup(calc2)

condition = pd.unique(results['Mastermix_with'])
RTs = pd.unique(results['RT'])
RTs = list(map(int, RTs))

# plot data
# for every MM approach
# figure 1, 2, 3: DD1 and DD2 at RT1, RT2, RT3
# figure 4: Average of all RT's
for MM in condition:
    for Num_RT in RTs:
        calc_DD1_RT = calc_DD1.loc[(calc_DD1['RT'] == str(Num_RT)) & (calc_DD1['Mastermix_with'] == MM)]
        calc_DD2_RT = calc_DD2.loc[(calc_DD2['RT'] == str(Num_RT)) & (calc_DD2['Mastermix_with'] == MM)]

        figure_zoom(calc_DD1_RT, calc_DD2_RT, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, str(Num_RT), tested_substrate)
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(Num_RT)) + MM +'zoom' + '.svg')
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(Num_RT)) + MM + 'zoom')
        figure_break(calc_DD1_RT, calc_DD2_RT, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, str(Num_RT), tested_substrate)
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(Num_RT)) + MM + 'break')
        figure_simple(calc_DD1_RT, calc_DD2_RT, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, str(Num_RT), tested_substrate)
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(Num_RT)) + MM + 'simple')

        plt.show()

    #figure 4: AVG(DD1, DD2)
    calc_MW_DD1 = calc_MW.loc[(calc_MW['ion_type'] == 'DD1') & (calc_MW['Mastermix_with'] == MM)]
    calc_MW_DD2 = calc_MW.loc[(calc_MW['ion_type'] == 'DD2') & (calc_MW['Mastermix_with'] == MM)]

    figure_break(calc_MW_DD1, calc_MW_DD2, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, 'all RTs', tested_substrate)
    plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'MW' + MM ))
    plt.show()





