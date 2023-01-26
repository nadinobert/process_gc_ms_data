import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

def figure_zoom(DD1, DD2, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, Num_RT, tested_substrate):

    num_rows = DD1.shape[0]

    if Num_RT.isnumeric():
        x1 = list(DD1.iloc[:, 1])
        y1 = list(DD1.iloc[:, 4])
        y1_err = list(DD1.iloc[:, 5])
        x2 = list(DD2.iloc[:, 1])
        y2 = list(DD2.iloc[:, 4])
        y2_err = list(DD2.iloc[:, 5])
    else:
        x1 = list(DD1.iloc[:, 1])
        y1 = list(DD1.iloc[:, 3])
        y1_err = list(DD1.iloc[:, 4])
        x2 = list(DD2.iloc[:, 1])
        y2 = list(DD2.iloc[:, 3])
        y2_err = list(DD2.iloc[:, 4])
        x3 = list(DD1.iloc[:, 1])

    if MM == "D2O":
        equilibrium = equ_MMw_D2O
    elif MM == "H2O":
        equilibrium = equ_MMw_H2O

    y3 = [equilibrium] * num_rows

    fig, ax = plt.subplots()
    ax.errorbar(x1, y1, yerr=y1_err, marker='s', alpha=0.7, capsize=3, label='DD1')
    #ax.errorbar(x2, y2, yerr=y2_err, marker='s', alpha=0.7, capsize=3, label='DD2')

    ax.plot(x1, y3, label='Equilibrium', color='grey')

    # create inset axes
    axins = inset_axes(ax, width='30%', height='30%', loc='center right')
    axins.plot([1, 2], [1, 4])
    axins.set_xlim(1, 1.25)  # gives the subpart of the plot that should be zoomed in
    axins.set_ylim(0, 2)  # gives the subpart of the plot that should be zoomed in
    # axins.scatter([2, 3], [4, 9], color='red', s=200)

    # mark the zoomed region
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")


    # Set common labels for the figure
    fig.suptitle(
        experiment + '\n' + 'DD1, DD2 at RT ' + str(Num_RT) + '\n' + ' Mastermix w: ' + MM + ', ' + tested_substrate)
    fig.text(0.5, 0.04, 'Time [min]', ha='center', va='center')
    fig.text(0.06, 0.5, 'Deuterium Degree', ha='center', va='center', rotation='vertical')

    ax.legend(loc="upper left")

    return fig
