import logging
from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Sett opp tidevannssensorer."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            TideWaterSensor(coordinator, "observation", "Tidevann Observasjon"),
            TideWaterSensor(coordinator, "prediction", "Tidevann Prediksjon"),
            TideWaterSensor(coordinator, "forecast", "Tidevann Prognose"),
        ]
    )


class TideWaterSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tidevannsdata."""

    # Tidsserien brukes av blant annet ApexCharts, men skal ikke lagres i
    # Recorder-databasen. Prognoser over flere dager kan ellers overstige
    # Home Assistants grense for størrelsen på lagrede state-attributter.
    _unrecorded_attributes = frozenset({"data"})

    def __init__(self, coordinator, tide_type, name):
        super().__init__(coordinator)
        location_name = coordinator.config_entry.data.get("location_name", "Ukjent")
        self._attr_name = f"{location_name} {name}"
        self._attr_unique_id = (
            f"tide_water_{coordinator.config_entry.entry_id}_{tide_type}"
        )
        self._attr_native_unit_of_measurement = "cm"
        self.tide_type = tide_type

    @staticmethod
    def _as_utc(value: str) -> datetime:
        """Konverter API-tid til UTC."""
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @property
    def native_value(self):
        """Returner verdien nærmest nå."""
        if not self.coordinator.data:
            return None

        tide_values = self.coordinator.data.get(self.tide_type, [])
        if not tide_values:
            return None

        now_utc = datetime.now(timezone.utc)

        if self.tide_type == "observation":
            candidates = [
                item
                for item in tide_values
                if self._as_utc(item["time"]) <= now_utc
            ]
            if not candidates:
                return None
            selected = max(candidates, key=lambda item: self._as_utc(item["time"]))
        else:
            selected = min(
                tide_values,
                key=lambda item: abs(
                    (self._as_utc(item["time"]) - now_utc).total_seconds()
                ),
            )

        return float(selected["level"])

    @property
    def extra_state_attributes(self):
        """Legg til tidsserie for ApexCharts."""
        if not self.coordinator.data:
            return {}

        tide_values = self.coordinator.data.get(self.tide_type, [])
        now_utc = datetime.now(timezone.utc)
        history_cutoff = now_utc - timedelta(hours=12)

        filtered = []
        last_time = None

        for item in sorted(tide_values, key=lambda value: self._as_utc(value["time"])):
            current_time = self._as_utc(item["time"])

            if current_time < history_cutoff:
                continue
            if self.tide_type == "observation" and current_time > now_utc:
                continue

            # Ett punkt hver 30. minutt gir god graf uten unødig store attributter.
            if last_time is None or (current_time - last_time).total_seconds() >= 1800:
                filtered.append(item)
                last_time = current_time

        return {
            "data": [
                {
                    "datetime": item["time"],
                    self.tide_type: float(item["level"]),
                }
                for item in filtered
            ]
        }
