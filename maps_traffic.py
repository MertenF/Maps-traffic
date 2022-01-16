#!/usr/bin/env python3

import datetime
import sched
import sys
import time
from pathlib import Path

import yaml

from mapsbrowser import FirefoxBrowser, ChromeBrowser


def url_gen(latitude, longitude, zoom, data='!5m1!1e1'):
    url = f'https://www.google.be/maps/@{latitude},{longitude},{zoom}z/data={data}'
    return url


def main():
    print('Started maps traffic screenshot tool')
    with open('config.yaml') as configuration_file:
        config = yaml.full_load(configuration_file)

    if sys.platform.startswith('linux'):
        Browser = ChromeBrowser
    elif sys.platform.startswith('win32'):
        Browser = FirefoxBrowser
    else:
        print('[ERROR]: OS is not linux or windows. Other operating systems are not supported.')
        return

    with Browser(config['visual']) as browser:
        browser.setup(config['window_x'], config['window_y'])

        print('[INFO]: Beginnen met alle taken te plannen.')
        plan = sched.scheduler(time.time, time.sleep)

        for name in config['locations']:
            data = config['locations'][name]

            url = url_gen(
                latitude=config['locations'][name]['latitude'],
                longitude=config['locations'][name]['longitude'],
                zoom=config['locations'][name]['zoom'])

            base_path = Path(f'screenshots/{name}')
            base_path.mkdir(parents=True, exist_ok=True)

            for timeString in data['time']:
                if timeString == 'now':
                    print(f'[INFO]: "{name}" heeft "now" als tijdstip, screenshot wordt nu genomen.')
                    browser.get_maps_page(url, base_path, name)
                else:
                    time_object = datetime.datetime.strptime(timeString, '%Y-%m-%d %H:%M')
                    if time_object > datetime.datetime.now():
                        plan.enterabs(
                            time=time_object.timestamp(),
                            priority=1,
                            action=browser.get_maps_page,
                            argument=(url, base_path, name),
                        )
                        print(f'[INFO]: "{name}" op {timeString} is toegevoegd.')
                    else:
                        print(f'[ERROR]: "{name}" op {timeString} valt in het verleden, overgeslagen.')

        if not plan.empty():
            print('[INFO]: Alle taken gepland. Dit venster open laten tot alle taken voltooid zijn aub.')
            plan.run()

        print('[INFO]: Geen resterende taken meer, afsluiten')
        input('Druk op enter om dit venster te sluiten...')


if __name__ == '__main__':
    main()
