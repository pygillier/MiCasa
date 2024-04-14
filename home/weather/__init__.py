from pathlib import Path
import json


def get_icon(code: int, moment: str) -> str:
    f = Path(__file__).parent.resolve() / "mappings.json"

    with f.open() as source:
        mappings = json.loads(source.read())
        chosen = [x for x in mappings if x["code"] == code]
        if len(chosen) == 1:
            return chosen[0]["icon"][moment]
        else:
            return "na"
