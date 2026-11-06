"""
Modular enterprise integration interfaces.

These are ADAPTER CONTRACTS + local simulators only.
They do NOT claim live endorsement or certification by Siemens, Nasdaq,
Hitachi, Tesla, or any other named vendor. Real connections require
customer credentials, contracts, and legal review.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any


# ---------------------------------------------------------------------------
# Industrial / facilities (Siemens-style pattern)
# ---------------------------------------------------------------------------
class IndustrialTelemetryProvider(ABC):
    @abstractmethod
    def read_sensors(self, asset_ids: list[str]) -> list[dict[str, Any]]:
        ...


class SimulatorIndustrialTelemetry(IndustrialTelemetryProvider):
    """Safe fictional telemetry for demos and tests."""

    def read_sensors(self, asset_ids: list[str]) -> list[dict[str, Any]]:
        now = time.time()
        out = []
        for i, aid in enumerate(asset_ids or ["demo-asset-1"]):
            out.append(
                {
                    "asset_id": aid,
                    "temperature_c": 42.0 + (i % 5),
                    "vibration_rms": 0.12 + 0.01 * i,
                    "status": "ok",
                    "ts": now,
                    "source": "simulator",
                }
            )
        return out


# ---------------------------------------------------------------------------
# Market / governance (Nasdaq-oriented pattern)
# ---------------------------------------------------------------------------
class MarketDataProvider(ABC):
    @abstractmethod
    def get_quotes(self, symbols: list[str]) -> list[dict[str, Any]]:
        ...


class SimulatorMarketData(MarketDataProvider):
    """Delayed/simulated quotes for demos. Not real market data."""

    def get_quotes(self, symbols: list[str]) -> list[dict[str, Any]]:
        now = time.time()
        out = []
        for i, sym in enumerate(symbols or ["DEMO"]):
            out.append(
                {
                    "symbol": sym.upper(),
                    "price": 100.0 + i * 1.5,
                    "currency": "USD",
                    "delayed": True,
                    "ts": now,
                    "source": "simulator",
                    "disclaimer": "Simulated data only. Not for trading.",
                }
            )
        return out


# ---------------------------------------------------------------------------
# Energy / mobility style adapters (Hitachi / Tesla pattern — interfaces only)
# ---------------------------------------------------------------------------
class EnergyDataProvider(ABC):
    @abstractmethod
    def get_site_power(self, site_id: str) -> dict[str, Any]:
        ...


class SimulatorEnergyData(EnergyDataProvider):
    def get_site_power(self, site_id: str) -> dict[str, Any]:
        return {
            "site_id": site_id or "demo-site",
            "kw_import": 120.5,
            "kw_export": 0.0,
            "soc_pct": 67.0,
            "source": "simulator",
            "ts": time.time(),
        }


class VehicleTelemetryProvider(ABC):
    @abstractmethod
    def get_fleet_snapshot(self, fleet_id: str) -> dict[str, Any]:
        ...


class SimulatorVehicleTelemetry(VehicleTelemetryProvider):
    def get_fleet_snapshot(self, fleet_id: str) -> dict[str, Any]:
        return {
            "fleet_id": fleet_id or "demo-fleet",
            "vehicles_online": 12,
            "avg_speed_kph": 48.2,
            "thermal_alerts": 0,
            "source": "simulator",
            "ts": time.time(),
        }


# Factory helpers
def get_industrial_provider() -> IndustrialTelemetryProvider:
    return SimulatorIndustrialTelemetry()


def get_market_provider() -> MarketDataProvider:
    return SimulatorMarketData()


def get_energy_provider() -> EnergyDataProvider:
    return SimulatorEnergyData()


def get_vehicle_provider() -> VehicleTelemetryProvider:
    return SimulatorVehicleTelemetry()
