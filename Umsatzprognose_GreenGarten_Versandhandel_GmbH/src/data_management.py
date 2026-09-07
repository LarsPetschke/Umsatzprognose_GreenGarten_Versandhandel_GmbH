"""
Data Management – Untersuchung des Rohdatensatzes
=================================================

Dieses Skript dient der ersten Analyse des Datensatzes 'verkaufe.csv'.
Ziel ist es, die Struktur, Spalten, Datentypen und Inhalte zu verstehen
und erste Qualitätsprobleme sichtbar zu machen.

Alle Schritte sind bewusst einfach und nachvollziehbar gehalten,
damit die Datenqualität klar dokumentiert werden kann.
"""

import pandas as pd
import numpy as np
import os

# %%
# -------------------------------------------------------------------
# 1. Rohdaten laden
# -------------------------------------------------------------------

# Pfad zur Rohdatei
path = "data/raw/verkaufe.csv"

# Daten laden
df_verkaufe_raw = pd.read_csv(path)

print("=== Datensatz erfolgreich geladen ===\n")

# %%
# -------------------------------------------------------------------
# 2. Überblick über Struktur und Spalten
# -------------------------------------------------------------------

print(f"Der Datensatz besteht aus {df_verkaufe_raw.shape[0]} Zeilen "
      f"und {df_verkaufe_raw.shape[1]} Spalten.\n")

print("Spaltennamen:")
print(df_verkaufe_raw.columns.tolist())

print("\nDatentypen der Spalten:")
print(df_verkaufe_raw.dtypes)

# %%
# -------------------------------------------------------------------
# 3. Beispielzeilen anzeigen
# -------------------------------------------------------------------

print("\n=== Erste fünf Zeilen des Datensatzes ===")
print(df_verkaufe_raw.head())

# %%
# -------------------------------------------------------------------
# 4. Fehlende Werte untersuchen
# -------------------------------------------------------------------

print("\n=== Fehlende Werte pro Spalte ===")
print(df_verkaufe_raw.isna().sum())

# %%
# -------------------------------------------------------------------
# 5. Einzigartige Werte pro Spalte (erste 20)
# -------------------------------------------------------------------

print("\n=== Einzigartige Werte (erste 20 je Spalte) ===")
for col in df_verkaufe_raw.columns:
    print(f"\nSpalte: {col}")
    print(df_verkaufe_raw[col].unique()[:20])

print("\n=== Untersuchung abgeschlossen ===")


# %%
# =====================================================================
# TEIL 2: DATENQUALITAET DOKUMENTIEREN UND BEHEBEN
# =====================================================================
#
# Die Untersuchung in Teil 1 hat folgende Qualitaetsprobleme aufgedeckt:
#
#   6.  'monat'         - drei unterschiedliche Datumsformate
#                          (MM.YYYY, MM/YYYY, YYYY-MM)
#   7.  'preis_eur'      - teilweise als Text mit Komma und "Euro-Zeichen"
#                          gespeichert (z. B. "36,77 EUR")
#   8.  'lagerbestand'   - teilweise mit dem Zusatz "Stueck" versehen
#                          (z. B. "65 Stueck")
#   9.  'kategorie'      - 24 statt 6 Schreibweisen durch
#                          Gross-/Kleinschreibung, Umlaut-Varianten und
#                          Abkuerzungen (z. B. "SAATGUT", "Saat",
#                          "Duengemittel", "DUENGER")
#   10. 30 vollstaendig doppelte Zeilen (identisch in allen Spalten)
#   11. Zwei unplausible Werte in 'umsatz_eur' (999.999 und 750.000)
#       sowie zwei negative Werte (-1 und -150)
#
# Fehlende Werte in folgenden Spalten werden NICHT als Fehler behandelt
# und bleiben bewusst als fehlend (NaN) erhalten - die genaue Ursache
# wurde je Spalte einzeln geprueft:
#
#   - 'vormonat_umsatz_eur' (600 fehlend): strukturell bedingt, betrifft
#     exakt den ersten Monat (2024-01) jedes der 600 Produkte, fuer den
#     es keinen Vormonat gibt.
#   - 'vorjahr_monat_umsatz_eur' (7.200 fehlend): strukturell bedingt,
#     betrifft exakt alle Zeilen des Jahres 2024, da fuer 2024 kein
#     Vorjahreswert im Datensatz vorhanden ist (Datensatz beginnt 2024).
#   - 'bewertungen_durchschnitt' (576 fehlend): fehlt vollstaendig fuer
#     einzelne Produkte (der Wert ist je Produkt konstant ueber alle
#     Monate) - vermutlich Produkte ohne Kundenbewertungen.
#   - 'marketingbudget_eur' (432 fehlend): keine erkennbare Systematik
#     feststellbar (fehlt sowohl bei aktiver als auch bei inaktiver
#     Kampagne, 'kampagne_aktiv'), daher als einfache Datenluecke
#     eingestuft statt als inhaltlich begruendbar.
#   - 'letzte_3_monate_umsatz_eur_avg' (1 fehlend): Einzelfall.
#
# Jedes Problem wird im Folgenden zunaechst anhand der Daten belegt und
# direkt im Anschluss behoben. Die Originaldaten (df_verkaufe_raw)
# bleiben dabei unveraendert; alle Bereinigungsschritte erfolgen auf
# einer Kopie (df_verkaufe_clean).

