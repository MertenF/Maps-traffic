import pathlib
import sched
import time
import datetime
from pathlib import Path
from typing import Dict, List, Callable


class ScreenshotScheduler:
    def __init__(self, action_funtion: Callable[[Dict, pathlib.Path, int, int], None]):
        self.plan = sched.scheduler(time.time, time.sleep)
        self.action = action_funtion
        self._running = False

    def add_exact_task(self, name: str, url: str, execute_time: datetime.datetime, screenshot_folder: Path):
        if execute_time > datetime.datetime.now():
            self._add_task({name: url}, execute_time, screenshot_folder)
            print(f'[INFO]: "{name}" op {execute_time} is toegevoegd.')
        else:
            print(f'[WARNING]: "{name}" op {execute_time} valt in het verleden, overgeslagen.')

    def add_task_same_name(self, name: str, url: str, execute_times: List[datetime.datetime], screenshot_folder: Path):
        for execute_time in execute_times:
            if execute_time > datetime.datetime.now():
                self._add_task({name: url}, execute_time, screenshot_folder)

    def _add_task(self, locations: Dict, execute_time: datetime.datetime, save_path: Path):
        self.plan.enterabs(
            time=execute_time.timestamp(),
            priority=1,
            action=self.action,
            argument=(locations, save_path),
        )

    def running(self) -> bool:
        """Check whether the scheduler is running"""
        return self._running

    def run(self):
        if not self.plan.empty():
            if not self._running:
                print('[INFO]: Starting the scheduler!')
                self._running = True
                self.plan.run()
                self._running = False
                print('[INFO] Scheduler is done running')
            else:
                print('[WARNING] Scheduler already running!')
        else:
            print('[WARNING] No tasks planning, cannot run')