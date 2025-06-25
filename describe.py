import json
import time


class DescribeBackend:
    """
    DescribeBackend is a class that manages the description of images or screenshots.
    """

    def __init__(self, dump_path="description.json", descriptor="你需要提取我的工作，并总结我在哪个时间段(相似工作应当放在同一个时间段下)主要干了什么(从核心任务，具体工作，关联工具这三个方面总结)，下面是我的屏幕截图日志："):
        self.dump_path = dump_path
        self.description = {}
        self.token_len = {}
        self.descriptor = descriptor

    def get_description(self, max_length=10000):
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
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(key))
                + '\n'
                + self.description.pop(key)
            )

        return "\n\n".join(block_description)

    def log(self, description):
        current_time = int(time.time())  # Use timestamp as key
        self.description[current_time] = description
        self.token_len[current_time] = len(description.split())  # simply split by space

    def summarize(self, llm_backend):
        screen_summary = []
        while len(self.description) != 0:
            screen_summary.append(
                llm_backend.send_msg_to_backend(
                    self.descriptor
                    + self.get_description(max_length=10000)
                )
            )
        
        summary = ""
        if not screen_summary:
            summary = "No summary available, check if something went wrong in the code or the LLM backend server."
        elif len(screen_summary) == 1:
            summary = screen_summary[0]
        else:
            summary = "\n\n".join(screen_summary)
        
        return summary

    def dump(self):
        with open(self.dump_path, "w") as file:
            json.dump(self.description, file, indent=4)

    def clear(self):
        self.description = {}
