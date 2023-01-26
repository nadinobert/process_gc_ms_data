import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

def figure_simple(DD1, DD2, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, Num_RT, tested_substrate):

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
    ax.set_ylim(0, 1)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Set common labels for the figure
    fig.suptitle(
        experiment + '\n' + 'DD1, DD2 at RT ' + str(Num_RT) + '\n' + ' Mastermix w: ' + MM + ', ' + tested_substrate)
    fig.text(0.5, 0.04, 'Time [min]', ha='center', va='center')
    fig.text(0.06, 0.5, 'Deuterium Degree', ha='center', va='center', rotation='vertical')

    ax.legend(loc="upper left")

    return fig
