import numpy as np
import onnxruntime
from huggingface_hub import hf_hub_download

MODEL_PATH = hf_hub_download(
    repo_id="pirocheto/phishing-url-detection",
    filename="model.onnx"
)

ONNX_SESSION = onnxruntime.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)


def predict_url(url: str) -> float:
    inputs = np.array([url], dtype="str")
    results = ONNX_SESSION.run(None, {"inputs": inputs})[1]
    return float(results[0][1] * 100)