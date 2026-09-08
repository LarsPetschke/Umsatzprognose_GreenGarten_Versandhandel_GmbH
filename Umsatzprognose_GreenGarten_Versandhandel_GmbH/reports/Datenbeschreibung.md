# Datenbeschreibung: `verkaufe_clean.csv`

Grundlage: `data/raw/verkaufe.csv` (Original), bereinigt durch
`src/data_management.py` zu `data/interim/verkaufe_clean.csv`.
Diese Beschreibung bezieht sich auf den **bereinigten** Datensatz.

## 1. Übersicht

| Merkmal | Wert |
|---|---|
| Zeilen | 14.400 |
| Spalten | 21 (17 fachliche Spalten + 4 Flag-Spalten aus der Fehlwert-Behandlung, siehe Abschnitt 3) |
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
Das wurde empirisch geprüft (siehe Abschnitt 4). Zusätzlich gibt es vier
**Flag-Spalten** (0/1), die aus der Fehlwert-Behandlung in Schritt 14
stammen und markieren, wo ein Wert fehlte bzw. ersetzt wurde (siehe
Abschnitt 3).

| Spalte | Typ | Ebene | Bedeutung | Fehlende Werte | Wertebereich / Beispiel |
|---|---|---|---|---|---|
| `produkt_id` | Text | Schlüssel | Eindeutige Produktkennung | 0 | `PR-0000` … `PR-0599` |
| `kategorie` | Text | produktkonstant | Produktkategorie (bereinigt aus 24 Schreibweisen) | 0 | Pflanzen, Werkzeuge, Saatgut, Toepfe, Duengemittel, Bewaesserung |
| `hersteller` | Text | produktkonstant | Hersteller/Marke | 0 | Vivero, Floraplan, Garda Tools, GartenStern, Hortica, BioGruen |
| `preis_eur` | Zahl (float) | produktkonstant | Verkaufspreis in Euro (über den gesamten Zeitraum konstant je Produkt) | 0 | 1,50 – 143,50 |
| `bewertungen_durchschnitt` | Zahl (float) | produktkonstant | Durchschnittliche Kundenbewertung | 0 (ursprünglich 576, aufgefüllt – siehe Abschnitt 3) | 1,5 – 5,0 |
| `bewertungen_ergaenzt` | Zahl (0/1), Flag | produktkonstant | 1 = Wert war ursprünglich fehlend und wurde rekonstruiert, 0 = Originalwert | 0 | 0 oder 1 |
| `bewertungen_anzahl` | Zahl (int) | produktkonstant | Anzahl Kundenbewertungen | 0 | ca. 20 – 59 |
| `monat` | Datum (`datetime64`) | Schlüssel | Kalendermonat als echter Datums-Typ (jeweils 1. des Monats) | 0 | `2024-01-01` … `2025-12-01` |
| `jahr` | Zahl (int) | monatsvariabel | Jahr als eigene Spalte, aus `monat` abgeleitet – ermöglicht Filter/Gruppierung nur nach Jahr | 0 | 2024, 2025 |
| `monat_idx` | Zahl (int) | monatsvariabel | Monat als eigene Spalte (1–12), unabhängig vom Jahr – ermöglicht Filter/Gruppierung nur nach Kalendermonat (z. B. "alle Umsätze im Juni, beide Jahre") | 0 | 1 – 12 |
| `wettbewerber_preis_eur` | Zahl (float) | monatsvariabel | Preis des stärksten Wettbewerbers in diesem Monat | 0 | 1,28 – 164,70 |
| `marketingbudget_eur` | Zahl (float) | monatsvariabel | Eingesetztes Marketingbudget in diesem Monat | 0 (ursprünglich 432, aufgefüllt – siehe Abschnitt 3) | 0 – ca. 237 |
| `marketingbudget_geschaetzt` | Zahl (0/1), Flag | monatsvariabel | 1 = Wert war ursprünglich fehlend und wurde per Median-Ersatz geschätzt, 0 = Originalwert | 0 | 0 oder 1 |
| `kampagne_aktiv` | Zahl (0/1) | monatsvariabel | Ob in diesem Monat eine Marketingkampagne lief | 0 | 0 = nein, 1 = ja |
| `lagerbestand` | Zahl (int) | monatsvariabel | Lagerbestand am Monatsende (Stück) | 0 | 1 – 441 |
| `vormonat_umsatz_eur` | Zahl (float) | abgeleitet | Umsatz des Vormonats desselben Produkts | 600 (bewusst NaN – siehe Abschnitt 3) | siehe Abschnitt 4 |
| `ist_neuprodukt` | Zahl (0/1), Flag | abgeleitet | 1 = erster Verkaufsmonat des Produkts (kein Vormonat vorhanden), 0 = sonst | 0 | 0 oder 1 |
| `letzte_3_monate_umsatz_eur_avg` | Zahl (float) | abgeleitet | Ø Umsatz der letzten 3 Monate desselben Produkts | 600 (bewusst NaN, deckungsgleich mit `ist_neuprodukt`) | siehe Abschnitt 4 |
| `vorjahr_monat_umsatz_eur` | Zahl (float) | abgeleitet | Umsatz desselben Monats im Vorjahr | 7.200 (bewusst NaN – siehe Abschnitt 3) | siehe Abschnitt 4 |
| `hat_vorjahreswert` | Zahl (0/1), Flag | abgeleitet | 1 = Vorjahreswert vorhanden, 0 = nicht vorhanden (alle Zeilen aus 2024) | 0 | 0 oder 1 |
| `umsatz_eur` | Zahl (float) | **Zielvariable** | Tatsächlicher Umsatz in diesem Monat (Prognoseziel) | 4 | 0 – 20.617,85 |

