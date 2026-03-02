import os
import json
import re
from typing import Optional, List
from dotenv import load_dotenv

from .llm.ollama import OllamaProvider
from .llm.gemini import GeminiProvider
from .llm.openai import OpenAIProvider
from .llm.mock import MockProvider

from .prompts import STRATEGY_ANALYSIS_PROMPT, TEST_BODY_PROMPT

# Load .env file
load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("LLM_API_KEY")
        provider_pref = os.getenv("LLM_PROVIDER", "").lower()
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

        # 1. Explicit preference
        if provider_pref == "ollama":
            print(f"[INFO] Using Ollama Provider ({ollama_model}).")
            self.provider = OllamaProvider(model=ollama_model)
            return
        elif provider_pref == "gemini" and api_key:
            self.provider = GeminiProvider(api_key)
            print("[INFO] Using Gemini Provider.")
            return
        elif provider_pref == "openai" and api_key:
            self.provider = OpenAIProvider(api_key)
            print("[INFO] Using OpenAI Provider.")
            return
        elif provider_pref == "mock":
            print("[INFO] Using Mock Provider.")
            self.provider = MockProvider()
            return

        # 2. Key-based detection (legacy logic)
        if api_key:
            if api_key.startswith("AIza"):
                self.provider = GeminiProvider(api_key)
                print("[INFO] Using Gemini Provider.")
                return
            elif api_key.startswith("sk-"):
                self.provider = OpenAIProvider(api_key)
                print("[INFO] Using OpenAI Provider.")
                return

        # 3. Auto-detect Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                if ollama_model not in models and ":" not in ollama_model:
                    match = next((m for m in models if m.startswith(ollama_model)), None)
                    if match:
                        ollama_model = match
                if any(m.startswith(ollama_model) for m in models):
                    print(f"[INFO] Auto-detected Ollama at localhost. Using {ollama_model}.")
                    self.provider = OllamaProvider(model=ollama_model)
                    return
        except Exception:
            pass

        # 4. Fallback to Mock
        print("[WARN] No valid LLM provider found. Using Mock Provider.")
        self.provider = MockProvider()

    def generate_test_body(self, function_signature: str, strategy: dict) -> str:
        prompt = self._construct_prompt(function_signature, strategy)
        try:
            return self.provider.generate_code(prompt)
        except Exception as e:
            print(f"[ERROR] LLM Generation failed: {e}")
            return f"// Error: {e}"

    def identify_test_strategy(self, signature: str, body_code: str, language: str, technical_context: dict) -> List[str]:
        """
        Asks the LLM to analyze code logic and unify it with technical requirements 
        (boundaries, EP, mocks, etc.) into a single master test strategy.
        """
        boundary_txt = "\n".join([f"- {c}" for c in technical_context.get("boundary_cases", [])])
        ep_txt = "\n".join([f"- {c}" for c in technical_context.get("equivalence_partition_cases", [])])
        mocks_txt = "\n".join([f"- {c}" for c in technical_context.get("mocks_needed", [])])
        mcdc_txt = "\n".join([f"- {c}" for c in technical_context.get("mcdc_cases", [])])

        prompt = STRATEGY_ANALYSIS_PROMPT.format(
            language=language,
            signature=signature,
            body_code=body_code,
            boundary_txt=boundary_txt or "None identified",
            ep_txt=ep_txt or "None identified",
            mocks_txt=mocks_txt or "None identified",
            mcdc_txt=mcdc_txt or "None identified"
        )
        try:
            response = self.provider.generate_code(prompt)
            # Try to parse as JSON list
            resp_text = response.strip()
            
            # 1. Try to find a JSON list anywhere in the response
            json_match = re.search(r'\[\s*".*"\s*\]', resp_text, re.DOTALL)
            if json_match:
                try:
                    cases = json.loads(json_match.group(0))
                    if isinstance(cases, list):
                        return [str(c) for c in cases]
                except:
                    pass
            
            # 2. Try to find a JSON block via markdown tags
            if "```json" in resp_text:
                json_block = resp_text.split("```json")[1].split("```")[0].strip()
                try:
                    cases = json.loads(json_block)
                    if isinstance(cases, list):
                        return [str(c) for c in cases]
                except:
                    pass

            # 3. Fallback: Parse bullet points
            bullet_matches = re.findall(r'(?:^|\n)(?:[-*]|\d+\.)\s*(.+)', resp_text)
            if bullet_matches:
                return [m.strip() for m in bullet_matches]
            
            # 4. Final fallback: If response is short enough and has multiple lines, treat each line as a case
            lines = [l.strip() for l in resp_text.split('\n') if l.strip() and not l.startswith('```')]
            if 0 < len(lines) < 10:
                return lines

            return ["Deep Logic Analysis (LLM response format not recognized)"]
        except Exception as e:
            print(f"[ERROR] Logic strategy identification failed for {signature}: {e}")
            return [f"Error identifying strategy: {e}"]

    def _construct_prompt(self, signature: str, strategy: dict) -> str:
        language = strategy.get("language", "C++")
        kind = strategy.get("kind", "free_function")
        is_static = strategy.get("is_static", False)
        access_spec = strategy.get("access_specifier", "none")
        class_name = strategy.get("class_name", "")

        # Build bullet lists
        cases_txt = "\n".join(
            [f"- {c}" for c in strategy.get("suggested_test_cases", [])]
        )
        
        # Optional baseline context if still provided
        boundary_txt = "\n".join([f"- {c}" for c in strategy.get("boundary_cases", [])])
        ep_txt = "\n".join([f"- {c}" for c in strategy.get("equivalence_partition_cases", [])])
        baseline_info = ""
        if boundary_txt or ep_txt:
            baseline_info = f"\nTechnical baseline for reference:\n{boundary_txt}\n{ep_txt}\n"

        # Calling convention hints
        fixture_context = ""
        if class_name and class_name not in ("UnknownClass", ""):
            if is_static:
                fixture_context = (
                    f"This is a STATIC method of class `{class_name}`. "
                    f"Call it as `{class_name}::{signature.split('(')[0].split()[-1]}(...)`."
                )
            elif access_spec in ("private", "protected"):
                fixture_context = (
                    f"This is a {access_spec.upper()} method of class `{class_name}`. "
                    f"Test it via the public API, a friend test class, or a test-only subclass."
                )
            else:
                fixture_context = (
                    f"Assume you are inside a Google Test fixture that has an instance of "
                    f"`{class_name}` named `obj`. Use `obj.<method>(...)` to call member functions."
                )

        return TEST_BODY_PROMPT.format(
            language=language,
            signature=signature,
            kind=kind,
            cases_txt=cases_txt,
            baseline_info=baseline_info,
            mocks_needed=strategy.get('mocks_needed', []),
            fixture_context=fixture_context
        )
