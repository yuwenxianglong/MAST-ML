import os.path
import itertools

import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure, figaspect
from matplotlib.ticker import MaxNLocator

def make_plots(runs, is_classification, outdir):
    paths = []
    # sort the runs by their score on the first test metric
    #import pdb; pdb.set_trace()
    runs = sorted(runs, key=lambda run: run['test_metrics'][0][1])
    for run,name in [(runs[0],'worst_run'), (runs[len(runs)//2], 'median_run'), (runs[-1], 'best_run')]:
        savepath = os.path.join(outdir, run['normalizer'].__class__.__name__,
                                        run['selector'].__class__.__name__,
                                        run['model'].__class__.__name__,
                                        run['split'].__class__.__name__,
                                        run['normalizer'].__class__.__name__,

                f"_split_{run['split']}" +
                                        f"_normalizer_{run['normalizer']}" +
                                        f"_selector_{run['selector']}" +
                                        f"_model_{run['model']}.png")
        paths.append(savepath)
        # Ordered Dict to preserve original user-specified statistics ordering:
        y_true, y_pred, stats = run['test_true'], run['test_pred'], run['test_metrics']
        if is_classification:
            plot_confusion_matrix(y_true, y_pred, savepath, stats, title=name)
        else: # is_regression
            plot_predicted_vs_true(y_true, y_pred, savepath, stats, title=name)
            plot_residuals_histogram(y_true, y_pred, savepath, stats, title=name)
    return paths

def plot_confusion_matrix(y_true, y_pred, savepath, stats, normalize=False, title='Confusion matrix',
        cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    """
    # calculate confusion matrix and lables in correct order
    cm = confusion_matrix(y_true, y_pred)
    classes = sorted(list(set(y_true).intersection(set(y_pred))))

    # initializae fig
    # set image aspect ratio. Needs to be wide enough or plot will shrink really skinny
    w, h = figaspect(0.7)
    fig = Figure(figsize=(w,h))
    FigureCanvas(fig)

    # these two lines are where the magic happens, trapping the figure on the left side
    # so we can make print text beside it
    gs = plt.GridSpec(2, 3)
    ax = fig.add_subplot(gs[0:2, 0:2], aspect='equal')
    FigureCanvas(fig)

    ax.set_title(title)

    # create the colorbar, not really needed but everyones got 'em
    mappable = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    fig.colorbar(mappable)

    # set x and y ticks to labels
    tick_marks = range(len(classes))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(classes, rotation='vertical', fontsize=18)

    ax.set_yticks(tick_marks)
    ax.set_yticklabels(classes, rotation='vertical', fontsize=18)

    # draw number in the boxes
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")


    # print stats onto the image. Goes off screen if they are too long or too many in number
    text_height = 0.08
    for i, (name, val) in enumerate(stats):
        y_pos = 1 - (text_height * i + 0.1)
        fig.text(0.7, y_pos, f'{name}: {val}')

    #plt.tight_layout()
    ax.set_ylabel('True label')
    ax.set_xlabel('Predicted label')
    fig.savefig(savepath)

# using OO interface from https://matplotlib.org/gallery/api/agg_oo_sgskip.html
def plot_predicted_vs_true(y_true, y_pred, savepath, stats, title='predicted vs true'):
    # set image aspect ratio. Needs to be wide enough or plot will shrink really skinny
    w, h = figaspect(0.7)
    fig = Figure(figsize=(w,h))
    FigureCanvas(fig)

    # these two lines are where the magic happens, trapping the figure on the left side
    # so we can make print text beside it
    gs = plt.GridSpec(2, 3)
    ax = fig.add_subplot(gs[0:2, 0:2], aspect='equal')

    ax.set_title(title)

    # do the actual plotting
    ax.scatter(y_true, y_pred, edgecolors=(0, 0, 0))
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'k--', lw=4)

    # set axis labels
    ax.set_xlabel('Measured')
    ax.set_ylabel('Predicted')

    # print stats onto the image. Goes off screen if they are too long or too many in number
    text_height = 0.08
    for i, (name, val) in enumerate(stats):
        y_pos = 1 - (text_height * i + 0.1)
        fig.text(0.7, y_pos, f'{name}: {val}')


    fig.savefig(savepath)

def plot_residuals_histogram(y_true, y_pred, savepath, stats, title='residuals histogram'):

    # make the aspect ration wide for text next to square-ish graph
    w, h = figaspect(0.7)

    fig = Figure(figsize=(w,h))
    FigureCanvas(fig)

    # these two lines are where the magic happens, trapping the figure on the left side
    # so we can make print text beside it
    gs = plt.GridSpec(2, 3)
    ax = fig.add_subplot(gs[0:2, 0:2], aspect='equal')


    ax.set_title(title)
    # do the actual plotting
    residuals = y_true - y_pred
    ax.hist(residuals, bins=30)

    # normal text stuff
    ax.set_xlabel('residual')
    ax.set_ylabel('frequency')

    # make y axis ints, because it is discrete
    #ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # shrink those margins
    fig.tight_layout()

    # print stats onto the image. Goes off screen if they are too long or too many in number
    text_height = 0.08
    for i, (name, val) in enumerate(stats):
        y_pos = 1 - (text_height * i + 0.1)
        fig.text(0.7, y_pos, f'{name}: {val}')

    fig.savefig(savepath)
