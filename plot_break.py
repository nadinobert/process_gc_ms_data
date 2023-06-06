from matplotlib import pyplot as plt

def figure_break(dataset1, dataset2, MM, equ_MMw_H2O, equ_MMw_D2O, experiment, Num_RT, tested_substrate):

    num_rows = dataset1.shape[0]

    #to distinguish between the plots for RT1, 2, 3 and all RT's, distinguish bewteen numeric for RT's and is not numeric for all RTs

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

    fig, (ax, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w', gridspec_kw={'width_ratios': [4, 1]})

    # plot the same data on both axes
    ax.errorbar(x1, y1, yerr=y1_err, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)  # plot the errorbar
    ax.plot(x1, y1, linewidth=0.6, color='blue')  # plot the simple line
    ax.scatter(x1, y1, marker='s', alpha=0.7, label='DD', color='blue')  # plot the datapoint dots
    ax2.errorbar(x1, y1, yerr=y1_err, marker='', capsize=3, capthick=0.5, ls='-', color='black', linewidth=0.5)  # plot the errorbar
    ax2.plot(x1, y1, linewidth=0.6, color='blue')  # plot the simple line
    ax2.scatter(x1, y1, marker='s', alpha=0.7, label='DD', color='blue')  # plot the datapoint dots

    #ax.errorbar(x2, y2, yerr=y2_err, marker='s', alpha=0.7, capsize=3, label='DD2')
    #ax2.errorbar(x2, y2, yerr=y2_err, marker='s', alpha=0.7, capsize=3, label='DD2')

    ax.plot(x1, y3, label='Equilibrium', color='green', linewidth=0.7, linestyle='--')
    ax2.plot(x1, y3, label='Equilibrium', color='green', linewidth=0.7, linestyle='--')

    # hide the spines between ax and ax2
    ax.spines['right'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.yaxis.set_visible(False)
    ax.yaxis.tick_left()
    ax.tick_params(axis='y', color='b')

    ax.set_xlim(0, 8.5)
    ax2.set_xlim(8.5, 62)

    ax.set_ylim(0, 1)
    ax2.set_ylim(0, 1)

    d = 0.01  # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((0.995, 1.005), (-d, +d), **kwargs)  # bottom left

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-0.02, 0.02), (-d, +d), **kwargs)  # bottom right

    # Set common labels for the figure
    fig.suptitle(experiment + '\n' + 'DD1, DD2 at RT ' + str(Num_RT) + '\n' + ' Mastermix w: ' + MM + ', ' + tested_substrate)
    fig.text(0.5, 0.04, 'Time [min]', ha='center', va='center')
    fig.text(0.06, 0.5, 'Deuterium Degree', ha='center', va='center', rotation='vertical')
    fig.subplots_adjust(wspace=0.025)

    ax.legend(loc="upper left")

    return fig
