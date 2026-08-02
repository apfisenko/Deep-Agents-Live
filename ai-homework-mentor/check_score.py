"""Запустить проверку course-companion и показать delta score."""
from homework_mentor.pipeline import run_homework_session

PREV_SCORE = 0.60
THRESHOLD = 0.70
TARGET = "c:/FISENKO/AI/Deep-Agents-Live/course-companion"

result = run_homework_session(
    raw_text=TARGET,
    explicit_path=TARGET,
    topic_extractor=lambda _: "multi-agent",
)

ff = result.final_feedback
fp = result.fix_plan

issues = ff.issues if ff else []
req = sum(1 for i in issues if i.severity == "required")
opt = sum(1 for i in issues if i.severity == "optional")
score = round(max(0.0, 1.0 - req * 0.15 - opt * 0.05), 2)
status = "PASS" if score >= THRESHOLD else "FAIL"
delta = round(score - PREV_SCORE, 2)
delta_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"

print()
print("=" * 50)
print(f"  PREV : {PREV_SCORE:.2f}  |  NOW: {score:.2f} / 1.00  {status}")
print(f"  DELTA: {delta_str}  (required={req}, optional={opt})")
print("=" * 50)
print()

if ff:
    print("Issues:")
    for i in issues:
        print(f"  [{i.severity.upper():8}] ({i.aspect}) {i.text[:110]}")
print()

if fp and fp.required:
    print("Fix plan (required):")
    for item in fp.required:
        print(f"  {item.priority}. {item.action[:110]}")

print()
print("--- full reply (first 1500 chars) ---")
print(result.reply[:1500])
