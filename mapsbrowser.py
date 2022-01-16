import datetime
import pathlib
import sys
import os


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class ScreenshotBrowser:
    def __init__(self, driver):
        self.driver = driver

    def setup(self, x_size: int, y_size: int) -> None:
        """Sets up the browser window size and adds consent"""
        # self.config['window_x'], self.config['window_y']
        self.driver.set_window_size(x_size, y_size)

        self.driver.get('https://www.google.be/404page')
        self.driver.add_cookie(
            {'name': 'CONSENT',
             'value': 'YES+cb.20220111+BE.nl'})

    def get_maps_page(self, url: str, base_path: pathlib.Path, name: str) -> None:
        """Gets the google maps page from url, removes clutter and saves it to base_path with name."""

        now = datetime.datetime.now()
        image_name = f'{now:%Y-%m-%d_%H%M}-{name}.png'
        image_path = base_path.joinpath(image_name)

        self.driver.get(url)

        # Remove omnibox
        js_string = 'var element = document.getElementById("omnibox-container"); element.remove();'
        self.driver.execute_script(js_string)
        # Remove username and icons
        js_string = 'var element = document.getElementById("vasquette"); element.remove();'
        self.driver.execute_script(js_string)
        # Remove bottom scaling bar
        js_string = 'var element = document.getElementsByClassName("app-viewcard-strip"); element[0].remove();'
        self.driver.execute_script(js_string)

        print('[INFO]: Saving screenshot to', str(image_path))
        self.driver.save_screenshot(str(image_path))

    def quit(self) -> None:
        """Quits the browser, closing it gracefully and preventing it from hogging up memory"""
        self.driver.quit()


def gecko_path():
    """
    Returns path to the geckodriver.
    Detects if it is running as a frozen instance by pyinstaller or not.
    """
    relative_path = './driver/geckodriver.exe'
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class FirefoxBrowser(ScreenshotBrowser):
    def __init__(self, visual: bool = False):
        if visual:
            self.driver = webdriver.Firefox(executable_path=gecko_path())
        else:
            capabilities = DesiredCapabilities.FIREFOX.copy()
            capabilities['marionette'] = True

            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

            self.driver = webdriver.Firefox(
                executable_path=gecko_path(),
                capabilities=capabilities,
                options=options,
            )

        super().__init__(self.driver)


class ChromeBrowser(ScreenshotBrowser):
    def __init__(self, visual=False):
        chromedriver_path = '/usr/lib/chromium-browser/chromedriver'

        if visual:
            self.driver = webdriver.Chrome(chromedriver_path)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')

            self.driver = webdriver.Chrome(
                executable_path=chromedriver_path,
                options=options,
            )

        super().__init__(self.driver)
