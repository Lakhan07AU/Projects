from app.main import app
for r in app.routes:
    if not hasattr(r, "methods"):
        print(type(r), repr(r)[:120])
