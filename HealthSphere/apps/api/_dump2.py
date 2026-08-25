from app.main import app
total = 0
for r in app.routes:
    p = getattr(r, "path", "?")
    m = getattr(r, "methods", None)
    total += 1
    print(f"{sorted(m) if m else '-'} {p}")
print("TOTAL", total)
