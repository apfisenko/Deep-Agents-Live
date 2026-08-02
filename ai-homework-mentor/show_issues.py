import json
from pathlib import Path

for session in ["20260802T154921Z", "20260802T161043Z"]:
    print(f"=== {session} ===")
    ff_path = Path("workspace") / session / "output" / "final_feedback.json"
    d = json.loads(ff_path.read_text("utf-8"))
    for i in d.get("issues", []):
        sev = i["severity"].upper()
        aspect = i.get("aspect", "?")
        text = i["text"][:105]
        print(f"  [{sev:8}] {aspect:15} {text}")
    print()
