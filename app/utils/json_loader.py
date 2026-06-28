import json
from pathlib import Path
from typing import Any


def load_json_file(
    file_path: str | Path,
) -> list[dict[str, Any]]:
    """
    Load and validate a JSON file.

    Expected format:
    [
        {...},
        {...}
    ]
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist."
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "Dataset must be a JSON array."
        )

    return data