Norsk Tidevann – Home Assistant integrasjon
![alt text](https://img.shields.io/badge/HACS-Custom-orange.svg)
Dette er en Home Assistant-integrasjon for å hente og vise tidevannsdata fra Kartverket.
Integrasjonen gjør det enkelt å følge med på observasjoner, prediksjoner og prognoser av tidevannet for en valgt posisjon.
Integrasjonen er basert på tmjo/ha-norwegiantide, men tilpasset med:
Full norsk språkdrakt (GUI, logg, sensornavn).
Ekstra funksjonalitet for ApexCharts (sensorene får attributter med siste 12 timer data, filtrert til hver 30. minutt).
Ferdig eksempel på Lovelace-konfigurasjon med graf.
![alt text](https://raw.githubusercontent.com/Howard0000/home-assistant-norsk-tidevann/main/examples/apexcharts/ApexCharts.png)
Funksjoner
Tre dedikerte sensorer for tidevann:
Observasjon (faktisk målt vannstand)
Prediksjon (tabellverdier/astronomisk tidevann)
Prognose (modellert vannstand inkludert vær)
Alle sensorer oppdateres automatisk hvert 15. minutt.
Enkel konfigurasjon via Home Assistants brukergrensesnitt (ingen YAML nødvendig).
Optimalisert for visualisering med ApexCharts ved å levere historiske data som attributter.
Installasjon
HACS (Anbefalt metode)
Gå til HACS -> Integrasjoner i Home Assistant.
Klikk på de tre prikkene øverst til høyre og velg Egendefinerte repositorier (Custom repositories).
Lim inn URL-en til dette prosjektet: https://github.com/Howard0000/home-assistant-norsk-tidevann
Velg kategorien Integrasjon.
Klikk Legg til.
Finn "Norsk Tidevann" i listen og klikk Installer.
Start Home Assistant på nytt.
Manuell Installasjon
Last ned den nyeste versjonen fra Releases-siden.
Pakk ut filene og kopier mappen norsk_tidevann til custom_components-mappen i Home Assistant.
Stien blir: /config/custom_components/norsk_tidevann
Start Home Assistant på nytt.
Konfigurasjon
Etter installasjon må integrasjonen konfigureres.
Gå til Innstillinger → Enheter og tjenester.
Klikk på Legg til integrasjon nede til høyre.
Søk etter og velg Norsk Tidevann.
Følg instruksjonene:
Velg et Navn for integrasjonen (f.eks. "Tidevann Arendal"). Dette blir en del av sensor-ID-en.
Angi Breddegrad (Latitude) og Lengdegrad (Longitude) for stedet du vil hente data for.
Integrasjonen vil nå opprette sensorene.
Bruk i Lovelace (ApexCharts)
Integrasjonen er laget for å spille godt sammen med ApexCharts Card. Sensorenes data-attributt inneholder alt du trenger for å tegne grafene.
Her er et eksempel for Lovelace-dashboardet ditt:
code
Yaml
type: custom:apexcharts-card
graph_span: 36h
span:
  offset: +24h
now:
  show: true
  label: Nå
header:
  show: true
  title: Tidevann
  show_states: true
series:
  - entity: sensor.tidevann_prediksjon
    name: Tabell
    color: orange
    show:
      extremas: true
      in_header: before_now
    data_generator: |
      return entity.attributes.data.map((entry) => {
        return [new Date(entry.datetime).getTime(), entry.prediction];
      });
  - entity: sensor.tidevann_prognose
    name: Prognose
    color: blue
    data_generator: |
      return entity.attributes.data.map((entry) => {
        return [new Date(entry.datetime).getTime(), entry.forecast];
      });
  - entity: sensor.tidevann_observasjon
    name: Observasjon
    color: red
    data_generator: |
      const now = new Date().getTime();
      return entity.attributes.data
        .filter(entry => new Date(entry.datetime).getTime() <= now)
        .map(entry => [new Date(entry.datetime).getTime(), entry.observation]);
Krav
Home Assistant versjon 2024.x eller nyere.
Tilgang til internett for å hente data fra vannstand.kartverket.no.
Anerkjennelser
Prosjektet er skrevet og vedlikeholdt av @Howard0000. En KI-assistent har hjulpet til med å forenkle forklaringer, rydde i README-en og pusse på skript. Alle forslag er manuelt vurdert før de ble tatt inn, og all konfigurasjon og testing er gjort av meg.
Merknad
Dette er et uoffisielt community-prosjekt og er ikke utviklet, støttet eller vedlikeholdt av Kartverket. All bruk skjer på eget ansvar. For offisiell dokumentasjon, se Kartverkets API-dokumentasjon.
Kreditering
Integrasjonen er en videreutvikling av tmjo/ha-norwegiantide.
Endringer i denne versjonen inkluderer:
Full norsk oversettelse i GUI, logger og entiteter.
Tilpassede attributter for enklere bruk med ApexCharts (12t historikk, 30-minutters intervaller).
Oppdaterte eksempler for Lovelace.
Lisens
Dette prosjektet er lisensiert under MIT License.
