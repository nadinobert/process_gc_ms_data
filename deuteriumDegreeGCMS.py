import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# experiment needs to be the name of the folder containing all sample folders
experiment = '20220907'
testes_substrate = 'TBP'

if testes_substrate == 'TBP':
    ion_types = {250: 'DD1', 252: 'DD2', 251: 'DD1', 253: 'DD2'}
if testes_substrate == 'TCP':
    'was anderes'

directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

# gives a list with all directories in my target/experiment folder
samples = os.listdir(directory)


if testes_substrate == 'TBP':
    linenums = [i for i in range(21, 33)]
elif testes_substrate == 'TCP':
    linenums = [i for i in range(21, 31)]

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


calc = results.groupby(['Mastermix_with', 'timepoint_[min]', 'RT', 'ion_type']).quotient.agg('mean')
calc = calc.reset_index()
NCC = calc[(calc['timepoint_[min]'] == 'NCC')].index
calc.drop(NCC, inplace=True)
NSC = calc[(calc['timepoint_[min]'] == 'NSC')].index
calc.drop(NSC, inplace=True)
calc.sort_values(by=['timepoint_[min]'])

# selects all data of calculated DD1 and DD2
calc_DD1 = calc.loc[calc['ion_type'] == 'DD1']
calc_DD2 = calc.loc[calc['ion_type'] == 'DD2']
condition = pd.unique(results['Mastermix_with'])

# for every MM approach
# figure 1, 2, 3: DD1, DD2 at RT1, RT2, RT3
# figure 4: DD1 and DD2 for average of all RT's
for MM in condition:
    for x in range(1, 4):
        calc_DD1_RT = calc_DD1.loc[(calc_DD1['RT'] == str(x)) & (calc_DD1['Mastermix_with'] == MM)]
        calc_DD2_RT = calc_DD2.loc[(calc_DD2['RT'] == str(x)) & (calc_DD2['Mastermix_with'] == MM)]

        x1 = list(calc_DD1_RT.iloc[:, 1])
        y1 = list(calc_DD1_RT.iloc[:, 4])
        x2 = list(calc_DD2_RT.iloc[:, 1])
        y2 = list(calc_DD2_RT.iloc[:, 4])

        plt.plot(x1, y1, label='DD1')
        plt.plot(x2, y2, label='DD2')
        plt.title('DD1, DD2 at RT ' + str(x) + ' Mastermix w: ' + MM + ', ' + experiment + ', ' + testes_substrate)
        plt.xlabel('time [min]')
        plt.ylabel('Deuterium Degree')
        plt.legend(loc="upper right")
        plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, str(x)) + MM)
        plt.show()

    #figure 4: AVG(DD1, DD2)
    calc_MW = calc.groupby(['Mastermix_with', 'timepoint_[min]', 'ion_type']).quotient.agg('mean')
    calc_MW = calc_MW.reset_index()

    calc_MW_DD1 = calc_MW.loc[(calc_MW['ion_type'] == 'DD1') & (calc_MW['Mastermix_with'] == MM)]
    calc_MW_DD2 = calc_MW.loc[(calc_MW['ion_type'] == 'DD2') & (calc_MW['Mastermix_with'] == MM)]

    x1 = list(calc_MW_DD1.iloc[:, 1])
    y1 = list(calc_MW_DD1.iloc[:, 3])
    x2 = list(calc_MW_DD2.iloc[:, 1])
    y2 = list(calc_MW_DD2.iloc[:, 3])

    plt.plot(x1, y1, label='DD1')
    plt.plot(x2, y2, label='DD2')
    plt.title('DD1, DD2 all RTs ' + ' Mastermix w: ' + MM + ', ' + experiment + ', ' + testes_substrate)
    plt.xlabel('time [min]')
    plt.ylabel('Deuterium Degree')
    plt.legend(loc="upper right")
    plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, 'MW' + MM))
    plt.show()



