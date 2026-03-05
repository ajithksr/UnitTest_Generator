from .base import LLMProvider

class AzureOpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, endpoint: str, version: str, deployment: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.version = version
        self.deployment = deployment
        try:
            import openai
            self.client = openai.AzureOpenAI(
                api_key=api_key,
                api_version=version,
                azure_endpoint=endpoint
            )
        except ImportError:
            raise ImportError("OpenAI client not installed. Run `pip install openai`.")

    def generate_code(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.deployment,
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
