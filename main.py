import cv2
import numpy as np
import mss
import time
from datetime import datetime, timedelta

from screen import ScreenCapture
from llm import LLMBackend
from describe import DescribeBackend
from email_sender import send_email


class Timestamp:
    """
    Timestamp is a class that manages the timestamp of the last processed frame.
    """

    def __init__(self):
        self.last_day = datetime.now()  # Store the current timestamp initially
        self.last_capture = datetime.now()  # Store the current timestamp initially

    def now(self):
        return datetime.now()
    
    def strf_now(self, fmt="%Y-%m-%d %H:%M:%S"):
        return self.now().strftime(fmt)

    def wait_for_next_capture(self, interval_minutes=4):
        """
        Wait for the next capture based on the specified interval in minutes.
        """
        while True:
            current_time = datetime.now()
            if current_time - self.last_capture >= timedelta(minutes=interval_minutes):
                self.last_capture = current_time
                return True
            time.sleep(10)

    def is_past_a_day(self):
        current_time = datetime.now()
        if current_time - self.last_day >= timedelta(hours=24):
            self.last_day = current_time
            return True
        return False


def main():
    """
    the related cURL is (I'm using ollama as backend server):
    curl -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d '{ \
            "model": "qwen2.5vl:latest", \
            "prompt": "caption this screenshot", \
            "images": "<base64_encoded_image>"
        }'

    where <base64_encoded_image> is the base64 encoded string of the image you want
    to send.
    """
    
    prompt_text = "caption this screenshot with as much text as you can recognize on the screen"
    descriptor = "你需要用中文提取我的工作，并总结我在哪个时间段(相似工作应当放在同一个时间段下)主要干了什么(从核心任务，具体工作，关联工具这三个方面总结)，下面是我的屏幕截图日志："

    llm_backend = LLMBackend(
        model_name="qwen2.5vl:latest",  # configure your model name here
        prompt_text=prompt_text,
        url="http://localhost:11434",  # configure your backend URL here
        uri="/api/generate",  # configure your backend URI here
    )

    # screen_capture do the actual screen capturing
    screen_capture = ScreenCapture(scale_factor=1, color=None)

    # describer stores the description of each images or screenshots
    describer = DescribeBackend(dump_path="description.json", descriptor=descriptor)

    timestamp = Timestamp()

    # Display the captured frame
    try:
        """
        init epoch
        """
        frame = screen_capture.capture_screen()
        response = llm_backend.send_img_to_backend(frame)
        describer.log(response)
        cv2.waitKey(4 * 60)
        print("[" + timestamp.strf_now() + "] init epoch: one frame processed")

        while True:
            timestamp.wait_for_next_capture(interval_minutes=5)
            if timestamp.is_past_a_day():
                summary = describer.summarize(llm_backend=llm_backend)
                send_email(subject="Daily Summary", body=summary)

            # capture the screen
            frame = screen_capture.capture_screen()

            # POST to get the response and log it
            response = llm_backend.send_img_to_backend(frame)
            describer.log(response)

            cv2.waitKey(4 * 60)
            print("[" + timestamp.strf_now() + "] main loop: one frame processed")
    except RuntimeError as e:
        describer.dump()  # Dump the description if screen capture fails

    # Release resources
    screen_capture.release()


if __name__ == "__main__":
    main()
