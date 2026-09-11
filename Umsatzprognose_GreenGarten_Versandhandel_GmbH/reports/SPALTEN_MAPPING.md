# Spalten-Dokumentation: `verkaufe.csv` → `verkaufe_clean.csv`

Bezieht sich auf `data_management.ipynb` und dessen Ausgabe
`data/interim/verkaufe_clean.csv`. Die Spalten werden **nicht**
umbenannt – alle 16 Original-Spalten behalten exakt ihren
ursprünglichen, technischen Namen aus `verkaufe.csv` (`snake_case`,
klein geschrieben, kein Sonderzeichen außer `_`). Nur die 7 neuen
Spalten (`jahr` und 6 Flags) kommen hinzu, im selben Namensschema.
14.430 Rohzeilen werden zu 23 bereinigten Spalten: die 16
Originalspalten (inhaltlich bereinigt, Namen unverändert) plus 7 neue
Spalten.

**Hinweis vorab:** 30 komplett doppelte Zeilen wurden aus dem gesamten
Datensatz entfernt (betrifft alle Spalten gemeinsam, keine einzelne
Spalte) – siehe Abschnitt 3.2 im Notebook.

## 1. Original-Spalten (16, Name unverändert)

| Spalte (`verkaufe.csv` = `verkaufe_clean.csv`) | Wofür steht die Spalte | Vorgenommene Korrektur |
|---|---|---|
| `produkt_id` | Eindeutige Kennung je Produkt (z. B. `PR-0000`), 600 unterschiedliche Werte. | Keine inhaltliche Korrektur. |
| `kategorie` | Produktkategorie, normalisiert auf 6 einheitliche Werte (Pflanzen, Werkzeuge, Saatgut, Toepfe, Duengemittel, Bewaesserung). | 24 Schreibweisen-Varianten (Groß-/Kleinschreibung, Umlaute, Abkürzungen wie `Saat`/`DUENGER`) auf eine feste Zuordnung normalisiert. |
| `hersteller` | Herstellername, 6 eindeutige Werte. | Keine Korrektur nötig – war bereits sauber. |
| `monat` | Verkaufsmonat als echtes Datum (`datetime64`, 1. Tag des Monats). | 3 verschiedene Textformate (`MM.YYYY`, `YYYY-MM`, `MM/YYYY`) auf einen einheitlichen Datumstyp vereinheitlicht. |
| `monat_idx` | Kalendermonat als Zahl 1–12, unabhängig vom Jahr. | Keine Korrektur nötig. |
| `preis_eur` | Verkaufspreis des Produkts, `float`, 2 Nachkommastellen. | `€`-Zeichen entfernt, Komma durch Punkt ersetzt, in `float` umgewandelt und auf 2 Nachkommastellen gerundet. |
| `wettbewerber_preis_eur` | Vergleichspreis des stärksten Wettbewerbers, `float`, 2 Nachkommastellen. | Keine inhaltliche Korrektur nötig (war bereits sauber numerisch), nur zur Konsistenz auf 2 Nachkommastellen gerundet. Faktor-Check gegen `preis_eur` ohne Auffälligkeiten. |
| `marketingbudget_eur` | Monatliches Marketingbudget für das Produkt. | 433 fehlende Werte im Rohdatensatz (432 nach Duplikat-Entfernung) mit dem Median je Kategorie aufgefüllt – markiert über Flag `marketingbudget_geschaetzt`. |
| `kampagne_aktiv` | Ob in diesem Monat eine Marketingkampagne für das Produkt lief (0/1). | Keine Korrektur nötig – vollständig befüllt. |
| `lagerbestand` | Lagerbestand am Monatsende in Stück, `int`. | Text-Zusatz `"Stueck"` bei 288 Zeilen entfernt, danach in `int` umgewandelt. |
| `bewertungen_durchschnitt` | Durchschnittliche Kundenbewertung des Produkts – pro Produkt über alle Monate konstant. | 576 fehlende Werte per Forward-/Backward-Fill je `produkt_id` rekonstruiert (kein Schätzwert, da der Wert pro Produkt konstant ist) – markiert über Flag `bewertungen_ergaenzt`. |
| `bewertungen_anzahl` | Anzahl abgegebener Kundenbewertungen. | Keine Korrektur nötig – vollständig befüllt. |
| `vormonat_umsatz_eur` | Umsatz des jeweiligen Vormonats desselben Produkts. | Keine Korrektur der Werte selbst – stimmte bereits exakt mit der strukturellen NaN-Logik überein (0 Abweichungen). Nur das erklärende Flag `neues_produkt` ergänzt. |
| `letzte_3_monate_umsatz_eur_avg` | Durchschnitt der letzten 3 Monatsumsätze desselben Produkts. | **Datenfehler korrigiert:** 1.799 Zeilen (Monat 1–3 des Jahres 2024) enthielten fälschlich einen Wert, obwohl noch keine 3 vollständigen Vormonate vorliegen konnten – auf `NaN` gesetzt. Markiert über Flag `hat_3_monats_durchschnitt`. |
| `vorjahr_monat_umsatz_eur` | Umsatz desselben Monats im Vorjahr. | Keine Korrektur der Werte selbst – stimmte bereits exakt mit der Logik überein (0 Abweichungen). Nur das erklärende Flag `hat_vorjahreswert` ergänzt. |
| `umsatz_eur` | Tatsächlicher Umsatz des Produkts in diesem Monat – die Zielgröße für die spätere Umsatzprognose. | **Datenfehler korrigiert:** 5 Zeilen mit unplausiblen Werten (Platzhalter-Extremwerte wie `999.999`, ein negativer Wert, ein falsch übernommener Nullwert) über Kreuzvalidierung mit `vormonat_umsatz_eur` der Folgezeile exakt rekonstruiert. Markiert über Flag `umsatz_korrigiert`. |

