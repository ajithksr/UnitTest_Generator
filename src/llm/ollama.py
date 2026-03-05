import requests
import json
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "qwen2.5-coder:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                print(f"[WARN] Ollama at {base_url} returned status {response.status_code}")
        except Exception as e:
            print(f"[WARN] Ollama at {base_url} not responsive: {e}")

    def generate_code(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        system_context = (
            "You are an expert C and C++ unit test generator using Google Test (gtest/gmock). "
            "You handle free functions (C and C++), static functions, class member methods "
            "(including private and protected), constructors, and destructors. "
            "Always include boundary, equivalence partition, and MCDC test cases."
        )
        payload = {
            "model": self.model,
            "prompt": f"System: {system_context}\n\nUser: {prompt}",
            "stream": False,
            "options": {"temperature": 0.2},
        }
        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")
                if "```cpp" in text:
                    text = text.split("```cpp")[1].split("```")[0].strip()
                elif "```c" in text:
                    text = text.split("```c")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                return text
            else:
                return f"// Error: Ollama returned {response.status_code}: {response.text}"
        except Exception as e:
            return f"// Error: Ollama connection failed: {e}"
