"""Parameter files (YAML) and provenance."""
import hashlib
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_params(path):
    path = Path(path)
    raw = path.read_bytes()
    params = yaml.safe_load(raw)
    params.setdefault("name", path.stem)
    sim = params.setdefault("simulation", {})
    sim.setdefault("solver", "tree")
    sim.setdefault("theta", 0.6)
    sim.setdefault("leaf_size", 8)
    out = params.setdefault("output", {})
    out.setdefault("render", {"every_myr": 10.0})
    out.setdefault("checkpoint_every_myr", 500.0)
    return params, hashlib.sha256(raw).hexdigest()


def git_commit():
    """`git describe`-style identifier of the code that is running ("-dirty" if modified)."""
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               cwd=REPO_ROOT, capture_output=True, text=True,
                               check=True).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"
