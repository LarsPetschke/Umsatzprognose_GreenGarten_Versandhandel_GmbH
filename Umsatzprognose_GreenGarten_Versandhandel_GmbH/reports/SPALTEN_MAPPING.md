# Spalten-Mapping: `verkaufe.csv` → `verkaufe_clean.csv`

Bezieht sich auf `data_management.ipynb` und dessen Ausgabe `data/interim/verkaufe_clean.csv`. 
16 Rohspalten werden zu 23 bereinigten Spalten: 
die 16 Originalspalten (umbenannt, teils bereinigt) plus 7 neue Spalten 
(`Jahr` und 6 Flags, die Bereinigungen dokumentieren).

**Hinweis vorab:** 30 komplett doppelte Zeilen wurden aus dem gesamten
Datensatz entfernt (betrifft alle Spalten gemeinsam, keine einzelne
Spalte) – siehe Abschnitt 3.2 im Notebook.

## 1. Umbenannte Original-Spalten (16)

| Ursprünglich (`verkaufe.csv`) | Bereinigt (`verkaufe_clean.csv`) | Wofür steht die Spalte | Vorgenommene Korrektur |
|---|---|---|---|
| `produkt_id` | `Produkt-ID` | Eindeutige Kennung je Produkt (z. B. `PR-0000`), 600 unterschiedliche Werte. | Keine inhaltliche Korrektur, nur umbenannt. |
| `kategorie` | `Kategorie` | Produktkategorie, normalisiert auf 6 einheitliche Werte (Pflanzen, Werkzeuge, Saatgut, Toepfe, Duengemittel, Bewaesserung). | 24 Schreibweisen-Varianten (Groß-/Kleinschreibung, Umlaute, Abkürzungen wie `Saat`/`DUENGER`) auf eine feste Zuordnung normalisiert. |
| `hersteller` | `Hersteller` | Herstellername, 6 eindeutige Werte. | Keine Korrektur nötig – war bereits sauber. |
| `monat` | `Monat` | Verkaufsmonat als echtes Datum (`datetime64`, 1. Tag des Monats). | 3 verschiedene Textformate (`MM.YYYY`, `YYYY-MM`, `MM/YYYY`) auf einen einheitlichen Datumstyp vereinheitlicht. |
| `monat_idx` | `Kalendermonat` | Kalendermonat als Zahl 1–12, unabhängig vom Jahr. | Keine Korrektur, nur umbenannt. |
| `preis_eur` | `Preis [€]` | Verkaufspreis des Produkts, `float`, 2 Nachkommastellen. | `€`-Zeichen entfernt, Komma durch Punkt ersetzt, in `float` umgewandelt und auf 2 Nachkommastellen gerundet. |
| `wettbewerber_preis_eur` | `Wettbewerberpreis [€]` | Vergleichspreis des stärksten Wettbewerbers, `float`, 2 Nachkommastellen. | Keine inhaltliche Korrektur nötig (war bereits sauber numerisch), nur zur Konsistenz auf 2 Nachkommastellen gerundet. Faktor-Check gegen `Preis [€]` ohne Auffälligkeiten. |
| `marketingbudget_eur` | `Marketingbudget [€]` | Monatliches Marketingbudget für das Produkt. | 433 fehlende Werte im Rohdatensatz (432 nach Duplikat-Entfernung) mit dem Median je Kategorie aufgefüllt – markiert über Flag `Marketingbudget geschätzt`. |
| `kampagne_aktiv` | `Kampagne aktiv` | Ob in diesem Monat eine Marketingkampagne für das Produkt lief (0/1). | Keine Korrektur nötig – vollständig befüllt. |
| `lagerbestand` | `Lagerbestand [Stück]` | Lagerbestand am Monatsende in Stück, `int`. | Text-Zusatz `"Stueck"` bei 288 Zeilen entfernt, danach in `int` umgewandelt. |
| `bewertungen_durchschnitt` | `Bewertung Durchschnitt` | Durchschnittliche Kundenbewertung des Produkts – pro Produkt über alle Monate konstant. | 576 fehlende Werte per Forward-/Backward-Fill je `Produkt-ID` rekonstruiert (kein Schätzwert, da der Wert pro Produkt konstant ist) – markiert über Flag `Bewertung ergänzt`. |
| `bewertungen_anzahl` | `Anzahl Bewertungen` | Anzahl abgegebener Kundenbewertungen. | Keine Korrektur nötig – vollständig befüllt. |
| `vormonat_umsatz_eur` | `Umsatz Vormonat [€]` | Umsatz des jeweiligen Vormonats desselben Produkts. | Keine Korrektur der Werte selbst – stimmte bereits exakt mit der strukturellen NaN-Logik überein (0 Abweichungen). Nur das erklärende Flag `Neues Produkt` ergänzt. |
| `letzte_3_monate_umsatz_eur_avg` | `Durchschnitt 3 Vormonate [€]` | Durchschnitt der letzten 3 Monatsumsätze desselben Produkts. | **Datenfehler korrigiert:** 1.799 Zeilen (Monat 1–3 des Jahres 2024) enthielten fälschlich einen Wert, obwohl noch keine 3 vollständigen Vormonate vorliegen konnten – auf `NaN` gesetzt. Markiert über Flag `Hat 3-Monats-Durchschnitt`. |
| `vorjahr_monat_umsatz_eur` | `Umsatz Vorjahresmonat [€]` | Umsatz desselben Monats im Vorjahr. | Keine Korrektur der Werte selbst – stimmte bereits exakt mit der Logik überein (0 Abweichungen). Nur das erklärende Flag `Hat Vorjahreswert` ergänzt. |
| `umsatz_eur` | `Umsatz [€]` | Tatsächlicher Umsatz des Produkts in diesem Monat – die Zielgröße für die spätere Umsatzprognose. | **Datenfehler korrigiert:** 5 Zeilen mit unplausiblen Werten (Platzhalter-Extremwerte wie `999.999`, ein negativer Wert, ein falsch übernommener Nullwert) über Kreuzvalidierung mit `Umsatz Vormonat [€]` der Folgezeile exakt rekonstruiert. Markiert über Flag `Umsatz korrigiert`. |

