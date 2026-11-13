"""Camera path (hand-authored presentation) and perspective projection."""
import numpy as np
from scipy.interpolate import PchipInterpolator


class Curve:
    """A scalar presentation parameter: a constant, or keys ``[[x0, v0], [x1, v1], ...]``
    joined by a monotone cubic (PCHIP).  Velocity is continuous through every key (no
    stop-start at keyframes) and there is no overshoot.  Constant before the first and
    after the last key.

    Used only for camera parameters.  Particle positions are never interpolated."""

    def __init__(self, spec):
        if spec is None or np.isscalar(spec):
            self.const = None if spec is None else float(spec)
            self.f = None
            return
        keys = sorted((float(k[0]), float(k[1])) for k in spec)
        self.x0, self.x1 = keys[0][0], keys[-1][0]
        self.v0, self.v1 = keys[0][1], keys[-1][1]
        self.const = keys[0][1] if len(keys) == 1 else None
        self.f = PchipInterpolator([k[0] for k in keys], [k[1] for k in keys]) if len(keys) > 1 else None

    def __call__(self, x):
        if self.f is None:
            return self.const
        if x <= self.x0:
            return self.v0
        if x >= self.x1:
            return self.v1
        return float(self.f(x))


class Camera:
    """Perspective camera looking at ``target`` from ``distance`` kpc.

    azimuth is measured in the x-y plane from +x, elevation above the x-y plane (degrees).
    ``fov_deg`` is the vertical field of view.
    """

    def __init__(self, target, distance, azimuth_deg, elevation_deg, fov_deg, width, height,
                 roll_deg=0.0):
        self.target = np.asarray(target, float)
        self.distance = float(distance)
        az = np.radians(azimuth_deg)
        el = np.radians(elevation_deg)
        d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        self.position = self.target + self.distance * d
        fwd = -d
        up0 = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(fwd, up0)) > 0.999:
            up0 = np.array([0.0, 1.0, 0.0])
        right = np.cross(fwd, up0)
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        if roll_deg:
            r = np.radians(roll_deg)
            right, up = (np.cos(r) * right + np.sin(r) * up, -np.sin(r) * right + np.cos(r) * up)
        self.R = np.vstack([right, up, fwd])       # world -> camera rows
        self.width = int(width)
        self.height = int(height)
        self.fov = np.radians(fov_deg)
        self.f = 0.5 * self.height / np.tan(0.5 * self.fov)

    def project(self, pos):
        """Pixel x, pixel y (pixel centres at integer + 0.5) and depth in kpc."""
        pc = (np.asarray(pos, np.float64) - self.position) @ self.R.T
        z = pc[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            px = 0.5 * self.width + self.f * pc[:, 0] / z
            py = 0.5 * self.height - self.f * pc[:, 1] / z
        return px, py, z

    def kpc_per_pixel_at_target(self):
        return self.distance / self.f
