"""
Script for generating training history plot
"""

from stable_baselines3.common.logger import Figure
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib import rc
from argparse import ArgumentParser
import sys


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--log', metavar='--l', type=str, nargs='?',
                        help="which model history to plot (e.g., '/path/to/history/sb3_log_180822/progress.csv'.")
    ret = parser.parse_args(sys.argv[1:])
    print(ret)

    data = pd.read_csv(ret.log)

    # set plot config
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})  # , 'size': 16})

    # load history and make plot
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(list(range(len(data["rollout/ep_len_mean"]))), data["rollout/ep_len_mean"])
    ax[0].set_title("Number of actions before game is done")
    ax[0].grid("on")
    ax[1].plot(list(range(len(data["rollout/ep_rew_mean"]))), data["rollout/ep_rew_mean"])
    ax[1].set_title("Number of wins in 100 games")
    ax[1].grid("on")
    plt.tight_layout()
    plt.show()
