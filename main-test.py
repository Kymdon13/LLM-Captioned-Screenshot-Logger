import os
import cv2
import time

from screen import ScreenCapture
from llm import LLMBackend
from describe import DescribeBackend
from email_sender import send_email
from timestamp import Timestamp


def test():
    screen_capture_dir = "screenshots"
    prompt_text = "描述这个屏幕截图中的内容，尽可能多地识别屏幕上的文本（如果有多个屏幕截图，请分别描述每个屏幕截图）"
    descriptor = "你需要用中文提取我的工作，并总结我在哪个时间段(相似工作应当放在同一个时间段下)主要干了什么(从核心任务，具体工作，关联工具这三个方面总结)，下面是我的屏幕截图日志（这个日志是由视觉大模型生成的，需要你自行甄别真正的屏幕内容）："
    interval_minutes = 5  # 5 minutes interval for capturing the screen

    llm_backend_vision = LLMBackend(
        model_name="qwen2.5vl:latest",  # configure your model name here
        prompt_text=prompt_text,
        url="http://localhost:11434",  # configure your backend URL here
        uri="/api/generate",  # configure your backend URI here
    )

    llm_backend_describe = LLMBackend(
        model_name="qwen3:8b",  # configure your model name here
        prompt_text="",
        url="http://localhost:11434",  # configure your backend URL here
        uri="/api/generate",  # configure your backend URI here
    )

    # screen_capture do the actual screen capturing
    screen_capture = ScreenCapture(scale_factor=2, color=None)

    # describer stores the description of each images or screenshots
    describer = DescribeBackend(
        dump_path="description.json",
        descriptor=descriptor,
        llm_backend_vision=llm_backend_vision,
        llm_backend_describe=llm_backend_describe,
        screen_capture_dir=screen_capture_dir
    )

    timestamp = Timestamp(interval_minutes=interval_minutes)

    # Display the captured frame
    print("test start")
    try:
        """
        init epoch
        """
        frame = screen_capture.capture_screen()
        cv2.imwrite(os.path.join(screen_capture_dir, str(int(time.time())) + ".jpg"), frame)
        print("[" + timestamp.strf_now() + "] init epoch: one frame captured")

        for _ in range(3):
            # wait for the next capture interval
            time.sleep(1)

            # capture and save the screenshot
            frame = screen_capture.capture_screen()
            if frame.sum() == 0:
                continue
            cv2.imwrite(os.path.join(screen_capture_dir, str(int(time.time())) + ".jpg"), frame)

            print("[" + timestamp.strf_now() + "] main loop: one frame captured")

        print('Entering Summary...')
        summary = describer.summarize()
        send_email(subject="Daily Summary", body=summary)
    except RuntimeError as e:
        describer.dump()  # Dump the description if screen capture fails

    # Release resources
    screen_capture.release()
    print("test done")


if __name__ == "__main__":
    test()
