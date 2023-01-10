import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from cleanup import cleanup

#TODO delete RT2 (11.1 min) in approaches with TBP substrate -> unsure what sis is
#TODO compress back equilibrium part on x-axis
#TODO: set up function for plotting
#TODO: find a better way to define y-axis-range

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


# set font globally to times new roman
plt.rcParams["font.family"] = "Times New Roman"

# experiment needs to be the name of the folder containing all sample folders
# experiments with DD calc for puplication: 20221102 20220919 20220308_practical_course_DBT

experiment = '20220309'
testes_substrate = 'TeBB'
equilibrium_H2O = 0.16
equilibrium_D2O = 0.791

if testes_substrate == 'TBP':
    ion_types = {250: 'DD1', 251: 'DD1', 252: 'DD2', 253: 'DD2'}
    linenums = range(21, 33)      #linenums represents the rows in the text file with related data
if testes_substrate == 'TCP':
    ion_types = {162: 'DD1', 163: 'DD1', 164: 'DD2', 165: 'DD2'}
    linenums = range(21, 29)
if testes_substrate == 'TeBB':
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
for i in results.index:
    time = results.loc[i, 'timepoint_[min]']
    if time == 'NCC' or time == 'NSC':
        continue
    newtime = re.findall('(\d+)', time)[0]
    unit = re.findall("[a-zA-Z]+", time)[0]
    if unit == 's' or unit == 'sec':
        newtime = int(newtime) / 60
        newtime = ("%.2f" % newtime)                # keep only 2 digits after dot
    results.loc[i, 'timepoint_[min]'] = float(newtime)

results = results.loc[(results['timepoint_[min]'] != 'NCC') & (results['timepoint_[min]'] != 'NSC')]
print(results)

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
# figure 4: DD1 and DD2 average of all RT's
for MM in condition:
    for x in RTs:
        calc_DD1_RT = calc_DD1.loc[(calc_DD1['RT'] == str(x)) & (calc_DD1['Mastermix_with'] == MM)]
        calc_DD2_RT = calc_DD2.loc[(calc_DD2['RT'] == str(x)) & (calc_DD2['Mastermix_with'] == MM)]

        num_rows = calc_DD1_RT.shape[0]

        x1 = list(calc_DD1_RT.iloc[:, 1])
        y1 = list(calc_DD1_RT.iloc[:, 4])
        y1_err = list(calc_DD1_RT.iloc[:, 5])
        #x2 = list(calc_DD2_RT.iloc[:, 1])
        #y2 = list(calc_DD2_RT.iloc[:, 4])
        #y2_err = list(calc_DD2_RT.iloc[:, 5])
        x3 = list(calc_DD1_RT.iloc[:, 1])

        if MM == "D2O":
            equilibrium = equilibrium_D2O
        elif MM == "H2O":
            equilibrium = equilibrium_H2O

        y3 = [equilibrium] * num_rows

        #decompres x-axis labels
        #timepoints_square = ([5-(5/(number**2+1))  for number in x1])
        #timepoints_shift = [0.17*7, 0.33*8, 0.5*9, 1.0*6, 2.0*4, 5.0*3, 15*1.5, 45]
        #plt.xticks(timepoints_shift, x1, rotation=50)

        #plot as line graph
        plt.errorbar(x1, y1, yerr=y1_err, marker='s', alpha=0.7, capsize=3, label='DD1')
        #plt.errorbar(x2, y2, yerr=y2_err, marker='s', alpha=0.7, capsize=3, label='DD2')
        plt.plot(x1, y3, label='Equilibrium')

        plt.title(experiment + '\n' + 'DD1, DD2 at RT ' + str(x) + '\n' + ' Mastermix w: ' + MM + ', ' + testes_substrate)
        plt.xlabel('Time [min]')
        plt.ylabel('Deuterium Degree')
        plt.ylim(0, equilibrium + 0.2)
        plt.legend(loc="upper right")
        plt.tight_layout()
        pltname = str(experiment + str(x) + MM)
        #plt.savefig(pltname + '.svg')
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(x)) + MM)
        plt.show()

    #figure 4: AVG(DD1, DD2)
    calc_MW_DD1 = calc_MW.loc[(calc_MW['ion_type'] == 'DD1') & (calc_MW['Mastermix_with'] == MM)]
    calc_MW_DD2 = calc_MW.loc[(calc_MW['ion_type'] == 'DD2') & (calc_MW['Mastermix_with'] == MM)]

    num_rows = calc_MW_DD1.shape[0]

    x1 = list(calc_MW_DD1.iloc[:, 1])
    y1 = list(calc_MW_DD1.iloc[:, 3])
    y1_err = list(calc_MW_DD1.iloc[:, 4])
    #x2 = list(calc_MW_DD2.iloc[:, 1])
    #y2 = list(calc_MW_DD2.iloc[:, 3])
    #y2_err = list(calc_MW_DD2.iloc[:, 4])
    x3 = list(calc_MW_DD1.iloc[:, 1])
    y3 = [equilibrium] * num_rows

    plt.errorbar(x1, y1, y1_err, marker='s', alpha=0.7, capsize=2, label='DD1')
    #plt.errorbar(x2, y2, y2_err,marker='s', alpha=0.7, capsize=2,  label='DD2')
    plt.plot(x3, y3, label='Equilibrium')
    plt.title(experiment + '\n' + 'DD1, DD2 all RTs ' + '\n' + ' Mastermix w: ' + MM + ', ' + testes_substrate)
    plt.xlabel('Time [min]')
    plt.ylabel('Deuterium Degree')
    plt.ylim(0, equilibrium + 0.2)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'MW' + MM ))
    plt.show()






