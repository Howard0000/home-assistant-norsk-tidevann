from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging
from datetime import datetime, timezone
latest = max(values, key=lambda x: datetime.fromisoformat(x["time"]).astimezone(timezone.utc))


from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Sett opp tidevannsdata sensorer."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    if not coordinator.data:
        _LOGGER.error("Ingen tidevannsdata ble hentet fra API-et.")
        return

    async_add_entities([
        TideWaterSensor(coordinator, "observation", "Tidevann Observasjon"),
        TideWaterSensor(coordinator, "prediction", "Tidevann Prediksjon"),
        TideWaterSensor(coordinator, "forecast", "Tidevann Prognose"),
    ], True)

class TideWaterSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tidevannsdata."""

    def __init__(self, coordinator, tide_type, name):
        """Initialiser sensoren."""
        super().__init__(coordinator)
        location_name = self.coordinator.config_entry.data.get("location_name", "Ukjent")
        self._attr_name = f"{location_name} {name}"
        self._attr_unique_id = f"tide_water_{self.coordinator.config_entry.entry_id}_{tide_type}"
        self._attr_unit_of_measurement = "cm"
        self.tide_type = tide_type

    @property
    def native_value(self):
        """Returner siste tidevannsnivå."""
        if not self.coordinator.data or self.tide_type not in self.coordinator.data:
            _LOGGER.warning(f"Ingen {self.tide_type}-data tilgjengelig ennå.")
            return None

        tide_values = self.coordinator.data[self.tide_type]
        now_utc = datetime.now(timezone.utc)

        # Fjern fremtidige observasjoner for "observation"
        if self.tide_type == "observation":
            tide_values = [
                t for t in tide_values
                if datetime.fromisoformat(t["time"]).astimezone(timezone.utc) <= now_utc
            ]

        if not tide_values:
            _LOGGER.warning(f"Ingen {self.tide_type}-verdier funnet!")
            return None

        # Finn den nyeste tilgjengelige observasjonen
        latest_tide = max(tide_values, key=lambda x: x["time"])
        return float(latest_tide["level"])  # Konverter til tall

    @property
    def extra_state_attributes(self):
        """Legger til tidevannsdata for ApexCharts, begrenset til de siste 12 timene og hver 30. minutt."""
        if not self.coordinator.data or self.tide_type not in self.coordinator.data:
            return {}

        tide_values = self.coordinator.data[self.tide_type]
        now_utc = datetime.now(timezone.utc)

        # Begrens til de siste 12 timene
        time_cutoff = now_utc - timedelta(hours=12)
        tide_values = [
            t for t in tide_values
            if datetime.fromisoformat(t["time"]).astimezone(timezone.utc) >= time_cutoff
        ]

        # Behold kun hver 30. minutt
        filtered_tide_values = []
        last_time = None

        for t in tide_values:
            current_time = datetime.fromisoformat(t["time"]).astimezone(timezone.utc)
            if last_time is None or (current_time - last_time).total_seconds() >= 1800:
                filtered_tide_values.append(t)
                last_time = current_time

        return {
            "data": [{"datetime": t["time"], self.tide_type: float(t["level"])} for t in filtered_tide_values],
        }








