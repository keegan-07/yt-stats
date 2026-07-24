"""Poll public YouTube stats for each channel in channels.json -> stats/<name>.csv"""
import csv, datetime, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
channels = json.loads((ROOT / "channels.json").read_text(encoding="utf-8"))
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

for name, cid in channels.items():
    url = f"https://www.youtube.com/channel/{cid}/shorts"
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", url],
                       capture_output=True, text=True)
    if not r.stdout.strip():
        print(f"{name}: FAILED\n{r.stderr[-800:]}", file=sys.stderr)
        continue
    data = json.loads(r.stdout)
    subs = data.get("channel_follower_count")
    out = ROOT / "stats" / f"{name}.csv"
    new = not out.exists()
    with open(out, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["utc", "video_id", "title", "views", "channel_subs"])
        for e in data.get("entries", []):
            w.writerow([now, e["id"], (e.get("title") or "")[:60], e.get("view_count"), subs])
    print(name, "ok:", len(data.get("entries", [])), "videos,", subs, "subs")
