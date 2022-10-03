import re
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

## process data (peak area) from gc-ms device

# TODO wann sollte mittelwert gebildet werden, wann median oder ähnliches verwendet werden?

# experiment needs to be the name of the folder containing all sample folders
experiment = '20220907'
testes_substrate = 'TBP'
num_ions = 4
peaks = 3

directory = os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment)

# gives a list with all directories in my target/experiment folder
samples = os.listdir(directory)

if testes_substrate == 'TBP':
    linenums = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                32]  # altes file geht bis line 26, neus file hat mehr ionen bis line 32
elif testes_substrate == 'TCP':
    linenums = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

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
                        if i in linenums:
                            new = ln.split(" ")
                            ion = (list(filter(lambda x: x != '', new))[1]).split('_')[1]
                            peakarea = (list(filter(lambda x: x != '', new))[4])
                            results = results.append(
                                {'Mastermix with': mastermix, 'timepoint [min]': time, 'replicate': replicate,
                                 'ion [m/z]': ion, 'peakarea': peakarea}, ignore_index=True)

# adjust the timepoints to [min] as unit
for i in results.index:
    time = results.loc[i, 'timepoint [min]']
    if time == 'NCC' or time == 'NSC':
        continue
    newtime = re.findall('(\d+)', time)[0]
    unit = re.findall("[a-zA-Z]+", time)[0]
    if unit == 's' or unit == 'sec':
        newtime = int(newtime) / 60
    results.loc[i, 'timepoint [min]'] = str(newtime)

#print(results)

condition = pd.unique(results['Mastermix with'])
stop_time = pd.unique(results['timepoint [min]'])
replicates = pd.unique(results['replicate'])
single_ions = pd.unique(results['ion [m/z]']) #evt wieder als int .asint oder so machen?

# iter through every single timepoint result
# calculate the DD
for mastermix_condition in condition:
    DeuteriumDegree = pd.DataFrame()
    for time in stop_time:
        # while repl increases, fill the lists/df
        single_result = results.loc[
            (results['Mastermix with'].eq(mastermix_condition)) & (results['timepoint [min]'].eq(time)), ['ion [m/z]', 'peakarea', 'replicate']]
        single_result = single_result.replace('N.D.', np.nan)
        single_result = single_result.apply(pd.to_numeric)
        #print(type(single_result))
        # wenn die anzahl der zeilen nur 1 replikat entspricht, dann, wenn drei replika in single result, dann was anderes
        if len(single_result.index) == num_ions * peaks * 3:
            single_result['peak'] = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
            print(single_result)
        else:
            single_result['peak'] = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
            print(single_result)
        for peak in range(1, 4):
            DD1_col = []
            DD2_col = []
            for repl in range(1, 4):
                peakarea_array = []
                for ion in single_ions:
                    peakarea = single_result.loc[(single_result['ion [m/z]'] == int(ion)) & (single_result['peak'] == peak) & (single_result['replicate'] == repl)]
                    try:
                        peakarea = int(peakarea['peakarea'])
                        peakarea_array.append(peakarea)
                    except Exception:
                        peakarea_array.append(np.nan)
                DD1 = peakarea_array[1] / (peakarea_array[1] + peakarea_array[0])
                DD2 = peakarea_array[3] / (peakarea_array[3] + peakarea_array[2])
                DD1_col.append(DD1)
                DD2_col.append(DD2)
            DDs = [np.mean(DD1_col), np.mean(DD2_col)]
            DeuteriumDegree[time] = [np.mean(DD1_col), np.mean(DD2_col)]
    print(DeuteriumDegree)
    # create plot
    # get rid of non numeric entries NCC and NSC
DeuteriumDegree = DeuteriumDegree.drop(['NCC', 'NSC'], axis=1)
#print(DeuteriumDegree.dtypes)
headerlist = list(DeuteriumDegree.columns.values)
headerlist = sorted([float(x) for x in headerlist])     #die drecks headerlist wird in floats umgewandelt und sortiert
DeuteriumDegree.columns = headerlist                    #die neude headerlist kommt auf den kack frame
x = list(DeuteriumDegree.columns)
y1 = DeuteriumDegree.iloc[0].tolist()
y2 = DeuteriumDegree.iloc[1].tolist()
plt.plot(x, y1, x, y2)
plt.title('Mastermix w: '+ condition + ', ' + experiment + ', tested on: ' + testes_substrate)
plt.savefig(os.path.join(r'C:\Users\hellmold\Nextcloud\Experiments\Activity_Assay_GC_MS', experiment, condition[0]))
plt.show()
