#!/usr/bin/env python3

import datetime
import pathlib
import sys
from pathlib import Path
from typing import Dict, List

import yaml

from mapsbrowser import FirefoxBrowser, ChromeBrowser
from screenshotscheduler import ScreenshotScheduler


def gen_url(latitude, longitude, zoom, data='!5m1!1e1'):
    url = f'https://www.google.be/maps/@{latitude},{longitude},{zoom}z/data={data}'
    return url


def gen_image_path(name, screenshot_folder):
    now = datetime.datetime.now()
    image_name = f'{now:%Y-%m-%d_%H%M}-{name}.png'

    base_path = Path(screenshot_folder, name)
    base_path.mkdir(parents=True, exist_ok=True)

    return base_path.joinpath(image_name)


def get_screenshots_now(locations: Dict, screenshot_folder: pathlib.Path, window_x: int = 1024, window_y: int = 768) -> None:
    if sys.platform.startswith('linux'):
        Browser = ChromeBrowser
    elif sys.platform.startswith('win32'):
        Browser = FirefoxBrowser
    else:
        print('[ERROR]: OS is not linux or windows. Other operating systems are not supported.')
        return

    with Browser(visual=False) as browser:
        browser.setup(window_x, window_y)
        print(f'{locations=}')
        for name, url in locations.items():
            image_path = gen_image_path(name, screenshot_folder)
            browser.get_maps_page(url, image_path)


def generate_executetimes(start_time: datetime.datetime, end_time: datetime.datetime, interval: int) -> List[datetime.datetime]:
    execute_times = []
    pointer = start_time
    delta = datetime.timedelta(minutes=interval)
    while pointer <= end_time:
        execute_times.append(pointer)
        pointer += delta

    return execute_times


def import_from_flask(name: str, latitude: float, longitude: float, zoom: float,
                      start_datetime: List[datetime.datetime], end_datetime: List[datetime.datetime],
                      interval: int) -> [str, str, List[datetime.datetime]]:
    url = gen_url(latitude, longitude, zoom)

    excute_times = set()
    for start, end in zip(start_datetime, end_datetime):
        excute_times.update(generate_executetimes(start, end, interval))

    print(excute_times)
    return name, url, list(excute_times)



def execute_from_config():
    print('Started maps traffic screenshot tool')
    with open('config.yaml') as configuration_file:
        config = yaml.full_load(configuration_file)

    print('[INFO]: Beginnen met alle taken te plannen.')

    planner = ScreenshotScheduler(get_screenshots_now)

    for name in config['locations']:
        data = config['locations'][name]

        url = gen_url(
            latitude=config['locations'][name]['latitude'],
            longitude=config['locations'][name]['longitude'],
            zoom=config['locations'][name]['zoom'])

        base_path = Path('screenshots')

        for time_string in data['time']:
            if time_string == 'now':
                get_screenshots_now({name: url}, base_path)
            else:
                try:
                    time_object = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M')
                except ValueError:
                    print(f'[ERROR] Geen geldig moment ingegeven! {time_string = }')
                    continue
                planner.add_exact_task(name, url, time_object, base_path)

    print('[INFO]: Geen resterende taken meer, afsluiten')
    input('Druk op enter om dit venster te sluiten...')


if __name__ == '__main__':
    execute_from_config()
    """
    import_from_flask(
        name="Test",
        latitude=50.357,
        longitude=4.257,
        zoom=13.5,
        start_datetime=datetime.datetime.now(),
        end_datetime=datetime.datetime.now() + datetime.timedelta(days=5),
        interval=15
    )
    """