## 3. Behandlung fehlender Werte (Strategie, Umsetzung und Flags)

Fehlende Werte wurden **je Spalte einzeln auf ihre Ursache geprüft**
und erst danach entschieden, ob und wie sie ersetzt werden – ein
pauschaler Mean-/Median-Ersatz über alle Spalten hinweg hätte an
mehreren Stellen falsche Signale erzeugt. Umgesetzt in
`src/data_management.py`, Schritt 14.

### 3.1 Strukturell fehlend → NaN bleibt, plus Flag

`vormonat_umsatz_eur` (600 fehlend) und `vorjahr_monat_umsatz_eur`
(7.200 fehlend) fehlen nicht zufällig, sondern weil zu diesem Zeitpunkt
schlicht noch keine Historie existieren *kann* (erster Verkaufsmonat
eines Produkts bzw. erstes Jahr des Datensatzes ohne Vorjahr). Ein
Auffüllen mit Mean oder Median würde eine Historie vortäuschen, die es
nicht gibt, und ein Prognosemodell würde daraus ein falsches Signal
lernen ("ähnlicher Umsatz wie im Vormonat", obwohl es den Vormonat gar
nicht gab). Deshalb bleiben die Werte `NaN`. Damit Modelle, die kein
`NaN` verarbeiten können (z. B. lineare Regression), diese Information
trotzdem nutzen können, wurden zwei binäre Flags ergänzt:

- `ist_neuprodukt` = 1 in genau den 600 Zeilen mit fehlendem
  `vormonat_umsatz_eur` (ein erster Monat je Produkt).
- `hat_vorjahreswert` = 0 in genau den 7.200 Zeilen des Jahres 2024.

`letzte_3_monate_umsatz_eur_avg` (600 fehlend, siehe Schritt 12) folgt
direkt aus `vormonat_umsatz_eur` (ohne Vormonat kein 3-Monats-Schnitt
möglich) und ist damit deckungsgleich mit `ist_neuprodukt` – eine
eigene Behandlung war nicht nötig.

Baumbasierte Modelle (z. B. LightGBM, XGBoost, CatBoost) verarbeiten
`NaN` ohnehin nativ und können zusätzlich von den Flags profitieren;
bei linearen Modellen sollten die drei NaN-Spalten vor dem Training auf
Basis der Flags behandelt werden (z. B. 0 einsetzen und ausschließlich
über den Flag steuern lassen, welches Gewicht das Modell dem beimisst).

### 3.2 `bewertungen_durchschnitt` (576 fehlend) → je Produkt rekonstruiert

Geprüft wurde, ob der Wert innerhalb eines Produkts über die 24 Monate
schwankt: Bei allen 600 Produkten gibt es **genau einen** eindeutigen,
nicht-fehlenden Wert – die Bewertung ist also je Produkt konstant. Ein
fehlender Monatswert ist damit kein unbekannter Wert, sondern lediglich
an dieser Stelle nicht mitgeschrieben, obwohl er aus anderen Monaten
desselben Produkts exakt bekannt ist. Statt einer Schätzung (Mean/
Median) wurde der Wert daher je `produkt_id` per Forward-/Backward-Fill
rekonstruiert (`groupby("produkt_id").transform(ffill().bfill())`).
Ergebnis: 0 verbleibende Fehlwerte. Der Flag `bewertungen_ergaenzt`
markiert die 576 rekonstruierten Zeilen, damit nachvollziehbar bleibt,
welche Werte nicht aus der Originalerhebung stammen.

### 3.3 `marketingbudget_eur` (432 fehlend) → Median je Kategorie

