import base64
import cv2
import json
import numpy as np
import requests
import time


class LLMBackend:
    def __init__(
        self,
        model_name="qwen2.5vl:latest",
        prompt_text="描述这个屏幕截图中的内容，尽可能多地识别屏幕上的文本（如果有多个屏幕截图，请分别描述每个屏幕截图）",
        url="http://localhost:11434",
        uri="/api/generate",
    ):
        """
        将 NumPy 图像数组编码为 Base64 并发送到后端服务器

        Args:
            image_np_array (np.ndarray): 要发送的图像 NumPy 数组
            model_name (str): 要使用的模型名称
            prompt_text (str): 图像描述提示
            url (str): 后端 API 的 URL
            uri (str): 后端 API 的 URI
        """
        self.model_name = model_name
        self.url = url
        self.uri = uri
        self.prompt_text = prompt_text
        self.retry_count = 0  # Initialize retry count
        self.max_retries = 3  # Maximum number of retries for sending requests
        self.tmp_msg = ""

    def parse_response_all(self, response):
        res = ""
        start_time = time.time()
        for line in response.iter_lines():
            obj = json.loads(line)
            res += obj["response"]  # OpenAI-like API
            if obj["done"] == True:
                break
            if time.time() - start_time > 30:  # Check if the response is taking too long
                break

        return res

    def parse_response_without_thinking(self, response):
        """
        exclude think tag from response
        """
        res = ""
        thinking = False
        start_time = time.time()
        for line in response.iter_lines():
            obj = json.loads(line)
            if "<think>" in obj["response"]:
                thinking = True
            elif thinking and "</think>" in obj["response"]:
                thinking = False
            elif not thinking:
                res += obj["response"]
                if obj["done"] == True:
                    break
            if time.time() - start_time > 30:  # Check if the response is taking too long
                break

        # thinking tag not closed
        if thinking:
            print(
                "Warning: thinking tag found true when done parsing, response may not be complete."
            )
            return self.parse_response_all(response)

        return res

    def send_msg_to_backend(self, msg):
        if msg is None:
            msg = self.tmp_msg
        payload = {
            "model": self.model_name,
            "prompt": msg,
        }
        print("msg sent:", payload)

        try:
            # post the request to the backend server
            # (connect timeout, read timeout) in seconds
            response = requests.post(self.url + self.uri, json=payload, stream=True, timeout=(30, 30))
            response.raise_for_status()
            print("成功响应:", response.status_code)
            self.retry_count = 0
            self.tmp_msg = ""
            return self.parse_response_without_thinking(response=response)
        except requests.exceptions.RequestException as e:
            print(f"发送请求时发生错误: {e}")
            if hasattr(e, "response") and e.response is not None:
                print("错误响应内容:", e.response.text)
            self.retry_count += 1
            self.tmp_msg = msg
            if self.retry_count >= self.max_retries:
                print("重试次数超过最大值")
                return "Failed to get response and retry over 3 times."
            return self.send_msg_to_backend(msg=None)

    def send_img_to_backend(self, image_np_array):
        # encoding the image to base64
        ret, buffer = cv2.imencode(
            ".jpg", image_np_array, [cv2.IMWRITE_JPEG_QUALITY, 90]
        )
        if not ret:
            print("错误: 图像编码失败！")
            return
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        payload = {
            "model": self.model_name,
            "prompt": self.prompt_text,
            "images": [image_base64],
        }
        print("msg sent:", payload)

        try:
            response = requests.post(self.url + self.uri, json=payload, stream=True, timeout=(30, 30))
            response.raise_for_status()
            print("成功响应:", response.status_code)
            return self.parse_response_all(response=response)
        except requests.exceptions.RequestException as e:
            print(f"发送请求时发生错误: {e}")
            if hasattr(e, "response") and e.response is not None:
                print("错误响应内容:", e.response.text)
            return "Failed to get response. Use description from last time."
