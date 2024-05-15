import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from scipy import signal

OUT_BASE = Path('out')
TIME_FORMAT = '%y-%m-%d %H:%M.%S'
DATE_FORMATTER = DateFormatter('%d.%m %Hh')
SAMPLING_RATE = 15/60 # every 15 seconds
BATTERY_VOLTAGE_MAX = 4.2 # V
BATTERY_VOLTAGE_MIN = 3.35 # V
BATTERY_VOLTAGE_EMPTY = 2.8 # V
BATTERY_CAPACITY = 0.300 # Ah
BATTERY_CAPACITY_EMPTY = 0.030 # Ah

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
        fig, (ax, ax_ledend) = plt.subplots(1, 2, figsize=(9, 6), width_ratios=[5, 1])

        indexes = [0]
        indexes.extend(np.where(data.index.diff() > pd.Timedelta(minutes=15))[0])
        indexes.append(len(data)-1)
        print(indexes)
        value_max, value_min = 650, 250
        
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
            ax.text(d1.index[-1] + pd.Timedelta(minutes=15), 600, 'No data', rotation=90, color='0.2')

        watered = data[data.index == pd.to_datetime('24-05-12 10:10.03', format=TIME_FORMAT)].index
        ax.axvline(watered, color='0.2', linestyle='--', linewidth=1.5)
        ax.text(watered + pd.Timedelta(minutes=15), 600, 'Watered', rotation=90, color='0.2')
        ax.get_legend().remove()
        ax.set_ylim(value_min, value_max)
        ax.grid(axis='y')
        ax.set_ylabel('Rise time of the zone capacitor voltage [$\\mu$s]')
        ax.set_xlabel('Time')
        ax.xaxis.set_major_formatter(DATE_FORMATTER)

        ax_ledend.axis('off')
        ax_ledend.imshow(plt.imread('../../boards/sensor/zones-sharp.png'))

        fig.autofmt_xdate()
        plt.tight_layout()
        plt.savefig(OUT_BASE / f'{name}.svg')
        if not args.no_show:
            plt.show()

    elif args.command == 'power':
        data = pd.read_csv('power_log.csv')
        data['time'] = pd.to_datetime(data['time'], format=TIME_FORMAT)
        data.set_index('time', inplace=True)
        data.pop('current')
        data = data.iloc[400:]
        data['voltage'] = data[data['voltage'] > BATTERY_VOLTAGE_EMPTY]['voltage']
        data['voltage'] = data['voltage'].apply(average, window=20, by_row=False)
        fig, ax = plt.subplots(figsize=(9, 3))

        start = data[data.index == pd.to_datetime('24-05-11 18:30.03', format=TIME_FORMAT)].index[0]
        print(start)
        prev = data['voltage'].iloc[0]
        delta = pd.Timedelta(minutes=60)
        power = []
        while start < data.index[-1]:
            end = start + delta
            new = data[start:end]['voltage'].mean()
            diff = new - prev

            if diff > 0 and prev > BATTERY_VOLTAGE_EMPTY:
                if new > BATTERY_VOLTAGE_MIN:
                    charge = diff / (BATTERY_VOLTAGE_MAX - BATTERY_VOLTAGE_MIN) * BATTERY_CAPACITY
                else:
                    charge = diff / (BATTERY_VOLTAGE_MIN - BATTERY_VOLTAGE_EMPTY) * BATTERY_CAPACITY_EMPTY
                charge /= ((end - start).seconds / 3600)
                charge *= 1000 * new
                if charge > 9:
                    power.append((start, charge))
            
            start = end
            prev = new

        power = np.array(power).T
        ax.bar(power[0], power[1], width=delta, color='orange', zorder=3)
        ax.set_ylabel('Battery charging power [mW/h]')
        ax.set_xlabel('Time')
        
        ax2 = ax.twinx()
        data.plot(ax=ax2, color='black', legend=True, zorder=1)
        ax2.get_legend().remove()
        ax2.set_ylabel('Battery voltage [V]')
        ax2.grid(zorder=0)
        ax2.xaxis.set_major_formatter(DATE_FORMATTER)

        fig.autofmt_xdate()
        plt.tight_layout()
        plt.savefig(OUT_BASE / f'{name}.svg')
        if not args.no_show:
            plt.show()


if __name__ == '__main__':
    main()
