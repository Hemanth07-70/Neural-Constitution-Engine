from backend.api.app import create_app

app = create_app()
for r in app.routes:
    if type(r).__name__ == "_IncludedRouter":
        print("Found _IncludedRouter!")
        print(dir(r))
        break
