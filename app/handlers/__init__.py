from .python_runner import PythonRunner
from .typescript_runner import TypeScriptRunner
from .php_runner import PHPRunner

RUNNERS = {
    "python": PythonRunner,
    "typescript": TypeScriptRunner,
    # "php": PHPRunner
}

def get_runner(language: str):
    runner_class = RUNNERS.get(language.lower())
    if not runner_class:
        raise ValueError(f"Unsupported language: {language}")
    return runner_class()
