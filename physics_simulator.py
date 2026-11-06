"""
Deterministic local physics simulator for development, demos, and CPU deploys.

This is NOT a trained PINN. Production inference uses a separate Triton /
Modulus cluster when INFERENCE_MODE=triton and TRITON_CLUSTER_URL is set.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np


def simulate_flow_field(
    domain_points: list[list[float]],
    inlet_velocity_mps: float = 10.0,
    temperature_kelvin: float = 288.15,
) -> dict[str, Any]:
    """
    Return deterministic vector and pressure fields for the given points.

    Shape conventions match the public API:
      - vector_field: flat list [ux, uy, uz, ux, uy, uz, ...]
      - pressure_field: flat list [p, p, ...]
    """
    if not domain_points:
        return {
            "vector_field": [],
            "pressure_field": [],
            "meta": {"mode": "simulator", "points": 0},
        }

    pts = np.asarray(domain_points, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] < 3:
        raise ValueError("domain_points must be a list of [x, y, z] triples")

    n = pts.shape[0]
    v = float(inlet_velocity_mps)
    t = float(temperature_kelvin)

    # Simple, smooth, reproducible synthetic field (not physics-accurate).
    # Useful for integration tests and demos without a GPU cluster.
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    ux = v * (1.0 + 0.05 * np.sin(0.1 * x) * np.cos(0.1 * y))
    uy = 0.02 * v * np.sin(0.15 * y + 0.05 * z)
    uz = 0.01 * v * np.cos(0.1 * z)
    # Density-ish pressure proxy from temperature and velocity magnitude
    speed = np.sqrt(ux * ux + uy * uy + uz * uz)
    pressure = 101325.0 - 0.5 * 1.225 * speed * speed + 0.1 * (t - 288.15)

    vector_field = np.column_stack([ux, uy, uz]).ravel().tolist()
    pressure_field = pressure.tolist()

    return {
        "vector_field": vector_field,
        "pressure_field": pressure_field,
        "meta": {
            "mode": "simulator",
            "points": n,
            "inlet_velocity_mps": v,
            "temperature_kelvin": t,
            "note": "Deterministic demo field. Not a trained PINN result.",
        },
    }


def mock_latency_ms(n_points: int) -> float:
    """Rough latency model for demos."""
    return round(0.4 + 0.002 * max(0, n_points) + 0.01 * math.sqrt(max(1, n_points)), 3)
