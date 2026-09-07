# Datenbeschreibung: `verkaufe_clean.csv`

Grundlage: `data/raw/verkaufe.csv` (Original), bereinigt durch
`src/data_management.py` zu `data/interim/verkaufe_clean.csv`.
Diese Beschreibung bezieht sich auf den **bereinigten** Datensatz.

## 1. Übersicht

| Merkmal | Wert |
|---|---|
| Zeilen | 14.400 |
| Spalten | 17 |
| Ein Datensatz (eine Zeile) ist ... | **ein Produkt in einem Monat** |
| Primärschlüssel (eindeutige Kombination) | `produkt_id` + `monat` |
| Eindeutige Produkte | 600 (`PR-0000` bis `PR-0599`) |
| Zeitraum | 24 Monate, `2024-01` bis `2025-12` |
| Rechnerische Kontrolle | 600 Produkte × 24 Monate = 14.400 Zeilen ✓ |

Der Rohdatensatz enthielt statt 14.400 noch 14.430 Zeilen; die
zusätzlichen 30 Zeilen waren vollständige Duplikate und wurden entfernt
(siehe `src/data_management.py`, Schritt 10).

## 2. Spalten

Die Spalten gliedern sich in zwei Ebenen: **produktkonstante** Merkmale
(ändern sich für ein Produkt über die 24 Monate nicht) und
**monatsvariable** Merkmale (haben in jedem Monat einen eigenen Wert).
Das wurde empirisch geprüft (siehe Abschnitt 3).

| Spalte | Typ | Ebene | Bedeutung | Fehlende Werte | Wertebereich / Beispiel |
|---|---|---|---|---|---|
| `produkt_id` | Text | Schlüssel | Eindeutige Produktkennung | 0 | `PR-0000` … `PR-0599` |
| `kategorie` | Text | produktkonstant | Produktkategorie (bereinigt aus 24 Schreibweisen) | 0 | Pflanzen, Werkzeuge, Saatgut, Toepfe, Duengemittel, Bewaesserung |
| `hersteller` | Text | produktkonstant | Hersteller/Marke | 0 | Vivero, Floraplan, Garda Tools, GartenStern, Hortica, BioGruen |
| `preis_eur` | Zahl (float) | produktkonstant | Verkaufspreis in Euro (über den gesamten Zeitraum konstant je Produkt) | 0 | 1,50 – 143,50 |
| `bewertungen_durchschnitt` | Zahl (float) | produktkonstant | Durchschnittliche Kundenbewertung | 576 | 1,5 – 5,0 |
| `bewertungen_anzahl` | Zahl (int) | produktkonstant | Anzahl Kundenbewertungen | 0 | ca. 20 – 59 |
| `monat` | Datum (`datetime64`) | Schlüssel | Kalendermonat als echter Datums-Typ (jeweils 1. des Monats) | 0 | `2024-01-01` … `2025-12-01` |
| `jahr` | Zahl (int) | monatsvariabel | Jahr als eigene Spalte, aus `monat` abgeleitet – ermöglicht Filter/Gruppierung nur nach Jahr | 0 | 2024, 2025 |
| `monat_idx` | Zahl (int) | monatsvariabel | Monat als eigene Spalte (1–12), unabhängig vom Jahr – ermöglicht Filter/Gruppierung nur nach Kalendermonat (z. B. "alle Umsätze im Juni, beide Jahre") | 0 | 1 – 12 |
| `wettbewerber_preis_eur` | Zahl (float) | monatsvariabel | Preis des stärksten Wettbewerbers in diesem Monat | 0 | 1,28 – 164,70 |
| `marketingbudget_eur` | Zahl (float) | monatsvariabel | Eingesetztes Marketingbudget in diesem Monat | 432 | 0 – ca. 237 |
| `kampagne_aktiv` | Zahl (0/1) | monatsvariabel | Ob in diesem Monat eine Marketingkampagne lief | 0 | 0 = nein, 1 = ja |
| `lagerbestand` | Zahl (int) | monatsvariabel | Lagerbestand am Monatsende (Stück) | 0 | 1 – 441 |
| `vormonat_umsatz_eur` | Zahl (float) | abgeleitet | Umsatz des Vormonats desselben Produkts | 600 | siehe Abschnitt 3 |
| `letzte_3_monate_umsatz_eur_avg` | Zahl (float) | abgeleitet | Ø Umsatz der letzten 3 Monate desselben Produkts | 600 | siehe Abschnitt 3 |
| `vorjahr_monat_umsatz_eur` | Zahl (float) | abgeleitet | Umsatz desselben Monats im Vorjahr | 7.200 | siehe Abschnitt 3 |
| `umsatz_eur` | Zahl (float) | **Zielvariable** | Tatsächlicher Umsatz in diesem Monat (Prognoseziel) | 4 | 0 – 20.617,85 |

## 3. Ursache der fehlenden Werte (einzeln geprüft, nicht pauschal angenommen)