## 2. Neue Spalten ohne Original-Gegenstück (7)

Diese Spalten existierten in `verkaufe.csv` nicht. `Jahr` ist eine reine
Ableitung, die restlichen 6 sind Flags (0/1), die jede Korrektur aus
Tabelle 1 nachvollziehbar machen, ohne die zugehörige Werte-Spalte selbst
zu verändern.

| Neue Spalte | Wofür steht sie | Herkunft |
|---|---|---|
| `Jahr` | Aus `Monat` abgeleitetes Kalenderjahr (2024 oder 2025). | Keine Korrektur – reine Ableitung aus `Monat`, kein Bezug zu einem Datenfehler. |
| `Marketingbudget geschätzt` | `1` = Wert in `Marketingbudget [€]` war ursprünglich `NaN` und wurde per Median je Kategorie aufgefüllt. `0` = Originalwert. | Dokumentiert die Korrektur an `marketingbudget_eur`. |
| `Bewertung ergänzt` | `1` = Wert in `Bewertung Durchschnitt` war ursprünglich `NaN` und wurde rekonstruiert. `0` = Originalwert. | Dokumentiert die Korrektur an `bewertungen_durchschnitt`. |
| `Neues Produkt` | `1` = 1. Verkaufsmonat des Produkts, `Umsatz Vormonat [€]` ist entsprechend strukturell `NaN`. `0` = es existiert ein Vormonat. | Keine Korrektur – dokumentiert nur die bereits korrekte Struktur von `vormonat_umsatz_eur`. |
| `Hat 3-Monats-Durchschnitt` | `1` = `Durchschnitt 3 Vormonate [€]` ist ein echter, nachgerechneter Wert. `0` = strukturell `NaN`. | Dokumentiert die Korrektur an `letzte_3_monate_umsatz_eur_avg`. |
| `Hat Vorjahreswert` | `1` = `Umsatz Vorjahresmonat [€]` ist befüllt. `0` = strukturell `NaN` (Jahr 2024, kein Vorjahr vorhanden). | Keine Korrektur – dokumentiert nur die bereits korrekte Struktur von `vorjahr_monat_umsatz_eur`. |
| `Umsatz korrigiert` | `1` = Wert in `Umsatz [€]` wurde als Datenfehler identifiziert und exakt rekonstruiert (5 von 14.400 Zeilen). `0` = Originalwert. | Dokumentiert die Korrektur an `umsatz_eur`. |

## Kurzreferenz: finale Spaltenreihenfolge

```
Produkt-ID, Kategorie, Hersteller, Monat, Jahr, Kalendermonat,
Preis [€], Wettbewerberpreis [€],
Marketingbudget [€], Marketingbudget geschätzt,
Kampagne aktiv, Lagerbestand [Stück],
Bewertung Durchschnitt, Bewertung ergänzt, Anzahl Bewertungen,
Umsatz Vormonat [€], Neues Produkt,
Durchschnitt 3 Vormonate [€], Hat 3-Monats-Durchschnitt,
Umsatz Vorjahresmonat [€], Hat Vorjahreswert,
Umsatz [€], Umsatz korrigiert
```

14.400 Zeilen × 23 Spalten (Rohdatensatz: 14.430 Zeilen × 16 Spalten,
30 Zeilen davon waren Duplikate).
