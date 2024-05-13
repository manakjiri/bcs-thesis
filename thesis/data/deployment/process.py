import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, ndimage

OUT_BASE = Path('out')
TIME_FORMAT = '%y-%m-%d %H:%M.%S'
SAMPLING_RATE = 15/60

def average(data: pd.Series, window: int):
    ret = np.zeros_like(data)
    for i in range(len(data)):
        start = max(0, i - window)
        ret[i] = np.mean(data[start:i+1])
    return ret

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, help='Command to execute', choices=['moisture', 'power'])
    parser.add_argument('--no-show', action='store_true', help='Do not show the plot')
    args = parser.parse_args()

    OUT_BASE.mkdir(exist_ok=True)
    name = args.command

    colors = np.concatenate([
        plt.colormaps["Dark2"](np.linspace(0, 1, 8)),
        plt.colormaps["Set1"](np.linspace(0, 1, 9))
    ])

    if args.command == 'moisture':
        data = pd.read_csv('sensor_log.csv')
        data['time'] = pd.to_datetime(data['time'], format=TIME_FORMAT)
        data.set_index('time', inplace=True)
        fig, (ax, ax_ledend) = plt.subplots(1, 2, figsize=(10, 7), width_ratios=[5, 1])

        indexes = [0]
        indexes.extend(np.where(data.index.diff() > pd.Timedelta(minutes=15))[0])
        indexes.append(len(data)-1)
        print(indexes)
        value_max, value_min = 650, 200
        
        for i in range(len(indexes) - 1):
            d = data.iloc[indexes[i]:indexes[i+1]]

            #d.plot(ax=ax, alpha=0.1, color=colors)
            
            #filtered = d.apply(average, window=4*45)
            filtered = d.apply(signal.savgol_filter, window_length=4*60, polyorder=2, mode='nearest')
            #sos = signal.butter(2, 1/3600, 'low', fs=SAMPLING_RATE, output='sos')
            #filtered = data.apply(lambda x: signal.sosfilt(sos, x))
            #filtered = data.apply(average, window=4*15)
            filtered.plot(ax=ax, color=colors)

        for i in range(0, len(indexes) - 2):
            d1 = data.iloc[indexes[i]:indexes[i+1]]
            d2 = data.iloc[indexes[i+1]:indexes[i+2]]
            ax.fill_betweenx([value_min,value_max], d1.index[-1], d2.index[0], color='0.95', hatch='/', edgecolor='0.8', linewidth=1)

        ax.get_legend().remove()
        ax.set_ylim(value_min, value_max)
        ax.grid(axis='y')
        ax.set_ylabel('Rise time of the zone capacitor voltage [us]')

        ax_ledend.axis('off')
        ax_ledend.imshow(plt.imread('../../boards/sensor/zones.png'))

        plt.tight_layout()
        plt.savefig(OUT_BASE / f'{name}.svg')
        if not args.no_show:
            plt.show()


if __name__ == '__main__':
    main()
