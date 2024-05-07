import argparse
from pathlib import Path
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import requests
import cartopy.geodesic as cgeo

parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, help='Command to execute', choices=['elevation', 'success'])
parser.add_argument('data', type=str, help='Path to data directory')
parser.add_argument('--key', type=str, help='mapy.cz API key')
parser.add_argument('--relief', action='store_true', help='Plot relief instead of elevation')
parser.add_argument('--lines', action='store_true', help='Plot line of sight lines')
parser.add_argument('--only', type=str, help='Only process these stations, format "1,2,3"')
parser.add_argument('--no-show', action='store_true', help='Do not show the plot')
args = parser.parse_args()

DATA_BASE = Path(args.data)
OUT_BASE = Path('out')
CACHE = Path('cache.pkl')
RESOLUTION = 5 # meters
STATION_HEIGHTS = [0.19, 0.55, 0.82]
CAR_HEIGHT = 1.65
PLOT_MARGIN = 0.08

class ElevationCache:
    def __init__(self) -> None:
        if CACHE.exists():
            with open(CACHE, 'rb') as f:
                self.elvs = pickle.load(f)['elevations']
        else:
            self.elvs = {}

    def get(self, lat, lon):
        lat, lon = round(lat, 6), round(lon, 6)
        if (lat, lon) in self.elvs:
            return self.elvs[(lat, lon)]
        
        print(f'Getting elevation for {lat}, {lon}')
        url = f'https://api.mapy.cz/v1/elevation?apiKey={args.key}&positions={lon},{lat}'
        e = requests.get(url, timeout=60).json()['items'][0]['elevation']
        self.elvs[(lat, lon)] = e
        
        with open(CACHE, 'wb') as f:
            pickle.dump({'elevations': self.elvs}, f)

        return e

