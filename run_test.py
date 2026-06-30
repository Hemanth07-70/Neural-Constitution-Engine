import subprocess

result = subprocess.run(
    ["pytest", "backend/tests/api/test_routes.py::test_evaluate_plan"], capture_output=True, text=True
)
for line in result.stdout.split("\n"):
    if "backend/tests/api/test_routes.py" in line or "Error" in line or "E   " in line:
        print(line)
