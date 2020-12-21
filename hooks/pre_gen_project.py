"""Script that runs after the project generation phase."""
import re
import sys

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

MODULE_NAME = "{{ cookiecutter.repo_name }}"

if not re.match(MODULE_REGEX, MODULE_NAME):
    print(
        f"ERROR: The project slug {MODULE_NAME} is not a valid Python module name. "
        "Please do not use a - and use _ instead."
    )

    # Exit to cancel project
    sys.exit(1)

MIN_PYTHON_VER = (3, 6)
if sys.version_info < MIN_PYTHON_VER:
    sys.exit("Python 3.6 or later is required!")