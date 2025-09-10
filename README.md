# Norsk Tidevann – Home Assistant integrasjon

Dette er en Home Assistant-integrasjon for å hente og vise tidevannsdata fra **Kartverket**.  
Integrasjonen gjør det enkelt å følge med på **observasjoner, prediksjoner og prognoser** av tidevannet for en valgt posisjon.  

Integrasjonen er basert på [tmjo/ha-norwegiantide](https://github.com/tmjo/ha-norwegiantide), men tilpasset med:  
- Full **norsk språkdrakt** (GUI, logg, sensornavn).  
- Ekstra funksjonalitet for **ApexCharts** (sensorene får attributter med siste 12 timer data, filtrert til hver 30. minutt).  
- Ferdig eksempel på **Lovelace-konfigurasjon** med graf.  

---

## Hva du får

- Sensorer for tidevann:
  - **Observasjon** (målt vannstand)
  - **Prediksjon** (tabellverdier fra Kartverket)
  - **Prognose** (modellert vannstand fremover)  
- Alle sensorer oppdateres automatisk hvert 15. minutt.  
- GUI-konfigurasjon i Home Assistant (ingen YAML nødvendig).  
- Mulighet til å tegne grafer i **ApexCharts** direkte fra sensordata.  

---

## Installasjon

1. Kopier mappen `custom_components/norsk_tidevann/` til din Home Assistant-installasjon.  
   Typisk:  
   ```
   /config/custom_components/norsk_tidevann
   ```
2. Start Home Assistant på nytt.  
3. Gå til **Innstillinger → Integrasjoner** og legg til **Norsk Tidevann**.  
4. Velg navn, breddegrad og lengdegrad for stedet du ønsker tidevannsdata.  

---

## Bruk i Lovelace (ApexCharts)

Integrasjonen er laget for å spille godt sammen med [ApexCharts Card](https://github.com/RomRider/apexcharts-card).  

Eksempel på visning:  

```yaml
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
```

📊 Se eksempelfil: `examples/apexcharts//type customapexcharts-card.txt`  
📷 Se skjermbilde: `examples/apexcharts//ApexCharts.png`  

---

## Krav

- Home Assistant 2024.x eller nyere  
- Tilgang til internett (for å hente data fra [vannstand.kartverket.no](https://vannstand.kartverket.no/))  

---

## Anerkjennelser
Prosjektet er skrevet og vedlikeholdt av @Howard0000. En KI-assistent har hjulpet til med å forenkle forklaringer, rydde i README-en og pusse på skript. Alle forslag er manuelt vurdert før de ble tatt inn, og all konfigurasjon og testing er gjort av meg.

---

## Lisens

Dette prosjektet er lisensiert under [MIT License](LICENSE).  

---

## Merknad

Dette er et **uoffisielt community-prosjekt** og ikke utviklet, støttet eller vedlikeholdt av **Kartverket**.  
All bruk skjer på eget ansvar. For offisiell dokumentasjon, se [Kartverket API-dokumentasjon](https://vannstand.kartverket.no/).  

---

## Kreditering

Integrasjonen er basert på [tmjo/ha-norwegiantide](https://github.com/tmjo/ha-norwegiantide).  
Endringer i denne versjonen:  
- Norsk språk i GUI og logg.  
- Tilpassede attributter for ApexCharts (12t, 30-minutt intervall).  
- Eksempler på bruk i Lovelace (YAML + skjermbilde).  
