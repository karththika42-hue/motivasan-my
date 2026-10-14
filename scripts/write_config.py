import os

pexels = os.environ.get("PEXELS_API_KEY", "")
provider = (os.environ.get("LLM_PROVIDER") or "gemini").lower()
model = os.environ.get("LLM_MODEL", "")

lines = ["[app]", 'video_source = "pexels"', f'pexels_api_keys = ["{pexels}"]',
         "listen_host = \"127.0.0.1\"", "listen_port = 8080", ""]

if provider == "openrouter":
    lines += [
        'llm_provider = "openai"',
        f'openai_api_key = "{os.environ.get("OPENROUTER_API_KEY", "")}"',
        'openai_base_url = "https://openrouter.ai/api/v1"',
        f'openai_model_name = "{model or "google/gemini-2.5-flash"}"',
    ]
else:
    lines += [
        'llm_provider = "gemini"',
        f'gemini_api_key = "{os.environ.get("GEMINI_API_KEY", "")}"',
        f'gemini_model_name = "{model or "gemini-2.5-flash"}"',
    ]

with open("Turbo/config.toml", "w") as f:
    f.write("\n".join(lines) + "\n")
print("config.toml written for", provider)
