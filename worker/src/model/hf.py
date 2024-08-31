import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class GPT:
    def __init__(self):
        self.url = os.environ.get('MODEL_URL')
        print("token :", os.environ.get('HUGGINFACE_INFERENCE_TOKEN'))
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINFACE_INFERENCE_TOKEN')}",
            "Content-Type": "application/json"}
        self.payload = {
            "inputs": "",
            "parameters": {
                "return_full_text": False,
                "use_cache": False,
                "max_new_tokens": 25
            }

        }

    def query(self, input: str) -> list:
        self.payload["inputs"] = f"Human: {input} Bot:"
        data = json.dumps(self.payload)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=data)
        data = json.loads(response.content.decode("utf-8"))
        print("Model Query Response : ", data)
        text = data[0]['generated_text']
        res = str(text.split("Human:")[0]).strip("\n").strip()
        print("Model Query Response split : ", res)
        return res


if __name__ == "__main__":
    GPT().query("Will artificial intelligence help humanity conquer the universe?")