"""Internal unit system: kpc, km/s, 1e10 Msun.

Time unit = kpc / (km/s) ~= 0.9778 Gyr.
"""

# Gravitational constant in kpc (km/s)^2 / (1e10 Msun).  This is the value used by
# GADGET-2 (Springel 2005) and requested in the project brief.  The CODATA-2018 value
# with IAU-2015 solar mass gives 43009.2; the 0.005 % difference is irrelevant here.
G = 43007.1

KPC_KM = 3.0856775814913673e16          # km in one kpc
GYR_S = 3.15576e16                      # seconds in one Julian Gyr
TIME_UNIT_GYR = KPC_KM / GYR_S          # 0.97779... Gyr per internal time unit
TIME_UNIT_MYR = TIME_UNIT_GYR * 1e3
MASS_UNIT_MSUN = 1e10


def gyr_to_internal(t_gyr):
    return t_gyr / TIME_UNIT_GYR


def internal_to_gyr(t):
    return t * TIME_UNIT_GYR


def myr_to_internal(t_myr):
    return t_myr / TIME_UNIT_MYR
