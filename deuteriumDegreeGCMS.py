import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from cleanup import cleanup

# experiment needs to be the name of the folder containing all sample folders
experiment = '20220919'
testes_substrate = 'TBP'
equilibrium = 0.5

if testes_substrate == 'TBP':
    ion_types = {250: 'DD1', 251: 'DD1', 252: 'DD2', 253: 'DD2'}
    linenums = [i for i in range(21, 33)]       #linenums represents the rows in the text file with related data
if testes_substrate == 'TCP':
    ion_types = {162: 'DD1', 163: 'DD1', 164: 'DD2', 165: 'DD2'}
    linenums = [i for i in range(21, 29)]

directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

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
                    k=1
                    a=0
                    for i, ln in enumerate(data):
                        if i in linenums:
                            new = ln.split(" ")
                            ion = (list(filter(lambda x: x != '', new))[1]).split('_')[1]
                            peakarea = (list(filter(lambda x: x != '', new))[4])
                            RT = (list(filter(lambda x: x != '', new))[1]).split('_')[2]
                            try:
                                peakarea = float(peakarea)
                            except Exception:
                                peakarea = np.nan
                            if k % 2 == 1:
                                a = peakarea
                            else:
                                quotient = peakarea / (a + peakarea)
                                if not np.isnan(quotient):
                                    results = results.append(
                                    {'Mastermix_with': mastermix, 'timepoint_[min]': time, 'replicate': replicate,
                                     'ion': int(ion), 'quotient': quotient, 'RT': RT}, ignore_index=True)
                            k = k + 1

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

print(results)

#calc df contains data for fiure 1, 2 and 3
#calc2 df contains data for figure 4
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

# for every MM approach
# figure 1, 2, 3: DD1 and DD2 at RT1, RT2, RT3
# figure 4: DD1 and DD2 average of all RT's
for MM in condition:
    for x in RTs:
        calc_DD1_RT = calc_DD1.loc[(calc_DD1['RT'] == str(x)) & (calc_DD1['Mastermix_with'] == MM)]
        calc_DD2_RT = calc_DD2.loc[(calc_DD2['RT'] == str(x)) & (calc_DD2['Mastermix_with'] == MM)]

        x1 = list(calc_DD1_RT.iloc[:, 1])
        y1 = list(calc_DD1_RT.iloc[:, 4])
        y1_err = list(calc_DD1_RT.iloc[:, 5])
        x2 = list(calc_DD2_RT.iloc[:, 1])
        y2 = list(calc_DD2_RT.iloc[:, 4])
        y2_err = list(calc_DD2_RT.iloc[:, 5])
        x3 = [*range(0, 61, 1)]
        y3 = [equilibrium] * 61

        plt.errorbar(x1, y1, yerr=y1_err, marker='s', alpha=0.7, capsize=10, label='DD1')
        plt.errorbar(x2, y2, yerr=y2_err, marker='s', alpha=0.7, capsize=10, label='DD2')
        plt.plot(x3, y3, label='Equilibrium')
        plt.title(experiment + '\n' + 'DD1, DD2 at RT ' + str(x) + '\n' + ' Mastermix w: ' + MM + ', ' + testes_substrate)
        plt.xlabel('time [min]')
        plt.ylabel('Deuterium Degree')
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(x)) + MM)
        plt.show()

    #figure 4: AVG(DD1, DD2)
    calc_MW_DD1 = calc_MW.loc[(calc_MW['ion_type'] == 'DD1') & (calc_MW['Mastermix_with'] == MM)]
    calc_MW_DD2 = calc_MW.loc[(calc_MW['ion_type'] == 'DD2') & (calc_MW['Mastermix_with'] == MM)]

    x1 = list(calc_MW_DD1.iloc[:, 1])
    y1 = list(calc_MW_DD1.iloc[:, 3])
    y1_err = list(calc_MW_DD1.iloc[:, 4])
    x2 = list(calc_MW_DD2.iloc[:, 1])
    y2 = list(calc_MW_DD2.iloc[:, 3])
    y2_err = list(calc_MW_DD2.iloc[:, 4])
    x3 = [*range(0, 61, 1)]
    y3 = [equilibrium] * 61

    plt.errorbar(x1, y1, y1_err, marker='s', alpha=0.7, capsize=10, label='DD1')
    plt.errorbar(x2, y2, y2_err,marker='s', alpha=0.7, capsize=10,  label='DD2')
    plt.plot(x3, y3, label='Equilibrium')
    plt.title(experiment + '\n' + 'DD1, DD2 all RTs ' + '\n' + ' Mastermix w: ' + MM + ', ' + testes_substrate)
    plt.xlabel('time [min]')
    plt.ylabel('Deuterium Degree')
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'MW' + MM))
    plt.show()


def calc_mean_std(x):
    d = {}
    d['new_mean'] = (x['quotient']['mean'] * x['quotient']['count']).sum() / x['quotient']['count'].sum()
    d['new_std'] = ((x['quotient']['mean'] * x['quotient']['count']).sum() / x['quotient']['count'].sum()).std()
    return pd.Series(d, index=['new_mean', 'new_std'])





