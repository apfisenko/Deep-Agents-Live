import json
from pathlib import Path

sessions = {
    "start  (15:49)": "20260802T154921Z",
    "fix #1 (16:22)": "20260802T162259Z",
    "fix #2 (16:29)": "20260802T162900Z",
    "fix #3 (16:38)": "20260802T163821Z",
    "fix #4 (16:42)": "20260802T164234Z",
}
for label, name in sessions.items():
    ff = Path("workspace") / name / "output" / "final_feedback.json"
    if not ff.exists():
        continue
    d = json.loads(ff.read_text("utf-8"))
    issues = d.get("issues", [])
    req = sum(1 for i in issues if i.get("severity") == "required")
    opt = sum(1 for i in issues if i.get("severity") == "optional")
    score = round(max(0.0, 1.0 - req * 0.15 - opt * 0.05), 2)
    status = "PASS" if score >= 0.70 else "FAIL"
    print(f"{label}  score={score:.2f}  {status}  req={req} opt={opt}")

print()
print("Latest issues:")
last = Path("workspace/20260802T164234Z/output/final_feedback.json")
d = json.loads(last.read_text("utf-8"))
for i in d.get("issues", []):
    sev = i["severity"].upper()
    text = i["text"][:110]
    print(f"  [{sev:8}] {text}")