## 2. Neue Spalten ohne Original-Gegenstück (7)

Diese Spalten existierten in `verkaufe.csv` nicht. `jahr` ist eine reine
Ableitung, die restlichen 6 sind Flags (0/1), die jede Korrektur aus
Tabelle 1 nachvollziehbar machen, ohne die zugehörige Werte-Spalte selbst
zu verändern. Namen im selben Stil: `snake_case`, klein geschrieben,
kein Sonderzeichen außer `_`.

| Neue Spalte | Wofür steht sie | Herkunft |
|---|---|---|
| `jahr` | Aus `monat` abgeleitetes Kalenderjahr (2024 oder 2025). | Keine Korrektur – reine Ableitung aus `monat`, kein Bezug zu einem Datenfehler. |
| `marketingbudget_geschaetzt` | `1` = Wert in `marketingbudget_eur` war ursprünglich `NaN` und wurde per Median je Kategorie aufgefüllt. `0` = Originalwert. | Dokumentiert die Korrektur an `marketingbudget_eur`. |
| `bewertungen_ergaenzt` | `1` = Wert in `bewertungen_durchschnitt` war ursprünglich `NaN` und wurde rekonstruiert. `0` = Originalwert. | Dokumentiert die Korrektur an `bewertungen_durchschnitt`. |
| `neues_produkt` | `1` = 1. Verkaufsmonat des Produkts, `vormonat_umsatz_eur` ist entsprechend strukturell `NaN`. `0` = es existiert ein Vormonat. | Keine Korrektur – dokumentiert nur die bereits korrekte Struktur von `vormonat_umsatz_eur`. |
| `hat_3_monats_durchschnitt` | `1` = `letzte_3_monate_umsatz_eur_avg` ist ein echter, nachgerechneter Wert. `0` = strukturell `NaN`. | Dokumentiert die Korrektur an `letzte_3_monate_umsatz_eur_avg`. |
| `hat_vorjahreswert` | `1` = `vorjahr_monat_umsatz_eur` ist befüllt. `0` = strukturell `NaN` (Jahr 2024, kein Vorjahr vorhanden). | Keine Korrektur – dokumentiert nur die bereits korrekte Struktur von `vorjahr_monat_umsatz_eur`. |
| `umsatz_korrigiert` | `1` = Wert in `umsatz_eur` wurde als Datenfehler identifiziert und exakt rekonstruiert (5 von 14.400 Zeilen). `0` = Originalwert. | Dokumentiert die Korrektur an `umsatz_eur`. |

## Kurzreferenz: finale Spaltenreihenfolge

```
produkt_id, kategorie, hersteller, monat, jahr, monat_idx,
preis_eur, wettbewerber_preis_eur,
marketingbudget_eur, marketingbudget_geschaetzt,
kampagne_aktiv, lagerbestand,
bewertungen_durchschnitt, bewertungen_ergaenzt, bewertungen_anzahl,
vormonat_umsatz_eur, neues_produkt,
letzte_3_monate_umsatz_eur_avg, hat_3_monats_durchschnitt,
vorjahr_monat_umsatz_eur, hat_vorjahreswert,
umsatz_eur, umsatz_korrigiert
```

14.400 Zeilen × 23 Spalten (Rohdatensatz: 14.430 Zeilen × 16 Spalten,
30 Zeilen davon waren Duplikate).
