import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def load_yaml(name):
    return yaml.safe_load((REPO / "scenarios" / name).read_text())


def write_params(tmp_path, params, fname="params.yaml"):
    p = Path(tmp_path) / fname
    p.write_text(yaml.safe_dump(params, sort_keys=False))
    return p


@pytest.fixture
def collision_params():
    return copy.deepcopy(load_yaml("test_collision_5k.yaml"))
