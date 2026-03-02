from .base import LLMProvider
from ..prompts import SYSTEM_CONTEXT

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model_client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError(
                "Google Generative AI client not installed. Run `pip install google-generativeai`."
            )

    def generate_code(self, prompt: str) -> str:
        """Calls Gemini API to generate code/text with retry logic for 429s."""
        import time
        full_prompt = f"System: {SYSTEM_CONTEXT}\n\nUser: {prompt}"
        
        for attempt in range(5):
            try:
                response = self.model_client.generate_content(full_prompt)
                if not response.text:
                    return "// Error: No response from Gemini."
                
                text = response.text
                # Cleanup markdown blocks
                if "```" in text:
                    import re
                    match = re.search(r'```(?:\w+)?\n?(.*?)```', text, re.DOTALL)
                    if match:
                        text = match.group(1).strip()
                    else:
                        text = text.replace("```cpp", "").replace("```c", "").replace("```", "").strip()
                return text
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "ResourceExhausted" in err_str:
                    wait_time = (2 ** attempt) * 5
                    print(f"[WARN] Gemini Rate Limit hit (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[ERROR] Gemini API Error: {err_str}")
                    return f"// Error: {err_str}"
        
        return "// Error: Gemini Quota Exceeded after multiple retries."
