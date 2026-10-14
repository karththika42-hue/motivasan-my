# Motivation Bot

Daily English motivation video: LLM writes the script, MoneyPrinterTurbo builds the video, YouTube upload (private by default).

## Secrets (Settings > Secrets and variables > Actions > Secrets)
- PEXELS_API_KEY
- GEMINI_API_KEY (or OPENROUTER_API_KEY)
- YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (only for auto-upload)

## Variables (same page > Variables tab)
- LLM_PROVIDER = openrouter (optional, default is gemini)
- LLM_MODEL (optional)
- YT_PRIVACY = public / unlisted / private (default private)

## Run
Actions tab > Daily Motivation Video > Run workflow. The video is also saved as an artifact.
