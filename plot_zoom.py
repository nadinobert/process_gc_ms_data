import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

def figure_zoom(dataset1, dataset2, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, Num_RT, tested_substrate):

    num_rows = dataset1.shape[0]

    if Num_RT.isnumeric():
        x1 = list(dataset1.iloc[:, 1])
        y1 = list(dataset1.iloc[:, 4])
        y1_err = list(dataset1.iloc[:, 5])
        x2 = list(dataset2.iloc[:, 1])
        y2 = list(dataset2.iloc[:, 4])
        y2_err = list(dataset2.iloc[:, 5])
    else:
        x1 = list(dataset1.iloc[:, 1])
        y1 = list(dataset1.iloc[:, 3])
        y1_err = list(dataset1.iloc[:, 4])
        x2 = list(dataset2.iloc[:, 1])
        y2 = list(dataset2.iloc[:, 3])
        y2_err = list(dataset2.iloc[:, 4])
        x3 = list(dataset1.iloc[:, 1])

    if MM == "D2O":
        equilibrium = equ_MMw_D2O
    elif MM == "H2O":
        equilibrium = equ_MMw_H2O

    y3 = [equilibrium] * num_rows

    fig, ax = plt.subplots()

    ax.errorbar(x1, y1, yerr=y1_err, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)   #plot the errorbar
    ax.plot(x1, y1, linewidth=0.6, color='blue')  #plot the simple line
    ax.scatter(x1, y1, marker='s', alpha=0.7, label='DD', color='blue')   #plot the datapoint dots
    #ax.errorbar(x2, y2, yerr=y2_err, marker='s', alpha=0.7, capsize=3, label='DD2')

    ax.plot(x1, y3, label='Equilibrium', color='green', linewidth=0.7, linestyle='--')
    ax.set_ylim(0, 1)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # create inset axes
    #axins = inset_axes(ax, width='30%', height='30%', loc='lower right')
    axins = ax.inset_axes([0.7, 0.1, 0.2, 0.2])         #first two numbers give the position in the plot, the second two numbers give the relative size

    axins.errorbar(x1, y1, yerr=y1_err, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)   #plot the errorbar
    axins.plot(x1, y1, linewidth=0.6, color='blue')  #plot the simple line
    axins.scatter(x1, y1, marker='s', alpha=0.7, label='DD', color='blue')      #plot the datapoint dots

    axins.set_xlim(-0.5, 3)     # location of subpart of the plot that should be zoomed in
    axins.set_ylim(0.17, 0.35)  # location of subpart of the plot that should be zoomed in
    axins.set_xticks(np.arange(0, 4, 1))
    # axins.scatter([2, 3], [4, 9], color='red', s=200)

    # mark the zoomed region
    mark_inset(ax, axins, loc1=2, loc2=3, fc="none", ec="0.5")


    # Set common labels for the figure
    fig.suptitle(
        experiment + '\n' + 'DD1, DD2 at RT ' + str(Num_RT) + '\n' + ' Mastermix w: ' + MM + ', ' + tested_substrate)
    fig.text(0.5, 0.04, 'Time [min]', ha='center', va='center')
    fig.text(0.06, 0.5, 'Deuterium Degree', ha='center', va='center', rotation='vertical')

    ax.legend(loc="upper left")

    return fig
