import cv2

from screen import ScreenCapture
from llm import LLMBackend
from describe import DescribeBackend
from email_sender import send_email
from timestamp import Timestamp


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

    prompt_text = (
        "caption this screenshot with as much text as you can recognize on the screen"
    )
    descriptor = "你需要用中文提取我的工作，并总结我在哪个时间段(相似工作应当放在同一个时间段下)主要干了什么(从核心任务，具体工作，关联工具这三个方面总结)，下面是我的屏幕截图日志："
    interval_minutes = 5  # 5 minutes interval for capturing the screen

    llm_backend = LLMBackend(
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
    screen_capture = ScreenCapture(scale_factor=1, color=None)

    # describer stores the description of each images or screenshots
    describer = DescribeBackend(dump_path="description.json", descriptor=descriptor, llm_backend=llm_backend_describe)

    timestamp = Timestamp(interval_minutes=interval_minutes)

    # Display the captured frame
    try:
        """
        init epoch
        """
        frame = screen_capture.capture_screen()
        response = llm_backend.send_img_to_backend(frame)
        describer.log(response)
        print("[" + timestamp.strf_now() + "] init epoch: one frame processed")

        while True:
            # wait for the next capture interval
            timestamp.wait_for_next_capture()
            # check if a day has passed to summarize the work
            if timestamp.is_past_a_day():
                summary = describer.summarize()
                send_email(subject="Daily Summary", body=summary)

            # capture the screen
            frame = screen_capture.capture_screen()
            # POST to get the response and log it
            response = llm_backend.send_img_to_backend(frame)
            describer.log(response)

            print("[" + timestamp.strf_now() + "] main loop: one frame processed")
    except RuntimeError as e:
        describer.dump()  # Dump the description if screen capture fails

    # Release resources
    screen_capture.release()


if __name__ == "__main__":
    main()