print("\n\n=== TEIL 2: Datenqualitaet dokumentieren und beheben ===")

df_verkaufe_clean = df_verkaufe_raw.copy()

# %%
# -------------------------------------------------------------------
# 6. Datumsformate in 'monat' vereinheitlichen
# -------------------------------------------------------------------
print("\n--- 6. Datumsformate in 'monat' ---")

muster = df_verkaufe_clean["monat"].astype(str).str.replace(r"\d", "#", regex=True)
print("Gefundene Formate (Ziffern durch '#' ersetzt):")
print(muster.value_counts())


def monat_vereinheitlichen(wert):
    """Wandelt 'monat' unabhaengig vom Ursprungsformat in 'YYYY-MM' um.

    Das Format 'YYYY-MM' wird bewusst gewaehlt (statt z. B. 'MM.YYYY'):
    Pandas liest 'MM.YYYY' beim erneuten Einlesen der CSV-Datei sonst als
    Kommazahl ein (z. B. wird "01.2024" zu 1.2024), da der Punkt als
    Dezimaltrenner interpretiert wird. 'YYYY-MM' ist dagegen eindeutig als
    Text erkennbar und zusaetzlich chronologisch sortierbar.
    """
    text = str(wert).replace("/", ".").replace("-", ".")
    erster_teil, zweiter_teil = text.split(".")
    if len(erster_teil) == 4:          # Format war 'YYYY-MM' -> Reihenfolge bereits richtig
        jahr, monat_zahl = erster_teil, zweiter_teil
    else:                               # Format war 'MM.YYYY' oder 'MM/YYYY' -> Reihenfolge tauschen
        monat_zahl, jahr = erster_teil, zweiter_teil
    return f"{jahr}-{int(monat_zahl):02d}"


df_verkaufe_clean["monat"] = df_verkaufe_clean["monat"].apply(monat_vereinheitlichen)

print("\nBeispiele nach der Vereinheitlichung:")
print(df_verkaufe_clean["monat"].head(5))
noch_abweichend = (~df_verkaufe_clean["monat"].str.match(r"^\d{4}-\d{2}$")).sum()
print(f"Verbleibende, nicht konforme Werte: {noch_abweichend}")


# %%
# -------------------------------------------------------------------
# 7. Preisangabe 'preis_eur' bereinigen
# -------------------------------------------------------------------
print("\n--- 7. Format von 'preis_eur' ---")

mit_euro_zeichen = df_verkaufe_clean["preis_eur"].astype(str).str.contains("€")
print(f"Werte mit Euro-Zeichen und Komma: {mit_euro_zeichen.sum()} von {len(df_verkaufe_clean)}")
print("Beispiele:", df_verkaufe_clean.loc[mit_euro_zeichen, "preis_eur"].unique()[:5])


def preis_bereinigen(wert):
    """Entfernt das Euro-Zeichen, wandelt Komma in Punkt um und liefert einen float-Wert."""
    text = str(wert).replace("€", "").replace(",", ".").strip()
    return float(text)


df_verkaufe_clean["preis_eur"] = df_verkaufe_clean["preis_eur"].apply(preis_bereinigen)

print("\nKennzahlen nach der Bereinigung:")
print(df_verkaufe_clean["preis_eur"].describe())


# %%
# -------------------------------------------------------------------
# 8. Lagerbestand 'lagerbestand' bereinigen
# -------------------------------------------------------------------
print("\n--- 8. Text-Zusatz in 'lagerbestand' ---")

mit_text_zusatz = df_verkaufe_clean["lagerbestand"].astype(str).str.contains("[A-Za-z]")
print(f"Werte mit Text-Zusatz: {mit_text_zusatz.sum()} von {len(df_verkaufe_clean)}")
print("Beispiele:", df_verkaufe_clean.loc[mit_text_zusatz, "lagerbestand"].unique()[:5])

df_verkaufe_clean["lagerbestand"] = (
    df_verkaufe_clean["lagerbestand"]
    .astype(str)
    .str.replace("Stueck", "", regex=False)
    .str.strip()
    .astype(int)
)

print("\nKennzahlen nach der Bereinigung:")
print(df_verkaufe_clean["lagerbestand"].describe())


# %%
# -------------------------------------------------------------------
# 9. Schreibweisen in 'kategorie' vereinheitlichen
# -------------------------------------------------------------------
print("\n--- 9. Schreibweisen in 'kategorie' ---")

print(f"Urspruenglich {df_verkaufe_clean['kategorie'].nunique()} unterschiedliche Werte:")
print(df_verkaufe_clean["kategorie"].value_counts())


