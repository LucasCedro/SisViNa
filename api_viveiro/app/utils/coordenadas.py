"""Conversão UTM (WGS84) → latitude/longitude."""
import math

_K0 = 0.9996
_A = 6378137.0
_E2 = 0.00669438
_E_PRIME2 = 0.006739497


def utm_para_latlon(easting: float, northing: float, zona: int, hemisferio_sul: bool = True) -> tuple[float, float]:
    """Converte UTM para graus decimais (WGS84)."""
    x = easting - 500000.0
    y = northing
    if hemisferio_sul:
        y -= 10000000.0

    lon_origin = (zona - 1) * 6 - 180 + 3
    m = y / _K0
    mu = m / (_A * (1 - _E2 / 4 - 3 * _E2**2 / 64 - 5 * _E2**3 / 256))

    e1 = (1 - math.sqrt(1 - _E2)) / (1 + math.sqrt(1 - _E2))
    phi1 = (
        mu
        + (3 * e1 / 2 - 27 * e1**3 / 32) * math.sin(2 * mu)
        + (21 * e1**2 / 16 - 55 * e1**4 / 32) * math.sin(4 * mu)
        + (151 * e1**3 / 96) * math.sin(6 * mu)
        + (1097 * e1**4 / 512) * math.sin(8 * mu)
    )

    n1 = _A / math.sqrt(1 - _E2 * math.sin(phi1) ** 2)
    t1 = math.tan(phi1) ** 2
    c1 = _E_PRIME2 * math.cos(phi1) ** 2
    r1 = _A * (1 - _E2) / (1 - _E2 * math.sin(phi1) ** 2) ** 1.5
    d = x / (n1 * _K0)

    lat = phi1 - (n1 * math.tan(phi1) / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * _E_PRIME2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * _E_PRIME2 - 3 * c1**2) * d**6 / 720
    )
    lon = (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * _E_PRIME2 + 24 * t1**2) * d**5 / 120
    ) / math.cos(phi1)

    lat_deg = math.degrees(lat)
    lon_deg = lon_origin + math.degrees(lon)
    return round(lat_deg, 7), round(lon_deg, 7)
