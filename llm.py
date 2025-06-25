import cv2
import requests
import json
import base64
import numpy as np


class LLMBackend:
    def __init__(
        self,
        model_name="qwen2.5vl:latest",
        prompt_text="caption this screenshot",
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

    def parse_response_all(self, response):
        res = ""
        for line in response.iter_lines():
            obj = json.loads(line)
            res += obj["response"]
            if obj["done"] == True:
                break
        return res

    def parse_response_without_thinking(self, response):
        """
        exclude think tag from response
        """
        res = ""
        thinking = False
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

        # thinking tag not closed
        if thinking:
            print(
                "Warning: thinking tag found true when done parsing, response may not be complete."
            )
            return self.parse_response_all(response)

        return res

    def send_msg_to_backend(self, msg):
        # construct the payload
        payload = {
            "model": self.model_name,
            "prompt": msg,
        }

        try:
            # post the request to the backend server
            response = requests.post(self.url + self.uri, json=payload)
            response.raise_for_status()
            print("服务器响应状态码:", response.status_code)
            # parse the response and return the result
            return self.parse_response_without_thinking(response=response)
        except requests.exceptions.RequestException as e:
            print(f"发送请求时发生错误: {e}")
            if hasattr(e, "response") and e.response is not None:
                print("服务器响应内容:", e.response.text)

    def send_img_to_backend(self, image_np_array):
        # encoding the image to base64
        ret, buffer = cv2.imencode(
            ".jpg", image_np_array, [cv2.IMWRITE_JPEG_QUALITY, 90]
        )
        if not ret:
            print("错误: 图像编码失败！")
            return
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # construct the payload
        payload = {
            "model": self.model_name,
            "prompt": self.prompt_text,
            "images": [image_base64],
        }

        try:
            # post the request to the backend server
            response = requests.post(self.url + self.uri, json=payload)
            response.raise_for_status()
            print("服务器响应状态码:", response.status_code)
            # parse the response and return the result
            return self.parse_response_without_thinking(response=response)
        except requests.exceptions.RequestException as e:
            print(f"发送请求时发生错误: {e}")
            if hasattr(e, "response") and e.response is not None:
                print("服务器响应内容:", e.response.text)
