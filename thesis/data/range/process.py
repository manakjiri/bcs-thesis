import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import argparse
from pathlib import Path
import pickle
import requests
import cartopy.geodesic as cgeo

def get_elevation(lat, lon):
    lat, lon = round(lat, 6), round(lon, 6)
    if CACHE.exists():
        with open(CACHE, 'rb') as f:
            elvs = pickle.load(f)['elevations']
    else:
        elvs = {}
    
    if (lat, lon) in elvs:
        return elvs[(lat, lon)]
    
    print(f'Getting elevation for {lat}, {lon}')
    url = f'https://api.mapy.cz/v1/elevation?apiKey={args.key}&positions={lon},{lat}'
    e = requests.get(url, timeout=60).json()['items'][0]['elevation']
    elvs[(lat, lon)] = e
    
    with open(CACHE, 'wb') as f:
        pickle.dump({'elevations': elvs}, f)

    return e


parser = argparse.ArgumentParser()
parser.add_argument('data', type=str, help='Path to data directory')
parser.add_argument('--key', type=str, help='mapy.cz API key')
parser.add_argument('--relief', action='store_true', help='Plot relief instead of elevation')
args = parser.parse_args()

DATA_BASE = Path(args.data)
CACHE = Path('cache.pkl')
RESOLUTION = 5 # meters
STATION_HEIGHTS = [0.1, 0.5, 1.0]
CAR_HEIGHT = 1.5

def main():
    # Load data
    data = pd.read_csv(DATA_BASE / 'locations.csv')
    print(data)

    ins = data['i']
    lats = data['lat']
    lons = data['lon']

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

        elvs = [get_elevation(lat, lon) for lat, lon in zip(lat_smooth, lon_smooth)]
        dists = interp1d([base_i, i], [0, dist])(ins_smooth)
        paths[i] = (elvs, dists, lat, lon)

    ## plot coordinates
    #plt.figure(figsize=(10, 10))
    #plt.plot(lons, lats, 'o', label='Original data')
    #plt.plot(lon_smooth, lat_smooth, label='Interpolated data')
    #plt.legend()
    #plt.show()

    if args.relief:
        last_path = paths[max(paths.keys(), key=lambda p: len(paths[p][0]))][0]
        corr = np.linspace(last_path[0], last_path[-1], num=len(last_path))

    # plot elevation
    plt.figure(figsize=(10, 5))
    colors = np.concatenate([
        plt.colormaps["Dark2"](np.linspace(0, 1, 8)), 
        plt.colormaps["Set1"](np.linspace(0, 1, 9))
    ])
    
    for i, (elvs, dists, lat, lon) in paths.items():
        if args.relief:
            elvs -= corr[:len(elvs)]
        plt.plot(dists, elvs, label=f'{i}', color=colors[i])
        plt.axvline(dists[-1], color='grey', linestyle='--', alpha=0.5)
        plt.text(dists[-1] + 5, elvs[-1], f'{i}')
        plt.scatter(dists[-1], elvs[-1], color='black', marker='2', s=150)

        for h in STATION_HEIGHTS:
            plt.plot([dists[0], dists[-1]], [elvs[0] + h, elvs[-1] + CAR_HEIGHT], color=colors[i], linestyle='--', alpha=0.5)

    
    #plt.legend()
    plt.xlabel('Transmitting distance [m]')
    plt.ylabel('Relief' if args.relief else 'Elevation [m]')
    plt.tight_layout()
    plt.savefig(f'elevation-{DATA_BASE.stem}.svg')
    plt.show()


if __name__ == '__main__':
    main()
