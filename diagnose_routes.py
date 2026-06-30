from backend.api.app import create_app

try:
    app = create_app()
    print(f"Total routes in app.routes: {len(app.routes)}")
    for i, route in enumerate(app.routes):
        print(f"Route {i}: type={type(route).__name__} (module={type(route).__module__})")
        if hasattr(route, "path"):
            print(f"  path={route.path}")
        if hasattr(route, "methods"):
            print(f"  methods={route.methods}")
except Exception as e:
    print(f"Error: {e}")
