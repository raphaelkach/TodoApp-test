# Übung: Minimaler Aufbau TODO-App mit Streamlit (30 min)

Versuchen umzusetzen:
- Software-Qualitätseigenschaften gemäß ISO 25010


Aufgabe: Eine funktionale, minimalistische TODO-App erstellen. 

- Grundfunktionen: 
    - Session State initialisieren
    - Möglichkeit Aufgaben hinzufügen (Textfeld, Button, … )
    - Übernehmen Sie die Aufgabe in die Liste im Session State
    - Lassen Sie Aufgaben mit Checkboxen anzeigen
    - Löschfunktion

Aufgabe: Design in Streamlit umsetzen
- Schritte:
    - Übertragen Sie jede UI-Komponente aus Figma in Streamlit
    - Testen Sie Zwischenschritte direkt in Streamlit
    - Prüfen Sie, ob die Nielsen-Heuristiken erfüllt sind
- Ziel: Ihre Streamlit-App entspricht dem heutigen Figma-Design

Übung: Überprüfung und Integration in Streamlit
- Überprüfen Sie Ihr Design: Stellen Sie sicher, dass mindestens fünf der vorgegebenen Anforderungen in Ihrem Design umgesetzt sind.
- Falls erforderlich: Ergänzen Sie die fehlenden Anforderungen in Ihrem Design.
- Integration: Übertragen Sie das vollständige Design in Ihre Streamlit-App, zunächst nur das Design!

Übung: Responsive TODO-App in Streamlit
- Aufgabe: Implementieren Sie ein responsives Design für die TODOApp in Streamlit, das auf verschiedenen Geräte (Desktop, Smartphone) gut aussieht und benutzerfreundlich ist

Aufgabe: Modellierung der TODO-App nach dem MVC-Architekturmuster
- 1. Definieren Sie für jede der drei MVC-Schichten mindestens die folgenden Elemente:
    - Model:
        - zentrale Domänenobjekte (z. B. „Task“), Datenzugriff, Validierungslogik
    - View:
        - UI-Elemente
    - Controller:
        - Steuerungslogik
        - Methoden für das Anlegen, Ändern, Löschen und Anzeigen von Aufgaben (siehe Funktionale Anforderungen)
- 2. Kurze Beschreibung der Architektur
    - Verfassen Sie eine Begründung (max. 10 Sätze), warum MVC für diese Anwendung geeignet ist
    - Beschreiben Sie kurz die Verantwortlichkeiten jeder Komponente.

-> ABGABE: Readme-Datei mit Code (Ende Semester)

Aufgabe: Implementieren Sie die Komponenten der MVC-Architektur für die TODO-App
    - Implementieren Sie für die TODO-App jeweils eine grundlegende Version der drei zuvor erstellten MVC-Schichten 
    - Ergänzen Sie die README-Datei um eine kurze Beschreibung, welche Klassen welche Rollen innerhalb des MVC-Architekturmodells übernehmen

Aufgabe: Unit Tests für TODO-App
Erstellen Sie eine vollständige Suite von Unit Tests für die TODO-App. Verwenden Sie dafür das Framework pytest. Die Tests sollen die Logik der Anwendung vollständig abdecken, ohne externe Systeme einzubeziehen. 
- Jeder Test soll klar das AAA-Muster verwenden.
- Jeder Test muss unabhängig voneinander lauffähig sein.
- Ihre Tests sollen mindestens 80 % des Codes abdecken (Sie können coverage.py nutzen, um das zu messen).
Erstellen Sie mindestens folgende Unit Tests:
- Hinzufügen eines neuen TODO-Items
- Entfernen eines Items
- Markieren als erledigt / nicht erledigt
- Bearbeiten eines Items
- Optional: Fehlerfälle oder Randbedingungen (z. B. leere Titel, doppelte Titel)
Abgabe: test_unit.py

Aufgabe: Integrationstests für eine TODO-App
Erstellen Sie 3 Integrationstests, z.B. 
- Mehrere Aufgaben erstellen und sicherstellen, dass die Repository-Schicht konsistent bleibt
- Aktualisieren eines vorhandenen Items (z. B. Status ändern) -> → Status korrekt im Repository aktualisiert
- Leere Aufgabe → Repository wirft kontrollierten Fehler
- Löschen eines Items und Überprüfung, ob es aus dem Repository verschwindet
Abgabe: test_intergration.py

Aufgabe: Systemtests für die TODO-App
Ziel: Prüfen, dass das komplette System technisch korrekt arbeitet, inkl. Service, Repository und evtl. UI-Elemente (kontrolliert, ohne echten Browser).
Framework: pytest

Szenarien:
    - Aufgabe anlegen → geprüft wird Speicherung und Abruf
    - Aufgabe als erledigt markieren → Status korrekt im System
    - Aufgabe löschen → System konsistent
    - Fehlerfälle → kontrollierte Fehlermeldung
Abgabe: system_test.py


Aufgabe: End-to-End-Test (E2E) für die TODO-App
Ziel: Prüfen, dass ein Benutzer alle Abläufe erfolgreich durchführen kann, inklusive Frontend (Streamlit), Backend und Persistenz.

Framework: pytest + Playwright

Mögliche Szenarien:
    - Aufgabe über UI anlegen → sichtbar und gespeichert
    - Aufgabe als erledigt markieren → Status sichtbar und gespeichert
    - Aufgabe löschen → aus UI und Persistenz entfernt
    - Fehlerfall: leere Aufgabe → Fehlermeldung sichtbar
    - Optional: App neu starten → Aufgaben korrekt wiederhergestellt




Funktionale Anforderungen
- Todo löschen
- Todo bearbeiten
- Todo als erledigt markieren
- Das System muss Aufgaben in einer Liste anzeigen.
- Das System soll Aufgaben nach Status (offen/erledigt) filtern können.

- Der Nutzer soll Aufgaben bis zu fünf Kategorien zuordnen können, die er selbst erstellen und löschen kann.
- Jede Aufgabe soll ein Fälligkeitsdatum enthalten können, das über einen Kalenderpicker in unter 3 Klicks ausgewählt werden kann.
- Die App soll es dem Nutzer ermöglichen, innerhalb von maximal 5 Sekunden eine neue Aufgabe mit Titel anzulegen.


## Update Prompts
Dabei sollen die Buttons in streamlit umgesetzt werden und nicht mit css. Dabei soll nur css genutzt werden, wenn es anders nicht möglich ist mit streamlit.
Ich möchte eine Todo App mit streamlit machen nach der Architektur von MVC. Wie baut man das richtig nach der Vorlesung

Ich möchte erstmal hier mit Starten nach MVC:
Aufgabe: Eine funktionale, minimalistische TODO-App erstellen. 

- Grundfunktionen: 
    - Session State initialisieren
    - Möglichkeit Aufgaben hinzufügen (Textfeld, Button, … )
    - Übernehmen Sie die Aufgabe in die Liste im Session State
    - Lassen Sie Aufgaben mit Checkboxen anzeigen
    - Löschfunktion

Für die Icons sollen immer die Icons von Google genutzt werden als: https://fonts.google.com/icons?icon.query=task&icon.size=24&icon.color=%236b52a2&icon.platform=web