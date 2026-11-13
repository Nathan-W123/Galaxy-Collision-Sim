"""Render simulation snapshots to PNG frames and an MP4.

    python -m render.render render/configs/preview_5k.yaml [--workers 4] [--no-video]

Reads *only* snapshot files (plus the run's static particle table and metadata).
One snapshot per frame: particle positions are drawn exactly as the integrator wrote
them -- no interpolation, no tweening, no frame blending.  Hand-authored presentation
is limited to the camera path, colours, glow and overlays.  The on-screen time is read
from the snapshot.

How a frame is drawn
--------------------
1. Star particles (disk + bulge; dark matter hidden) are loaded from the snapshot.
2. Each particle gets a smoothing length from the distance to its k-th nearest
   neighbour in 3D (adaptive kernel density estimation, as in SPH visualisation): dense
   disks render sharp, sparse tidal debris renders soft, and nothing looks like a
   field of dots.
3. Each particle's light (proportional to its mass) is deposited as a normalised
   Gaussian of that width, projected through a perspective camera, on a supersampled
   canvas.  Wide kernels go to coarser levels of an image pyramid, so cost per particle
   stays bounded; the levels are upsampled and summed.  Image values are surface
   densities (Msun / kpc^2), independent of camera distance.
4. Log-density tone mapping with a filmic (ACES-style) curve; colour by galaxy of
   origin (bulges paler); highlights desaturate towards white.
5. Bloom from highlights only, at three radii; screen-blended over a dark background.
6. Overlay (time from the snapshot, legend, scale bar, provenance tag), see overlay.py.

Writes ``frames_manifest.csv`` (frame -> snapshot file, step, time, energy, plus the
simulation's git commit and parameter-file hash) next to the frames.
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import yaml
from numba import njit
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from nbody.io import PTYPE_BULGE, PTYPE_DISK, read_json, read_snapshot, read_static  # noqa: E402
from nbody.params import git_commit  # noqa: E402
from render.camera import Camera, Curve  # noqa: E402
from render.overlay import draw_overlay  # noqa: E402

DEFAULT_STYLE = {
    "supersample": 2,
    "knn": 16,                  # neighbours defining the smoothing length
    "kernel_scale": 0.5,        # Gaussian sigma = kernel_scale * (distance to k-th neighbour)
    "h_min_kpc": 0.03,
    "h_max_kpc": 4.0,
    "min_sigma_px": 0.75,       # in supersampled pixels (anti-aliasing floor)
    "density_lo": 1.0e6,        # Msun/kpc^2 at the bottom of the log scale
    "density_hi": 3.0e9,        # Msun/kpc^2 at the top of the log scale
    "exposure": 1.25,
    "highlight_desat": 0.7,
    "colors": [                 # sRGB 0-1: [disk, bulge] per galaxy of origin
        [[0.47, 0.66, 1.00], [0.80, 0.87, 1.00]],     # cool blue
        [[1.00, 0.66, 0.36], [1.00, 0.86, 0.68]],     # warm amber
    ],
    "bloom": {"threshold": 0.45, "strength": 0.55,
              "radii": [0.004, 0.012, 0.035], "weights": [0.5, 0.32, 0.18]},
    "background": [7, 9, 15],
    "vignette": 0.18,
    "dither": True,
}


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------- kernels
@njit(cache=True)
def deposit_gaussian(x, y, sig, w, ch, out, rmax):
    """Add normalised, separable Gaussians (sum of weights == w) to out[ch, y, x].

    Pixel centres are at integer + 0.5.  Normalising by the discrete kernel sum keeps the
    flux exact and makes sub-pixel motion smooth even for narrow kernels."""
    C, H, W = out.shape
    gx = np.empty(2 * rmax + 3)
    gy = np.empty(2 * rmax + 3)
    for k in range(x.shape[0]):
        s = sig[k]
        r = int(np.ceil(3.0 * s))
        if r > rmax:
            r = rmax
        xc = x[k]
        yc = y[k]
        ix0 = int(np.floor(xc)) - r
        iy0 = int(np.floor(yc)) - r
        n = 2 * r + 1
        if ix0 + n < 0 or iy0 + n < 0 or ix0 >= W or iy0 >= H:
            continue
        inv = 0.5 / (s * s)
        sx = 0.0
        sy = 0.0
        for i in range(n):
            d = ix0 + i + 0.5 - xc
            gx[i] = np.exp(-d * d * inv)
            sx += gx[i]
            d = iy0 + i + 0.5 - yc
            gy[i] = np.exp(-d * d * inv)
            sy += gy[i]
        norm = w[k] / (sx * sy)
        c = ch[k]
        for j in range(n):
            yy = iy0 + j
            if yy < 0 or yy >= H:
                continue
            a = gy[j] * norm
            for i in range(n):
                xx = ix0 + i
                if xx < 0 or xx >= W:
                    continue
                out[c, yy, xx] += a * gx[i]


@njit(cache=True)
def upsample2(a, H, W):
    """Bilinear 2x upsampling with pixel-centre alignment, cropped to (H, W)."""
    C, h, w = a.shape
    out = np.empty((C, H, W), a.dtype)
    for c in range(C):
        for j in range(H):
            sy = (j + 0.5) * 0.5 - 0.5
            y0 = int(np.floor(sy))
            fy = sy - y0
            y1 = min(max(y0 + 1, 0), h - 1)
            y0 = min(max(y0, 0), h - 1)
            for i in range(W):
                sx = (i + 0.5) * 0.5 - 0.5
                x0 = int(np.floor(sx))
                fx = sx - x0
                x1 = min(max(x0 + 1, 0), w - 1)
                x0 = min(max(x0, 0), w - 1)
                out[c, j, i] = ((1 - fy) * ((1 - fx) * a[c, y0, x0] + fx * a[c, y0, x1])
                                + fy * ((1 - fx) * a[c, y1, x0] + fx * a[c, y1, x1]))
    return out


def downsample(a, f):
    C, H, W = a.shape
    return a.reshape(C, H // f, f, W // f, f).mean(axis=(2, 4))


def aces(x):
    return np.clip(x * (2.51 * x + 0.03) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0)


# ------------------------------------------------------------------- renderer
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.run_dir = _abs(cfg["run"])
        self.meta = read_json(self.run_dir / "run_meta.json")
        st = read_static(self.run_dir / "static.npz")
        self.ptype = st["ptype"]
        self.galaxy = st["galaxy"]
        self.mass = st["mass"]
        self.galaxy_names = [str(x) for x in st["galaxy_names"]]
        self.style = {**DEFAULT_STYLE, **cfg.get("style", {})}
        self.style["bloom"] = {**DEFAULT_STYLE["bloom"], **cfg.get("style", {}).get("bloom", {})}
        stars = np.isin(self.ptype, [PTYPE_DISK, PTYPE_BULGE])
        if self.style.get("show_dark_matter", False):
            stars[:] = True
        self.sel = np.nonzero(stars)[0]
        self.ng = int(self.galaxy.max()) + 1
        # channel = 2 * galaxy + (1 if bulge else 0)
        self.chan = (2 * self.galaxy[self.sel].astype(np.int64)
                     + (self.ptype[self.sel] == PTYPE_BULGE).astype(np.int64))
        self.W = int(cfg["width"])
        self.H = int(cfg["height"])
        if self.W % 2 or self.H % 2:
            raise ValueError("width and height must be even (H.264 yuv420p)")
        self.ss = int(self.style["supersample"])
        self.fps = int(cfg.get("fps", 30))
        self.out_dir = _abs(cfg["out"])
        cam = cfg.get("camera", {})
        self.cam_key = cam.get("key", "time_gyr")
        self.c_dist = Curve(cam.get("distance_kpc", 150.0))
        self.c_elev = Curve(cam.get("elevation_deg", 30.0))
        self.c_azk = Curve(cam.get("azimuth_keys", 0.0))
        self.az0 = float(cam.get("azimuth_deg", 0.0))
        self.az_rate = float(cam.get("azimuth_rate_deg_per_frame", 0.0))
        self.fov = float(cam.get("fov_deg", 40.0))
        tgt = cam.get("target", [0.0, 0.0, 0.0])
        self.c_tgt = [Curve(v) for v in tgt] if not isinstance(tgt, str) else None
        self.frames = self.plan_frames()

    # ------------------------------------------------------------ frame plan
    def plan_frames(self):
        """List of (frame_index, step).  Each frame is exactly one saved snapshot."""
        steps = np.asarray(self.meta["render_steps"], dtype=np.int64)
        dt_gyr = self.meta["dt_internal"] * self.meta["time_unit_gyr"]
        fr = self.cfg.get("frames", {})
        t = steps * dt_gyr
        sel = np.ones(steps.size, bool)
        if "start_gyr" in fr:
            sel &= t >= float(fr["start_gyr"]) - 1e-9
        if "end_gyr" in fr:
            sel &= t <= float(fr["end_gyr"]) + 1e-9
        steps = steps[sel]
        snap_dir = self.run_dir / "snapshots"
        steps = [int(s) for s in steps if (snap_dir / f"snap_{int(s):07d}.npz").exists()]
        return list(enumerate(steps))

    # ------------------------------------------------------------ camera
    def camera_for(self, frame, t_gyr, ss=1):
        x = t_gyr if self.cam_key == "time_gyr" else frame
        tgt = [c(x) for c in self.c_tgt] if self.c_tgt else [0.0, 0.0, 0.0]
        az = self.az0 + self.az_rate * frame + self.c_azk(x)
        return Camera(tgt, self.c_dist(x), az, self.c_elev(x), self.fov, self.W * ss, self.H * ss)

    # ------------------------------------------------------------ light
    def splat(self, pos, cam):
        st = self.style
        ss = self.ss
        Hs, Ws = self.H * ss, self.W * ss
        m = self.mass[self.sel]
        k = int(st["knn"])
        tree = cKDTree(pos)
        dist, _ = tree.query(pos, k=min(k + 1, len(pos)))
        h = np.clip(dist[:, -1] * float(st["kernel_scale"]), st["h_min_kpc"], st["h_max_kpc"])
        px, py, z = cam.project(pos)
        ok = z > 1e-3
        px, py, z, h, m, ch = px[ok], py[ok], z[ok], h[ok], m[ok], self.chan[ok]
        sig = np.maximum(h * cam.f / z, float(st["min_sigma_px"]))
        # surface density contributed (Msun / kpc^2 per supersampled pixel, before the kernel)
        w = m * 1e10 * (cam.f / z) ** 2
        # pyramid level: keep sigma <= 3 px at the level the particle is drawn on
        lev = np.clip(np.ceil(np.log2(np.maximum(sig / 3.0, 1.0))), 0, 6).astype(np.int64)
        C = 2 * self.ng
        acc = None
        for L in range(int(lev.max()), -1, -1):
            f = 2 ** L
            hL, wL = -(-Hs // f), -(-Ws // f)
            buf = np.zeros((C, hL, wL))
            s = lev == L
            if s.any():
                deposit_gaussian(px[s] / f, py[s] / f, sig[s] / f, w[s] / (f * f), ch[s], buf, 12)
            acc = buf if acc is None else upsample2(acc, hL, wL) + buf
        return downsample(acc, ss)          # (C, H, W) surface densities

    def shade(self, dens, frame):
        st = self.style
        cols = np.asarray(st["colors"], float)[: self.ng].reshape(-1, 3)        # (C, 3)
        D = dens.sum(0)
        lo, hi = float(st["density_lo"]), float(st["density_hi"])
        Lg = np.log1p(np.maximum(D, 0) / lo) / np.log1p(hi / lo)
        T = aces(float(st["exposure"]) * Lg)
        hue = np.einsum("chw,ck->hwk", dens, cols) / np.maximum(D, 1e-30)[..., None]
        rgb = hue * T[..., None]
        s = (np.clip((T - 0.55) / 0.45, 0, 1) ** 1.5 * float(st["highlight_desat"]))[..., None]
        rgb = rgb * (1 - s) + T[..., None] * s
        # bloom from highlights, computed at quarter resolution
        b = st["bloom"]
        if float(b["strength"]) > 0:
            thr = float(b["threshold"])
            hl = np.clip((rgb - thr) / (1 - thr), 0, None)
            q = 4
            Hq, Wq = self.H // q, self.W // q
            small = hl[: Hq * q, : Wq * q].reshape(Hq, q, Wq, q, 3).mean(axis=(1, 3))
            bl = np.zeros_like(small)
            for rad, wt in zip(b["radii"], b["weights"]):
                sgm = max(rad * self.H / q, 0.5)
                for c in range(3):
                    bl[..., c] += float(wt) * gaussian_filter(small[..., c], sgm, mode="constant")
            up = bl.transpose(2, 0, 1)
            for _ in range(2):
                up = upsample2(np.ascontiguousarray(up), up.shape[1] * 2, up.shape[2] * 2)
            full = np.zeros((3, self.H, self.W))
            full[:, : up.shape[1], : up.shape[2]] = up[:, : self.H, : self.W]
            bloom = np.clip(full.transpose(1, 2, 0) * float(b["strength"]), 0, 1)
            rgb = 1 - (1 - np.clip(rgb, 0, 1)) * (1 - bloom)
        bg = np.asarray(st["background"], float) / 255.0
        out = 1 - (1 - bg) * (1 - np.clip(rgb, 0, 1))
        v = float(st.get("vignette", 0))
        if v > 0:
            yy, xx = np.mgrid[0:self.H, 0:self.W]
            r2 = ((xx + 0.5) / self.W - 0.5) ** 2 + ((yy + 0.5) / self.H - 0.5) ** 2
            out *= (1 - v * np.clip(r2 / 0.5, 0, 1))[..., None]
        if st.get("dither", True):
            rng = np.random.default_rng(1_000_003 + frame)
            out += (rng.random(out.shape) - 0.5) / 255.0
        return np.clip(out, 0, 1)

    # ------------------------------------------------------------ one frame
    def render_frame(self, frame, step):
        snap_path = self.run_dir / "snapshots" / f"snap_{step:07d}.npz"
        snap = read_snapshot(snap_path)
        assert int(snap["step"]) == step
        pos = snap["pos"][self.sel].astype(np.float64)
        t_gyr = float(snap["time_gyr"])
        cam = self.camera_for(frame, t_gyr, self.ss)
        dens = self.splat(pos, cam)
        img = self.shade(dens, frame)
        im = Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB")
        ov = dict(self.cfg.get("overlay", {}))
        ov["_bg"] = self.style["background"]
        colors = [c[0] for c in self.style["colors"]]
        n_part = int(self.meta.get("n_particles", len(self.mass)))
        im = draw_overlay(im, ov, t_gyr, self.camera_for(frame, t_gyr, 1).kpc_per_pixel_at_target(),
                          colors, self.galaxy_names, frame, n_part)
        return im, snap


# ---------------------------------------------------------------- driver
_R = None


def _init(cfg):
    global _R
    _R = Renderer(cfg)


def _work(item):
    frame, step = item
    im, snap = _R.render_frame(frame, step)
    path = _R.out_dir / "frames" / f"{frame:05d}.png"
    im.save(path, compress_level=1)
    return frame, step, float(snap["time_gyr"]), float(snap["energy"])


def encode_video(frames_dir, fps, out_mp4, crf=16):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
           "-i", str(Path(frames_dir) / "%05d.png"), "-c:v", "libx264", "-preset", "slow",
           "-crf", str(crf), "-tune", "film", "-pix_fmt", "yuv420p", "-r", str(fps),
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-movflags", "+faststart", str(out_mp4)]
    subprocess.run(cmd, check=True)


def render(cfg_path, workers=4, video=True):
    cfg = yaml.safe_load(Path(cfg_path).read_text())
    R = Renderer(cfg)
    out = R.out_dir
    (out / "frames").mkdir(parents=True, exist_ok=True)
    for old in (out / "frames").glob("*.png"):
        old.unlink()
    print(f"rendering {len(R.frames)} frames from {R.run_dir} -> {out}", flush=True)
    with ProcessPoolExecutor(workers, initializer=_init, initargs=(cfg,)) as ex:
        results = sorted(ex.map(_work, R.frames, chunksize=2))
    meta = R.meta
    rows = []
    for frame, step, tg, E in results:
        rows.append({
            "frame": frame,
            "snapshot_file": os.path.relpath(R.run_dir / "snapshots" / f"snap_{step:07d}.npz", REPO),
            "step": step,
            "time_gyr": f"{tg:.9f}",
            "total_energy": f"{E:.12e}",
            "sim_git_commit": meta["git_commit"],
            "param_sha256": meta["param_sha256"],
        })
    with open(out / "frames_manifest.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    side = {
        "run_dir": os.path.relpath(R.run_dir, REPO),
        "run_name": meta["name"],
        "sim_git_commit": meta["git_commit"],
        "param_file": meta["param_file"],
        "param_sha256": meta["param_sha256"],
        "schedule_file": meta.get("schedule_file"),
        "schedule_sha256": meta.get("schedule_sha256"),
        "render_git_commit": git_commit(),
        "render_config": str(cfg_path),
        "render_config_sha256": sha256_file(cfg_path),
        "n_frames": len(rows),
        "fps": R.fps,
        "width": R.W,
        "height": R.H,
    }
    with open(out / "frames_manifest.json", "w") as fh:
        json.dump(side, fh, indent=2)
    if video:
        mp4 = out / cfg.get("video_name", "clip.mp4")
        encode_video(out / "frames", R.fps, mp4, int(cfg.get("crf", 16)))
        print("wrote", mp4)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args(argv)
    render(a.config, a.workers, not a.no_video)


if __name__ == "__main__":
    main()
