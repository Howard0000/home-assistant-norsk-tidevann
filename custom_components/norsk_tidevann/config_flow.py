import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import (
    CONF_FORECAST_DAYS,
    DEFAULT_FORECAST_DAYS,
    DOMAIN,
    MAX_FORECAST_DAYS,
    MIN_FORECAST_DAYS,
)


class NorskTidevannConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Norsk Tidevann integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Håndter konfigurasjonsflyt fra GUI."""
        errors = {}

        if user_input is not None:
            try:
                lat = float(user_input["latitude"])
                lon = float(user_input["longitude"])
            except (KeyError, ValueError, TypeError):
                errors["base"] = "invalid_coords"
            else:
                uid = f"{round(lat, 4)}_{round(lon, 4)}"
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input["location_name"],
                    data={
                        "latitude": lat,
                        "longitude": lon,
                        "location_name": user_input["location_name"],
                    },
                )

        hass: HomeAssistant = self.hass
        schema = vol.Schema(
            {
                vol.Required("location_name", default="Mitt sted"): str,
                vol.Required("latitude", default=hass.config.latitude): float,
                vol.Required("longitude", default=hass.config.longitude): float,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Returner options flow."""
        return NorskTidevannOptionsFlow()


class NorskTidevannOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Norsk Tidevann."""

    async def async_step_init(self, user_input=None):
        """Vis og lagre integrasjonens innstillinger."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_days = self.config_entry.options.get(
            CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECAST_DAYS,
                    default=current_days,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_FORECAST_DAYS, max=MAX_FORECAST_DAYS),
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
