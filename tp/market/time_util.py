from dataclasses import dataclass
from datetime import datetime
import pytz

import time
def sleep_sec(s):
    time.sleep(s)
    return

@dataclass
class Event:
    name: str
    start_time: datetime
    end_time: datetime

    def duration(self) -> str:
        """Returns the duration of the event as a string."""
        duration = self.end_time - self.start_time
        return str(duration)

    @staticmethod
    def _get_current_time(timezone_str: str) -> datetime:
        """Returns the current time in the specified timezone (defaults to EST)."""
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)

def get_current_time(frmt = "%Y-%m-%d %H:%M:%S"):
    return Event._get_current_time("America/New_York").strftime(format=frmt)

if __name__ == "__main__":
    print(get_current_time())
# Usage Example
    current_time_est = get_current_time()  # Defaults to EST
    print("Current Time (EST):", current_time_est)
    sleep_sec(5)
