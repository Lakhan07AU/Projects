from app.main import app
routes = []
def walk(rs):
    for r in rs:
        if type(r).__name__ == "_IncludedRouter":
            walk(r.original_router.routes)
        elif hasattr(r, "methods"):
            for m in sorted(r.methods - {"HEAD", "OPTIONS"}):
                routes.append(f"{m:7s} {r.path}")
walk(app.routes)
for line in sorted(set(routes)):
    print(line)
print(f"TOTAL: {len(set(routes))}")
