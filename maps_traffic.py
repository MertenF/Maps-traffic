import datetime
import os
import sched
import sys
import time
from pathlib import Path

import yaml

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options


def get_maps_page(driver, url, base_path, name):
    now = datetime.datetime.now()
    image_name = '{0}-{1}.png'.format(now.strftime("%Y-%m-%d_%H%M"), name)
    image_path = base_path.joinpath(image_name)
    
    driver.get(url)

# Remove omnibox
    js_string = "var element = document.getElementById(\"omnibox-container\"); element.remove();"
    driver.execute_script(js_string)

# Remove username and icons
    js_string = "var element = document.getElementById(\"vasquette\"); element.remove();"
    driver.execute_script(js_string)

# Remove bottom scaling bar
    js_string = "var element = document.getElementsByClassName(\"app-viewcard-strip\"); element[0].remove();"
    driver.execute_script(js_string)

    print('[INFO]: Saving screenshot to', str(image_path))
    driver.save_screenshot(str(image_path))

    
def read_config():
    with open('config.yaml') as configFile:
        config = yaml.full_load(configFile)
        return config


def url_gen(latitude, longitude, zoom, data='!5m1!1e1'):
    url = f'https://www.google.be/maps/@{latitude},{longitude},{zoom}z/data={data}'
    return url


def resource_path(relative_path='./driver/geckodriver.exe'):
    try:
        print('try')
        base_path = sys._MEIPASS
        print('tried')
    except AttributeError:
        print('exception')
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


def main():
    print('Started maps traffic screenshot tool')
    print('[INFO]: Config inlezen.')
    config = read_config()
    
    print('[INFO]: Webbrowser starten, dit kan even duren.')
    if config['visual']:
        driver = webdriver.Firefox(executable_path=resource_path())
    else:
        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities['marionette'] = True
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        driver = webdriver.Firefox(
            executable_path=resource_path(),
            capabilities=capabilities,
            options=options)

    driver.set_window_size(config['window_x'], config['window_y'])

    driver.get('http://www.google.be/404page')
    driver.add_cookie(
        {'name': 'CONSENT',
         'value': 'YES+BE.nl'})

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
                get_maps_page(driver, url, base_path, name)
            else:
                time_object = datetime.datetime.strptime(timeString, '%Y-%m-%d %H:%M')
                if time_object > datetime.datetime.now():
                    plan.enterabs(time_object.timestamp(), 1, get_maps_page, argument=(driver, url, base_path, name))
                    print(f'[INFO]: "{name}" op {timeString} is toegevoegd.')
                else:
                    print(f'[ERROR]: "{name}" op {timeString} valt in het verleden, overgeslagen.')

    if not plan.empty():
        print('[INFO]: Alle taken gepland. Dit venster open laten tot alle taken voltooid zijn aub.')
        plan.run()

    print('[INFO]: Geen resterende taken meer, afsluiten')
    driver.quit()
    input('Druk op enter om dit venster te sluiten...')


if __name__ == '__main__':
    main()
