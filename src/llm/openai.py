from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI client not installed. Run `pip install openai`.")

    def generate_code(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert C and C++ unit test generator using Google Test (gtest/gmock). "
                        "You handle free functions (C and C++), static functions, class member methods "
                        "(including private and protected), constructors, and destructors. "
                        "Always include boundary, equivalence partition, and MCDC test cases."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
