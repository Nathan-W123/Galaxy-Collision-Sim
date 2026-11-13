"""Render -> manifest -> verify pipeline, including tamper detection."""
import csv
import shutil

import yaml

from conftest import load_yaml, write_params
from nbody.run import run
from render.render import render
from render.verify import verify


def test_render_and_verify(tmp_path):
    p = load_yaml("test_collision_5k.yaml")
    p["output"]["render"] = {"every_myr": 1}
    run_dir = run(write_params(tmp_path, p), out_root=tmp_path / "runs", n_steps_override=24,
                  name="tiny", quiet=True)
    cfg = {"run": str(run_dir), "out": str(tmp_path / "clip"), "width": 160, "height": 200,
           "fps": 30, "camera": {"distance_kpc": 250, "elevation_deg": 40,
                                 "azimuth_rate_deg_per_frame": 0.5, "fov_deg": 40}}
    cfg_path = tmp_path / "render.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))
    out = render(cfg_path, workers=2)
    clip = out / "clip.mp4"
    ok, report = verify(clip, rerender=2, render_config=str(cfg_path))
    print(report)
    assert ok
    rows = list(csv.DictReader(open(out / "frames_manifest.csv")))
    assert len(rows) == 25 and rows[0]["step"] == "0" and rows[-1]["step"] == "24"

    # tamper 1: a snapshot goes missing
    victim = run_dir / "snapshots" / "snap_0000010.npz"
    shutil.move(victim, tmp_path / "moved.npz")
    ok, report = verify(clip)
    assert not ok and "FAIL every manifest row points to an existing snapshot" in report
    shutil.move(tmp_path / "moved.npz", victim)

    # tamper 2: manifest claims a time order the snapshots do not have
    rows2 = [dict(r) for r in rows]
    rows2[5]["step"], rows2[6]["step"] = rows2[6]["step"], rows2[5]["step"]
    rows2[5]["snapshot_file"], rows2[6]["snapshot_file"] = rows2[6]["snapshot_file"], rows2[5]["snapshot_file"]
    bad = out / "bad_manifest.csv"
    with open(bad, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows2[0].keys()))
        w.writeheader()
        w.writerows(rows2)
    ok, report = verify(clip, manifest=bad)
    assert not ok and "FAIL simulation time never decreases" in report
