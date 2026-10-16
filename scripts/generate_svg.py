
import os
import uuid
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

COUNT = 10
source = Path("source.svg")
output_dir = Path("generated")

if not source.is_file():
    raise SystemExit("ERROR: source.svg was not found.")

content = source.read_text(encoding="utf-8").lstrip("\ufeff").strip()

try:
    root = ET.fromstring(content)
except ET.ParseError as exc:
    raise SystemExit(f"ERROR: Invalid SVG/XML: {exc}")

if root.tag.split("}")[-1].lower() != "svg":
    raise SystemExit("ERROR: The root element must be <svg>.")

repo = os.environ["GITHUB_REPOSITORY"]
branch = os.environ.get("GITHUB_REF_NAME", "main")
output_dir.mkdir(parents=True, exist_ok=True)

created = []

for _ in range(COUNT):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"{stamp}_{uuid.uuid4().hex[:16]}.svg"
    output_path = output_dir / filename
    output_path.write_text(content + "\n", encoding="utf-8")

    cdn_url = (
        f"https://cdn.jsdelivr.net/gh/"
        f"{repo}@{branch}/generated/{filename}"
    )
    created.append((filename, cdn_url))

subprocess.run(["git", "add", "generated/"], check=True)

subprocess.run([
    "git", "-c", "user.name=github-actions[bot]",
    "-c",
    "user.email=41898282+github-actions[bot]@users.noreply.github.com",
    "commit", "-m", f"Generate {COUNT} SVG files"
], check=True)

subprocess.run(["git", "push"], check=True)

print(f"\nSUCCESS: GENERATED {COUNT} SVG FILES")
print("\nJSDELIVR LINKS")

for number, (filename, url) in enumerate(created, start=1):
    print(f"{number}. {url}")
