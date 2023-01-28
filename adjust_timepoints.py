# this function translates s and min values to min values only
# only the last to digits after the dot will be kept

import re

def adjust_timepoints(results):
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
