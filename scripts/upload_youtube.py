import json
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

meta = json.load(open("output/meta.json", encoding="utf-8"))

creds = Credentials(
    None,
    refresh_token=os.environ["YT_REFRESH_TOKEN"],
    client_id=os.environ["YT_CLIENT_ID"],
    client_secret=os.environ["YT_CLIENT_SECRET"],
    token_uri="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)
yt = build("youtube", "v3", credentials=creds)

privacy = os.environ.get("YT_PRIVACY") or "private"
body = {
    "snippet": {
        "title": meta["title"][:100],
        "description": meta["description"] + "\n\n#motivation #shorts",
        "categoryId": "22",
    },
    "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
}
media = MediaFileUpload("output/video.mp4", chunksize=-1, resumable=True)
req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

resp = None
while resp is None:
    status, resp = req.next_chunk()
    if status:
        print("Uploaded", int(status.progress() * 100), "%")
print("Video id:", resp["id"], "privacy:", privacy)
