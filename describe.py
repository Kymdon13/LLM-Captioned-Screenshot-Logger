import os
import json
import time
from datetime import datetime

import cv2


class DescribeBackend:
    """
    DescribeBackend is a class that manages the description of images or screenshots.
    """

    def __init__(
        self,
        dump_path="description.json",
        descriptor="你需要用中文提取我的工作，并总结我在哪个时间段(相似工作应当放在同一个时间段下)主要干了什么(从核心任务，具体工作，关联工具这三个方面总结)，下面是我的屏幕截图日志（这个日志是由视觉大模型生成的，需要你自行甄别真正的屏幕内容）：",
        llm_backend_vision=None,
        llm_backend_describe=None,
        screen_capture_dir="screenshots",  # Directory to save screenshots
    ):
        self.dump_path = dump_path
        self.description = {}
        self.token_len = {}
        self.descriptor = descriptor
        self.llm_backend_vision = llm_backend_vision
        self.llm_backend_describe = llm_backend_describe
        self.screen_capture_dir = screen_capture_dir

    def get_description(self, max_length=5000):
        """
        Consume a block of description and return it, one block description is less than max_length.

        Args:
            max_length (int): Maximum length of the description to return (simply split by space).

        Returns:
            str: The description of the image or screenshot.
        """
        if not self.description:
            return "No description available."

        # Join descriptions in one block and truncate if necessary
        block_description = []
        token_count = 0
        for key in sorted(self.description.keys()):
            token_count += self.token_len[key]
            if token_count > max_length:
                break
            block_description.append(
                time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(key))
                + "\n"
                + self.description.pop(key)
            )
            self.token_len.pop(key)

        return "\n\n".join(block_description)

    def log(self, timestamp, description):
        self.description[timestamp] = description
        self.token_len[timestamp] = len(description.split())  # simply space tokenize

    def summarize(self):
        # summarize the screen
        for file in sorted(os.listdir(self.screen_capture_dir)):
            if file.endswith(".jpg"):
                frame = cv2.imread(os.path.join(self.screen_capture_dir, file))
                if frame is None:
                    print(f"Failed to read image {file}. Skipping.")
                    continue

                # send the image to the backend for description
                timestamp = int(os.path.splitext(file)[0])
                response = self.llm_backend_vision.send_img_to_backend(frame)
                print(
                    f"One image processed of timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}"
                )
                self.log(timestamp, response)

        # summarize the description
        screen_summary = []
        print("Summarizing the description...")
        while len(self.description) != 0:
            screen_caption = self.get_description(max_length=5000)
            response = self.llm_backend_describe.send_msg_to_backend(
                self.descriptor + screen_caption
            )
            screen_summary.append(response)

        summary = ""
        if not screen_summary:
            summary = "No summary available, check if something went wrong in the code or the LLM backend server."
        elif len(screen_summary) == 1:
            summary = screen_summary[0]
        else:
            summary = "\n\n".join(screen_summary)

        # clear the screenshots after summarizing
        for file in os.listdir(self.screen_capture_dir):
            os.remove(os.path.join(self.screen_capture_dir, file))

        return summary

    def dump(self):
        with open(self.dump_path, "w") as file:
            json.dump(self.description, file, indent=4)

    def clear(self):
        self.description = {}