| Spalte | Fehlend | Ursache |
|---|---|---|
| `vormonat_umsatz_eur` | 600 | **Strukturell erklärbar:** betrifft exakt den ersten Monat (`2024-01`) jedes der 600 Produkte – hier existiert kein Vormonat. |
| `vorjahr_monat_umsatz_eur` | 7.200 | **Strukturell erklärbar:** betrifft exakt alle Zeilen des Jahres 2024 (600 × 12), da der Datensatz erst 2024 beginnt und somit kein Vorjahreswert existiert. |
| `bewertungen_durchschnitt` | 576 | Fehlt vollständig für einzelne Produkte (Wert ist je Produkt konstant) – vermutlich Produkte ohne Kundenbewertungen. |
| `marketingbudget_eur` | 432 | **Keine erkennbare Systematik:** fehlt sowohl bei aktiver als auch bei inaktiver Kampagne (390 von 12.769 inaktiven Zeilen, 42 von 1.631 aktiven Zeilen) – wird als einfache Datenlücke eingestuft, nicht als inhaltlich begründbar. |
| `letzte_3_monate_umsatz_eur_avg` | 600 | **Strukturell erklärbar (nach Korrektur):** identisch zu `vormonat_umsatz_eur` – der erste Monat eines Produkts kann keinen 3-Monats-Durchschnitt haben. **Export-Fehler behoben:** Ursprünglich waren bei 599 dieser 600 Zeilen trotzdem Werte eingetragen (die auch nicht dem eigenen Umsatz der Zeile entsprachen, also nicht plausibel herleitbar waren) – laut Projekt-Brief-Definition wurden diese auf NaN korrigiert (`src/data_management.py`, Schritt 12). |
| `umsatz_eur` | 4 | Keine echten Fehlwerte, sondern die vier von uns korrigierten Ausreißer (zwei Platzhalterwerte 999.999 / 750.000, zwei negative Werte -1 / -150), die bewusst auf NaN gesetzt wurden statt die Zeilen zu löschen. |

## 4. Hinweise für die weitere Verarbeitung (EDA / Modellierung)

- **Konstante Merkmale je Produkt:** `preis_eur`, `bewertungen_durchschnitt`
  und `bewertungen_anzahl` ändern sich in diesem Datensatz über die Zeit
  nicht (geprüft: 0 von 600 Produkten mit abweichenden Werten). Für die
  Modellierung sind das reine Produktmerkmale, keine Zeitreihenmerkmale.
- **Zielvariable und ihre Ableitungen:** `vormonat_umsatz_eur`,
  `letzte_3_monate_umsatz_eur_avg` und `vorjahr_monat_umsatz_eur` sind
  inhaltlich aus `umsatz_eur` abgeleitet. **Geprüft (Schritt 11 in
  `data_management.py`):** Für alle vier korrigierten `umsatz_eur`-Werte
  wurde in den Folgemonaten, den nächsten drei Monaten (wegen des
  3-Monats-Durchschnitts) und im Folgejahr explizit nachgesehen, ob dort
  noch der fehlerhafte Wert (999.999 / 750.000 / -1 / -150) steht. Ergebnis:
  **keine Kontamination gefunden** – die drei abgeleiteten Spalten wurden
  offenbar unabhängig aus den echten, unverfälschten Umsätzen berechnet.
  Keine weitere Korrektur nötig.
- **`jahr` und `monat_idx` für Marketing-Auswertungen:** Statt jedes
  Mal die Kombination `monat` (z. B. `2024-06`) zu filtern, stehen Jahr
  und Kalendermonat als eigene Spalten zur Verfügung. Beispiele:
  `df[df["jahr"] == 2024]` liefert alle Zeilen eines Jahres ohne
  12-fachen Filter über `monat`; `df[df["monat_idx"] == 6]` liefert
  alle Juni-Werte über beide Jahre hinweg (z. B. für saisonale
  Marketing-Auswertungen); `df.groupby("jahr")["umsatz_eur"].sum()`
  bzw. `df.groupby("monat_idx")["umsatz_eur"].sum()` fassen direkt
  zusammen. Die Spalte `monat` bleibt als eindeutiger Zeitschlüssel
  (für Sortierung und Verknüpfung) zusätzlich erhalten.
- **`monat` beim Wiedereinlesen:** Da CSV-Dateien keine Datentypen
  speichern, steht `monat` in der Datei als Text (`2024-01-01`). Beim
  erneuten Einlesen unbedingt `pd.read_csv(..., parse_dates=["monat"])`
  verwenden, damit wieder ein echter `datetime64`-Typ entsteht (nicht
  `dtype=str` – das war nur der Workaround für den ursprünglichen
  Punkt-Format-Bug und ist mit dem jetzigen Format nicht mehr nötig).
- **Zeitlicher Split:** Für eine echte Prognose darf beim Train/Test-Split
  ausschließlich chronologisch getrennt werden (z. B. 2024 = Training,
  2025 = Test), damit keine zukünftigen Informationen ins Training
  gelangen.
