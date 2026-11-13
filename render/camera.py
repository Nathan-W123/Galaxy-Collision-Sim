"""Camera path (hand-authored presentation) and perspective projection."""
import numpy as np


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def keyframed(keys, x):
    """Piecewise smoothstep interpolation of ``[[x0, v0], [x1, v1], ...]`` at ``x``.

    Used only for camera parameters (presentation).  Particle positions are never
    interpolated."""
    if np.isscalar(keys):
        return float(keys)
    keys = sorted((float(k[0]), np.asarray(k[1], float)) for k in keys)
    if x <= keys[0][0]:
        return keys[0][1]
    for (x0, v0), (x1, v1) in zip(keys, keys[1:]):
        if x <= x1:
            s = smoothstep((x - x0) / (x1 - x0)) if x1 > x0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


class Camera:
    """Orbiting perspective camera.

    azimuth/elevation in degrees (azimuth measured in the x-y plane from +x,
    elevation above the x-y plane), distance in kpc from ``target``.
    """

    def __init__(self, target, distance, azimuth_deg, elevation_deg, fov_deg, width, height,
                 roll_deg=0.0):
        self.target = np.asarray(target, float)
        self.distance = float(distance)
        az = np.radians(azimuth_deg)
        el = np.radians(elevation_deg)
        # unit vector from target to camera
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
        self.fov = np.radians(fov_deg)            # vertical field of view
        self.f = 0.5 * self.height / np.tan(0.5 * self.fov)

    def project(self, pos):
        """Return pixel x, pixel y, depth (kpc) for world positions (N,3)."""
        pc = (np.asarray(pos, np.float64) - self.position) @ self.R.T
        z = pc[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            px = 0.5 * self.width + self.f * pc[:, 0] / z
            py = 0.5 * self.height - self.f * pc[:, 1] / z
        return px, py, z

    def kpc_per_pixel_at_target(self):
        return self.distance / self.f
