import serial
from datetime import datetime
from pathlib import Path

LOG_FILE = Path('power_log.csv')

port = serial.Serial('/dev/ttyACM0', timeout=1)

while port.is_open:
    line = port.readline()
    if not line:
        continue

    try:
        line = line.decode('utf-8')
        print(line, end='')
        
        parts = line.split(',')
        values = {}
        for part in parts:
            piece = part.split('=')
            values[piece[0].strip()] = float(piece[1].strip())

        if not LOG_FILE.exists():
            LOG_FILE.write_text('time,current,voltage\n', encoding='utf-8')
        with open(LOG_FILE, 'a', encoding='utf-8') as file:
            file.write(f"{datetime.now().strftime('%y-%m-%d %H:%M.%S')},{values['a']},{values['v']}\n")

    except KeyboardInterrupt:
        port.close()
    except Exception as e:
        print('Error:', e)
