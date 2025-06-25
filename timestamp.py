import time
from datetime import datetime, timedelta


class Timestamp:
    """
    Timestamp is a class that manages the timestamp of the last processed frame.
    """

    def __init__(self, interval_minutes=5):
        self.last_day = datetime.now()  # Store the current timestamp initially
        self.last_capture = datetime.now()  # Store the current timestamp initially
        self.interval_minutes = (
            interval_minutes  # Interval in minutes for capturing the screen
        )

    def now(self):
        return datetime.now()

    def strf_now(self, fmt="%Y-%m-%d %H:%M:%S"):
        return self.now().strftime(fmt)

    def wait_for_next_capture(self):
        """
        Wait for the next capture based on the specified interval in minutes.
        """
        while True:
            current_time = datetime.now()
            if current_time - self.last_capture >= timedelta(
                minutes=self.interval_minutes
            ):
                self.last_capture = current_time
                return True
            time.sleep(1)

    def is_past_a_day(self):
        current_time = datetime.now()
        if current_time - self.last_day >= timedelta(hours=24):
            self.last_day = current_time
            return True
        return False


if __name__ == "__main__":
    timestamp = Timestamp(interval_minutes=5)
    while True:
        timestamp.wait_for_next_capture()
        if timestamp.is_past_a_day():
            print("Is past a day")
        print("One round")
