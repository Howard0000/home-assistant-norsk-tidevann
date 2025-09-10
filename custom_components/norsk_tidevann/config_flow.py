import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

class NorskTidevannConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Norsk Tidevann integration."""

    async def async_step_user(self, user_input=None):
        """Håndter konfigurasjonsflyt fra GUI."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input["location_name"],
                data={
                    "latitude": user_input["latitude"],
                    "longitude": user_input["longitude"],
                    "location_name": user_input["location_name"],
                },
            )

        # Hent standardposisjon fra Home Assistant
        hass: HomeAssistant = self.hass
        default_latitude = hass.config.latitude
        default_longitude = hass.config.longitude

        # Definer skjemaet for GUI
        schema = vol.Schema({
            vol.Required("location_name", default="Mitt sted"): str,
            vol.Required("latitude", default=default_latitude): float,
            vol.Required("longitude", default=default_longitude): float,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)









