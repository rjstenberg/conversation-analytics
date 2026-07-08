import json
from pathlib import Path


def load_people(path="data/people.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_mapping(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))