import datetime
import glob
import json
import os
import shutil
import sys
import time

import requests

API = "http://127.0.0.1:8080/api/v1"


def pick():
    t = json.load(open("templates.json", encoding="utf-8"))
    d = datetime.date.today().timetuple().tm_yday
    theme = t["themes"][d % len(t["themes"])]
    fmt = t["formats"][(d + d // len(t["themes"])) % len(t["formats"])]
    style = t["styles"][(d * 3 + 1) % len(t["styles"])]
    return theme, fmt, style


def ask_llm(prompt):
    provider = (os.environ.get("LLM_PROVIDER") or "gemini").lower()
    model = os.environ.get("LLM_MODEL", "")
    if provider == "openrouter":
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]},
            json={"model": model or "google/gemini-2.5-flash",
                  "messages": [{"role": "user", "content": prompt}],
                  "response_format": {"type": "json_object"}},
            timeout=120)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
    else:
        m = model or "gemini-2.5-flash"
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
            params={"key": os.environ["GEMINI_API_KEY"]},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"responseMimeType": "application/json"}},
            timeout=120)
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)


def main():
    theme, fmt, style = pick()
    print("Theme:", theme, "| Format:", fmt["name"], "| Style:", style["name"])

    prompt = f"""You write original English motivational video scripts for a YouTube channel.
Theme: {theme}
Format: {fmt['name']} - {fmt['instruction']}
Length: about {style['words']} words of spoken text.
Rules: plain spoken English, no emojis, no hashtags, no stage directions, no headings, no quotes copied from famous speeches. Fresh angle, concrete images, strong last line.
Return ONLY JSON with keys:
"title" (max 70 chars, catchy),
"description" (2 sentences),
"script" (the spoken text only),
"terms" (list of 6 short English stock-footage search terms, inspired by: {style['footage']})."""
    data = ask_llm(prompt)
    print("Title:", data["title"])

    payload = {
        "video_subject": theme,
        "video_script": data["script"],
        "video_terms": ", ".join(data["terms"]),
        "video_aspect": style["aspect"],
        "video_concat_mode": "random",
        "video_clip_duration": style["clip_duration"],
        "video_count": 1,
        "video_source": "pexels",
        "video_language": "en-US",
        "voice_name": style["voice"],
        "voice_rate": style["voice_rate"],
        "voice_volume": 1.0,
        "bgm_type": "random",
        "bgm_volume": 0.15,
        "subtitle_enabled": True,
        "subtitle_position": style["position"],
        "text_fore_color": style["font_color"],
        "stroke_color": style["stroke_color"],
        "stroke_width": 1.5,
        "font_size": style["font_size"],
        "n_threads": 2,
    }
    r = requests.post(f"{API}/videos", json=payload, timeout=60)
    r.raise_for_status()
    task_id = r.json()["data"]["task_id"]
    print("Task:", task_id)

    for _ in range(240):  # up to ~40 min
        time.sleep(10)
        info = requests.get(f"{API}/tasks/{task_id}", timeout=30).json()["data"]
        print("state", info.get("state"), "progress", info.get("progress"))
        if info.get("state") == 1:
            break
        if info.get("state") == -1:
            print("Turbo reported failure:", info)
            sys.exit(1)
    else:
        print("Timed out")
        sys.exit(1)

    files = glob.glob(f"Turbo/storage/tasks/{task_id}/final-*.mp4")
    if not files:
        print("No final video found")
        sys.exit(1)

    os.makedirs("output", exist_ok=True)
    shutil.copy(files[0], "output/video.mp4")
    json.dump({"title": data["title"], "description": data["description"],
               "theme": theme, "format": fmt["name"], "style": style["name"]},
              open("output/meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Done: output/video.mp4")


if __name__ == "__main__":
    main()
