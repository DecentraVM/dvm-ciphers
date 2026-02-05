import json
from app.main import executor_handler


def handler(event, context):
    """
    Lambda-compatible handler that normalizes input
    before passing it to the executor.
    """

    # If event is a raw JSON string
    if isinstance(event, str):
        try:
            return executor_handler(json.loads(event))
        except json.JSONDecodeError:
            return executor_handler(event)

    # If event is a dict with a body (API Gateway / Lambda proxy)
    if isinstance(event, dict):
        if "body" in event:
            try:
                return executor_handler(json.loads(event["body"]))
            except json.JSONDecodeError:
                return executor_handler({})
        return executor_handler(event)

    # Fallback for any other input type
    return executor_handler(event)
