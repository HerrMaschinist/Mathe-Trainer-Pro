# Mathe Trainer Pro By WIMAEDV

**Mathe Trainer Pro** ist eine interaktive Desktop-Anwendung, die Schülern dabei hilft, mathematische Fähigkeiten zu üben – maßgeschneidert nach Klassenstufen von 1 bis 4. Das Programm generiert abwechslungsreiche Aufgaben (Addition, Subtraktion, Multiplikation, Division, Verdoppeln, Halbieren, Sachaufgaben, Brüche, Dezimalzahlen, u.v.m.) und passt den Schwierigkeitsgrad sowie die Aufgabenart dynamisch an, basierend auf der gewählten Klassenstufe und dem aktuellen Fortschritt des Benutzers.

## Features

- **Klassenstufenspezifische Übungen**  
  - **1. Klasse:** Zahlen im Zahlenraum bis 20, Vorwärts-/Rückwärtszählen, Addition, Subtraktion, Verdoppeln, Halbieren, erste geometrische Formen sowie Größen (Geld, Zeit, Längen) und Muster.
  - **2. Klasse:** Erweiterter Zahlenraum bis 100, Addition, Subtraktion, erste Multiplikation und Division, einfache Sachaufgaben.
  - **3. Klasse:** Zahlenraum bis 1.000, festes Einmaleins, Division mit Rest, schriftliche Rechenmethoden, Geometrie (Symmetrie, Flächen, Umfang) und komplexere Sachaufgaben.
  - **4. Klasse:** Zahlenraum bis 1.000.000, schriftliche Multiplikation/Division, Einführung in Dezimalzahlen und einfache Brüche, Volumenberechnungen, komplexe Sachaufgaben und Diagramme.

- **Adaptives Level- und XP-System**  
  Nutzer sammeln Erfahrungspunkte (XP) mit jeder korrekt gelösten Aufgabe. Sobald eine XP-Schwelle erreicht wird, steigt der Nutzer im Level auf. Erreichte Levels werden als Achievements angezeigt.

- **Detaillierte Statistiken**  
  Nach jeder Sitzung werden Punkte, Anzahl richtiger und falscher Antworten sowie die durchschnittliche Bearbeitungszeit pro Aufgabe angezeigt. Am Ende wird auch ein "Tipp des Tages" eingeblendet.

- **Robustes Logging**  
  Wichtige Aktionen und Fehler werden protokolliert, was die Fehlerdiagnose und zukünftige Erweiterungen erleichtert.

- **Flexible Ressourcenverwaltung**  
  Benutzerprofile werden in einem Datenordner im Benutzerverzeichnis (unter `MatheTrainerProData`) gespeichert, um sicherzustellen, dass Schreibrechte vorhanden sind.

- **Modernes & adaptives GUI**  
  Die Oberfläche ist benutzerfreundlich gestaltet und ermöglicht einfache Navigation zwischen Auswahl-, Übungs- und Ergebnis-Seite.

## Voraussetzungen

- **Python 3.x** (geprüft mit Python 3.8+)
- **PyQt6** – für die grafische Benutzeroberfläche
- Weitere Abhängigkeiten: `json`, `time`, `os`, `logging`, `random` – alle Standardmodule in Python