Geprüft wurde, ob die fehlenden Werte mit `kategorie` oder
`kampagne_aktiv` zusammenhängen: Die Fehlquote liegt in beiden Gruppen
bei rund 3 % (inaktive Kampagne: 391 von 12.769 Zeilen; aktive
Kampagne: 42 von 1.596 Zeilen) – kein erkennbarer Zusammenhang. Auch
die Mediane je Kategorie liegen eng beieinander (85,58 € bis 90,72 €
gegenüber einem globalen Median von 88,09 €). Die Verteilung ist leicht
rechtsschief (Skew ≈ 0,35), weshalb der **Median statt des
Mittelwerts** verwendet wurde – er ist robuster gegenüber den wenigen
hohen Werten am oberen Rand der Verteilung. Fehlende Werte wurden mit
dem Median der jeweiligen `kategorie` aufgefüllt. Ergebnis: 0
verbleibende Fehlwerte. Der Flag `marketingbudget_geschaetzt` markiert
die 432 geschätzten Zeilen.

### 3.4 `umsatz_eur` (4 fehlend)

Keine echten Fehlwerte, sondern die vier korrigierten Ausreißer (zwei
Platzhalterwerte 999.999 / 750.000, zwei negative Werte -1 / -150), die
bewusst auf `NaN` gesetzt wurden statt die Zeilen zu löschen (Details:
Abschnitt 5). Diese vier bleiben unverändert `NaN` – hierfür wäre jede
Schätzung (Mean/Median) eine Erfindung von Umsatzzahlen, die es nie gab.

## 4. Ausreißer in der Zielvariable `umsatz_eur` (Detail)

Bei der Untersuchung des bereinigten Datensatzes wurden vier Werte in
der Zielvariable `umsatz_eur` identifiziert, die eindeutig nicht
plausibel sind:

| Produkt | Monat | Wert | Einordnung |
|---|---|---|---|
| PR-0486 | 08/2025 | 999.999,00 € | Platzhalter-/Erfassungsfehler (liegt mehr als 48-mal über dem nächsthöheren Wert im gesamten Datensatz) |
| PR-0236 | 04/2025 | 750.000,00 € | Platzhalter-/Erfassungsfehler (liegt mehr als 36-mal über dem nächsthöheren Wert) |
| PR-0334 | 03/2024 | -1,00 € | Negativer Umsatz ist fachlich nicht möglich |
| PR-0545 | 07/2024 | -150,00 € | Negativer Umsatz ist fachlich nicht möglich |

Zum Vergleich: Der nächsthöhere, plausible Umsatzwert im gesamten
Datensatz liegt bei rund 20.600 €. Betroffen sind 4 von 14.400 Werten
(ca. 0,03 %).

**Entscheidung:** Die vier Werte wurden nicht gelöscht – das würde das
jeweilige Produkt in diesem Monat komplett aus dem Datensatz
verschwinden lassen –, sondern gezielt auf fehlend (`NaN`) gesetzt. So
bleiben Produkt und Zeitpunkt sichtbar und können in der Modellierung
bewusst behandelt werden (z. B. Ausschluss aus dem Training oder
gezielte Imputation).

**Prüfung auf Folgefehler:** Da `vormonat_umsatz_eur`,
`letzte_3_monate_umsatz_eur_avg` und `vorjahr_monat_umsatz_eur`
inhaltlich aus `umsatz_eur` abgeleitet sind, wurde zusätzlich geprüft,
ob die vier fehlerhaften Werte auch dort auftauchen – im jeweiligen
Folgemonat, in den beiden darauffolgenden Monaten (wegen des
3-Monats-Durchschnitts) sowie im Folgejahr. Ergebnis: In keinem der 20
geprüften Folgewerte (4 Ausreißer × 5 Prüfpunkte) trat der fehlerhafte
Wert erneut auf. Die abgeleiteten Spalten basieren demnach auf den
tatsächlichen, unverfälschten Umsätzen und mussten nicht zusätzlich
korrigiert werden.

*Quelle: `src/data_management.py`, Schritt 11.*

## 5. Hinweise für die weitere Verarbeitung (EDA / Modellierung)

- **Konstante Merkmale je Produkt:** `preis_eur`, `bewertungen_durchschnitt`
  und `bewertungen_anzahl` ändern sich in diesem Datensatz über die Zeit
  nicht (geprüft: 0 von 600 Produkten mit abweichenden Werten). Für die
  Modellierung sind das reine Produktmerkmale, keine Zeitreihenmerkmale.
- **Flag-Spalten vor der Modellierung sichten:** `ist_neuprodukt`,
  `hat_vorjahreswert`, `bewertungen_ergaenzt` und
  `marketingbudget_geschaetzt` sind reine Meta-Informationen aus der
  Datenaufbereitung (Schritt 14). Sie sollten je nach Modelltyp bewusst
  einbezogen (z. B. als zusätzliches Feature, ob ein Wert geschätzt war)
  oder vor dem Training wieder entfernt werden – sie sind keine
  fachlichen Merkmale des Produkts oder Verkaufsmonats.
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