def main():
    OUT_BASE.mkdir(exist_ok=True)
    name = DATA_BASE.stem + ('-' + args.only if args.only else '') + ('-lines' if args.lines else '')
    # Load data
    data = pd.read_csv(DATA_BASE / 'locations.csv')
    if args.only:
        only = list(map(int, args.only.split(',')))
        only.append(0)
        data = data[data['i'].isin(only)]

    print(data)
    elevation = ElevationCache()
    ins = data['i']
    lats = data['lat']
    lons = data['lon']

    colors = np.concatenate([
        plt.colormaps["Dark2"](np.linspace(0, 1, 8)),
        plt.colormaps["Set1"](np.linspace(0, 1, 9))
    ])

    globe = cgeo.Geodesic()
    paths = {}
    gen = zip(ins, zip(lats, lons))
    base_i, (base_lat, base_lon) = next(gen)
    for i, (lat, lon) in gen:
        print(f'Processing {base_lat}, {base_lon} -> {lat}, {lon}')
        dist = float(globe.inverse((base_lon, base_lat), (lon, lat)).T[0][0])
        print(f'Distance: {dist}')

        ins_smooth = np.linspace(base_i, i, num=int(dist//RESOLUTION))
        lat_smooth = interp1d([base_i, i], [base_lat, lat])(ins_smooth)
        lon_smooth = interp1d([base_i, i], [base_lon, lon])(ins_smooth)

        elvs = [elevation.get(lat, lon) for lat, lon in zip(lat_smooth, lon_smooth)]
        dists = interp1d([base_i, i], [0, dist])(ins_smooth)
        paths[i] = (elvs, dists, lat, lon)

    if args.command == 'success':
        success = {i: {} for i in ins}
        for path in DATA_BASE.glob('*.csv'):
            if path.stem == 'locations':
                continue

            spot = int(path.stem.split('-')[0])
            node = int(path.stem.split('-')[1])
            print(f'Processing spot {spot} node {node}')
            success[spot]['spot'] = spot
            try:
                data = pd.read_csv(path)
                success[spot][node] = round(data['acked'].array[-1] / data['txed'].array[-1] * 100)
                #time = data['time'][-1]

            except pd.errors.EmptyDataError:
                success[spot][node] = 0

        success = pd.DataFrame.from_dict(success, orient='index')
        success.to_csv(OUT_BASE / f'success-{name}.csv', index_label='spot')
        latex_path = OUT_BASE / f'success-{name}.tex'
        latex = '\\begin{tabular}{|l|l|l|l|}\n'
        latex += '\\multicolumn{4}{c}{\\textbf{' + name.upper() + '}} \\\\ \\hline \n'
        header = ['\\textbf{Spot}'] + ['\\textbf{' + f'Node {i}' + '}' for i in success.columns if str(i).isdigit()]
        latex += ' & '.join(header) + ' \\\\ \\hline\n'
        for i, row in success.iterrows():
            latex += ' & '.join([str(row.values[0])] + [f'{v}\\%' for v in row.values[1:]]) + ' \\\\ \\hline\n'
        latex += '\\end{tabular}\n'
        #success.to_latex(latex_path, header=header, column_format='|l|' + 'l|' * len(success.columns), index=False)
        #latex = latex_path.read_text().replace('\\\\', '\\\\ \\hline')
        #latex = latex.replace('\\midrule', '').replace('toprule', 'hline').replace('\\bottomrule', '')
        latex_path.write_text(latex)

        fig, ax = plt.subplots(figsize=(9, 3))
        plt.grid(axis='y', zorder=0, linestyle='--')
        for i, (node, data) in enumerate(success.items()):
            if node == 'spot':
                continue
            dists = [0] + [p[1][-1] for p in paths.values()]
            #ax.plot(dists, data, label=f'Node {node}')
            ax.bar(np.arange(len(data)) + i * 0.2, data + 0.1, width=0.15, label=f'Node {node}', zorder=3, color=colors[i-1])

        ax.set_ylim(0, 100 * (1 + PLOT_MARGIN))
        ax.set_xticks(np.arange(len(data)) + 0.2)
        ax.set_xticklabels([round(d) for d in dists])
        ax.set_yticks([0, 25, 50, 75, 90, 95, 100])
        ax.margins(PLOT_MARGIN, PLOT_MARGIN)
        plt.xlabel('Transmitting distance [m]')
        plt.ylabel('Success rate [%]')
        plt.legend(loc='lower left')
        plt.tight_layout()
        plt.savefig(OUT_BASE / f'success-{name}.svg')
        if not args.no_show:
            plt.show()
        return

    # plot elevation
    if args.command == 'elevation':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3), width_ratios=[1, 2])

        #m = Basemap(ax=ax1, llcrnrlat=min(lats) - 0.01, urcrnrlat=max(lats) + 0.01, llcrnrlon=min(lons) - 0.01, urcrnrlon=max(lons) + 0.01, resolution='f')
        #m.shadedrelief()
        #m.bluemarble()
        for i, (spot, lat, lon) in enumerate(zip(ins, lats, lons)):
            color = 'black' if int(spot) == 0 else colors[spot-1]
            lat, lon = round(lat, 6), round(lon, 6)
            ax1.scatter(lon, lat, label=f'{spot}', color=color)
            ax1.text(lon, lat, f'{spot}')
            if args.lines:
                ax1.plot([lons[0], lon], [lats[0], lat], color=color, linestyle='--', alpha=0.5)

        ax1.set_xlabel('Longitude [°]')
        ax1.set_ylabel('Latitude [°]')
        ax1.ticklabel_format(useOffset=False)
        ax1.grid()
        ax1.margins(PLOT_MARGIN, PLOT_MARGIN)

        if args.relief:
            last_path = paths[max(paths.keys(), key=lambda p: len(paths[p][0]))][0]
            corr = np.linspace(last_path[0], last_path[-1], num=len(last_path))
        
        for h in STATION_HEIGHTS:
            ax2.scatter(0, (0 if args.relief else list(paths.values())[0][0][0]) + h, color='black', marker='+', s=150)
        
        for i, (spot, (elvs, dists, lat, lon)) in enumerate(paths.items()):
            if args.relief:
                elvs -= corr[:len(elvs)]
            
            color = 'black' if int(spot) == 0 else colors[spot-1]
            ax2.plot(dists, elvs, label=f'{spot}', color=color)
            ax2.axvline(dists[-1], color='grey', linestyle='--', alpha=0.5)

            if args.lines:
                for h in STATION_HEIGHTS:
                    ax2.plot([dists[0], dists[-1]], [elvs[0] + h, elvs[-1] + CAR_HEIGHT], color=color, linestyle='--', alpha=0.5)
        
        for i, (spot, (elvs, dists, lat, lon)) in enumerate(paths.items()):
            if args.relief:
                elvs -= corr[:len(elvs)]

            ax2.text(dists[-1] + 5, elvs[-1] + 0.1 + CAR_HEIGHT, f'{spot}')
            ax2.scatter(dists[-1], elvs[-1] + CAR_HEIGHT, color='black', marker='+', s=150)
            ax2.scatter(dists[-1], elvs[-1], color='black', marker='o', s=50)

        #ax2.legend(loc='upper left', ncols=3)
        ax2.set_xlabel('Transmitting distance [m]')
        ax2.set_ylabel('Relief' if args.relief else 'Elevation [m]')
        ax2.grid()
        ax2.margins(PLOT_MARGIN, PLOT_MARGIN)
        plt.tight_layout()
        plt.savefig(OUT_BASE / f'{"relief" if args.relief else "elevation"}-{name}.svg')
        if not args.no_show:
            plt.show()
        return


if __name__ == '__main__':
    main()