def kategorie_normalisieren(wert):
    """Bringt eine Kategorie-Angabe auf eine einheitliche, vergleichbare Form."""
    text = str(wert).strip().lower()
    text = (text.replace("ae", "ae").replace("ä", "ae").replace("ö", "oe")
                .replace("ü", "ue").replace("ß", "ss"))
    return text


# Zuordnung aller in den Rohdaten vorkommenden Schreibweisen zu den
# sechs tatsaechlichen Produktkategorien.
KATEGORIE_MAPPING = {
    "pflanzen": "Pflanzen",
    "pflanze": "Pflanzen",
    "werkzeuge": "Werkzeuge",
    "werkzeug": "Werkzeuge",
    "saatgut": "Saatgut",
    "saat": "Saatgut",
    "toepfe": "Toepfe",
    "duengemittel": "Duengemittel",
    "duenger": "Duengemittel",
    "bewaesserung": "Bewaesserung",
}

df_verkaufe_clean["kategorie"] = (
    df_verkaufe_clean["kategorie"].apply(kategorie_normalisieren).map(KATEGORIE_MAPPING)
)

print(f"\nNach der Vereinheitlichung noch {df_verkaufe_clean['kategorie'].nunique()} Kategorien:")
print(df_verkaufe_clean["kategorie"].value_counts())
print("Nicht zuordenbare Werte:", df_verkaufe_clean["kategorie"].isna().sum())


# %%
# -------------------------------------------------------------------
# 10. Vollstaendige Duplikate entfernen
# -------------------------------------------------------------------
print("\n--- 10. Vollstaendig doppelte Zeilen ---")

anzahl_duplikate = df_verkaufe_clean.duplicated().sum()
print(f"Gefundene Duplikate: {anzahl_duplikate}")
print("Erwartung laut Struktur: 600 Produkte x 24 Monate (2024+2025) = 14.400 Zeilen; "
      f"tatsaechlich vorhanden: {len(df_verkaufe_clean)} "
      f"-> {len(df_verkaufe_clean) - 14400} zusaetzliche, doppelte Zeilen.")

df_verkaufe_clean = df_verkaufe_clean.drop_duplicates()
print(f"Zeilen nach Entfernen der Duplikate: {len(df_verkaufe_clean)}")


# %%
# -------------------------------------------------------------------
# 11. Unplausible Werte in 'umsatz_eur' markieren
# -------------------------------------------------------------------
print("\n--- 11. Ausreisser und Fehlwerte in 'umsatz_eur' ---")

print("Die beiden hoechsten Umsatzwerte:")
print(df_verkaufe_clean.nlargest(2, "umsatz_eur")[["produkt_id", "monat", "umsatz_eur"]])
print("-> Beide liegen weit ueber dem naechsthoeheren, plausiblen Wert "
      "(rund 20.600) und werden als Erfassungs-/Platzhalterfehler eingestuft.")

print("\nNegative Umsatzwerte (fachlich nicht moeglich):")
print(df_verkaufe_clean.loc[df_verkaufe_clean["umsatz_eur"] < 0,
                             ["produkt_id", "monat", "umsatz_eur"]])

# Fehlerhafte Werte werden auf NaN gesetzt statt die Zeile zu loeschen,
# damit das betroffene Produkt im jeweiligen Monat sichtbar bleibt.
unplausibel = (df_verkaufe_clean["umsatz_eur"] > 100_000) | (df_verkaufe_clean["umsatz_eur"] < 0)
print(f"\nAls fehlerhaft markierte Werte: {unplausibel.sum()}")

df_verkaufe_clean.loc[unplausibel, "umsatz_eur"] = np.nan


# %%
# -------------------------------------------------------------------
# 12. Bereinigten Datensatz speichern
# -------------------------------------------------------------------
print("\n--- 12. Bereinigten Datensatz speichern ---")

os.makedirs("data/interim", exist_ok=True)

INTERIM_PATH = "data/interim/verkaufe_clean.csv"
df_verkaufe_clean.to_csv(INTERIM_PATH, index=False)

print(f"Bereinigter Datensatz gespeichert unter: {INTERIM_PATH}")
print(f"Finale Form: {df_verkaufe_clean.shape[0]} Zeilen, "
      f"{df_verkaufe_clean.shape[1]} Spalten "
      f"(Rohdatensatz: {df_verkaufe_raw.shape[0]} Zeilen)")

print("\n=== Datenbereinigung abgeschlossen ===")
print("\nHinweis: Die abgeleiteten Umsatzspalten 'vormonat_umsatz_eur', "
      "'letzte_3_monate_umsatz_eur_avg' und 'vorjahr_monat_umsatz_eur' "
      "enthalten an denselben Stellen voraussichtlich aehnliche Fehlwerte, "
      "da sie sich aus 'umsatz_eur' ableiten. Das wird im naechsten "
      "Schritt (Feature-Aufbereitung) geprueft.")
