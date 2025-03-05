"""
Mathe Trainer Pro - Ultimativ verbesserte Version

Features:
- Klassenstufenspezifische Übungsaufgaben (Klasse 1 bis 4)
- Adaptives Level- und XP-System mit Achievements und Tips
- Detaillierte Statistiken & Fortschrittsanzeige
- Logging aller Aktionen
- Flexible Ressourcenpfad-Ermittlung (profiles.json wird im Datenordner im Benutzerverzeichnis abgelegt)
- Robuste Eingabevalidierung und Fehlermeldungen
- Erweiterte GUI mit Menüoptionen
"""

import sys
import random
import json
import time
import os
import logging
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QStackedWidget, QMessageBox, QComboBox, 
    QProgressBar, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QAction

# Konfiguriere das Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

class Difficulty(Enum):
    EINFACH = "Einfach"
    MITTEL = "Mittel"
    SCHWER = "Schwer"

def get_data_dir():
    """
    Ermittelt den Pfad zum Datenordner im Benutzerverzeichnis.
    Hier werden externe Dateien wie profiles.json gespeichert.
    """
    data_dir = os.path.join(os.path.expanduser("~"), "MatheTrainerProData")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def resource_path(filename):
    """
    Gibt den absoluten Pfad zu einer Ressourcendatei relativ zum Datenordner zurück.
    """
    return os.path.join(get_data_dir(), filename)

def get_tip_of_the_day():
    """
    Liefert einen zufälligen mathematischen Tipp.
    """
    tips = [
        "Denke daran: Übung macht den Meister!",
        "Beim Teilen immer mal wieder den Rest überprüfen.",
        "Tipp: Schau dir zuerst die Aufgabenstellung genau an.",
        "Manchmal hilft es, Zahlen zu zerlegen.",
        "Mathematik ist logisches Denken – bleib ruhig und strukturiert!"
    ]
    return random.choice(tips)

class MathTrainer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathe Trainer Pro")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #222; color: white; font-size: 16px;")
        
        # Initiale Variablen
        self.current_solution = None
        self.score = 0
        self.total_problems = 10
        self.current_problem_number = 0
        self.timer_duration = 30000  # 30 Sekunden pro Aufgabe
        self.start_time = None
        self.total_time = 0
        self.correct_answers = 0
        self.wrong_answers = 0

        self.user_profiles = self.load_profiles()
        self.current_user = None

        # Timer initialisieren
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_out)
    
        # GUI‑Elemente
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Menü erstellen
        self.create_menus()
        # Seiten erstellen
        self.selection_page = self.create_selection_page()
        self.problem_page = self.create_problem_page()
        self.result_page = self.create_result_page()
        self.stacked_widget.addWidget(self.selection_page)
        self.stacked_widget.addWidget(self.problem_page)
        self.stacked_widget.addWidget(self.result_page)
        
        logging.info("Mathe Trainer Pro gestartet")
        self.show()
    
    def create_menus(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Einstellungen')
        
        theme_action = QAction('Thema ändern', self)
        theme_action.triggered.connect(self.change_theme)
        settings_menu.addAction(theme_action)
        
        font_action = QAction('Schriftgröße anpassen', self)
        font_action.triggered.connect(self.change_font_size)
        settings_menu.addAction(font_action)
        
        reset_action = QAction('Fortschritt zurücksetzen', self)
        reset_action.triggered.connect(self.reset_progress)
        settings_menu.addAction(reset_action)
    
    def change_theme(self):
        QMessageBox.information(self, "Thema ändern", "Die Funktion 'Thema ändern' ist noch nicht implementiert.")
    
    def change_font_size(self):
        QMessageBox.information(self, "Schriftgröße anpassen", "Die Funktion 'Schriftgröße anpassen' ist noch nicht implementiert.")
    
    def reset_progress(self):
        reply = QMessageBox.question(self, 'Fortschritt zurücksetzen',
                                     'Bist du sicher, dass du deinen Fortschritt zurücksetzen möchtest?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.user_profiles[self.current_user] = {
                "score": 0,
                "level": 1,
                "xp": 0,
                "achievements": []
            }
            self.save_profiles()
            QMessageBox.information(self, "Zurückgesetzt", "Dein Fortschritt wurde zurückgesetzt.")
            logging.info("Fortschritt für Benutzer %s zurückgesetzt", self.current_user)
    
    def load_profiles(self):
        try:
            profiles_path = resource_path("profiles.json")
            with open(profiles_path, "r") as f:
                profiles = json.load(f)
                # Sicherstellen, dass alle Schlüssel vorhanden sind
                for user in profiles:
                    profiles[user].setdefault("score", 0)
                    profiles[user].setdefault("level", 1)
                    profiles[user].setdefault("xp", 0)
                    profiles[user].setdefault("achievements", [])
                logging.info("Profile erfolgreich geladen")
                return profiles
        except Exception as e:
            logging.warning("Profile nicht gefunden oder fehlerhaft: %s", e)
            return {}
    
    def save_profiles(self):
        profiles_path = resource_path("profiles.json")
        with open(profiles_path, "w") as f:
            json.dump(self.user_profiles, f)
        logging.info("Profile gespeichert")
    
    def create_selection_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("Mathe Trainer Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Dein Name...")
        self.name_input.setStyleSheet("font-size: 18px;")
        self.name_input.setToolTip("Gib deinen Namen ein")
        layout.addWidget(self.name_input)
        
        self.class_selection = QComboBox()
        self.class_selection.addItems(["Klasse 1", "Klasse 2", "Klasse 3", "Klasse 4"])
        self.class_selection.setStyleSheet("font-size: 18px;")
        self.class_selection.setToolTip("Wähle deine Klassenstufe aus")
        layout.addWidget(self.class_selection)

        self.difficulty_selection = QComboBox()
        self.difficulty_selection.addItems(["Einfach", "Mittel", "Schwer"])
        self.difficulty_selection.setStyleSheet("font-size: 18px;")
        self.difficulty_selection.setToolTip("Wähle den Schwierigkeitsgrad")
        layout.addWidget(self.difficulty_selection)

        self.timer_checkbox = QCheckBox("Timer deaktivieren")
        self.timer_checkbox.setStyleSheet("font-size: 18px;")
        self.timer_checkbox.setToolTip("Aktiviere oder deaktiviere den Timer pro Aufgabe")
        layout.addWidget(self.timer_checkbox)
        
        self.num_problems_input = QLineEdit()
        self.num_problems_input.setPlaceholderText("Anzahl der Aufgaben (Standard: 10)")
        self.num_problems_input.setStyleSheet("font-size: 18px;")
        self.num_problems_input.setToolTip("Gib die Anzahl der Aufgaben pro Sitzung ein")
        layout.addWidget(self.num_problems_input)

        start_btn = QPushButton("Jetzt starten!")
        start_btn.setStyleSheet("background-color: #008080; color: white; padding: 10px; border-radius: 10px;")
        start_btn.clicked.connect(self.start_trainer)
        layout.addWidget(start_btn)
        
        return widget
    
    def create_problem_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        self.problem_label = QLabel("Aufgabe: ?")
        self.problem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.problem_label.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(self.problem_label)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Antwort eingeben...")
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer_input.setStyleSheet("font-size: 24px;")
        self.answer_input.setToolTip("Gib deine Antwort hier ein")
        # Bei Drücken der Eingabetaste wird Antwort geprüft
        self.answer_input.returnPressed.connect(self.check_answer)
        layout.addWidget(self.answer_input)

        check_btn = QPushButton("Antwort prüfen")
        check_btn.setStyleSheet("background-color: #008080; color: white; padding: 10px; border-radius: 10px;")
        check_btn.clicked.connect(self.check_answer)
        layout.addWidget(check_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_problems)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.highscore_label = QLabel("Punkte: 0 | Level: 1")
        self.highscore_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.highscore_label.setStyleSheet("font-size: 20px; color: yellow;")
        layout.addWidget(self.highscore_label)
        
        self.back_button = QPushButton("Zurück zum Hauptmenü")
        self.back_button.setStyleSheet("background-color: #d35400; color: white; padding: 10px; border-radius: 10px;")
        self.back_button.clicked.connect(self.go_to_main_menu)
        layout.addWidget(self.back_button)
        
        widget.setLayout(layout)
        return widget
    
    def create_result_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        self.result_label = QLabel("Ergebnisse")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(self.result_label)

        self.statistics_label = QLabel("")
        self.statistics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statistics_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(self.statistics_label)

        self.achievement_label = QLabel("")
        self.achievement_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.achievement_label.setStyleSheet("font-size: 20px; color: lightgreen;")
        layout.addWidget(self.achievement_label)

        self.restart_button = QPushButton("Erneut spielen")
        self.restart_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 10px;")
        self.restart_button.clicked.connect(self.restart_game)
        layout.addWidget(self.restart_button)
        
        self.back_to_menu_button = QPushButton("Zum Hauptmenü")
        self.back_to_menu_button.setStyleSheet("background-color: #d35400; color: white; padding: 10px; border-radius: 10px;")
        self.back_to_menu_button.clicked.connect(self.go_to_main_menu)
        layout.addWidget(self.back_to_menu_button)

        widget.setLayout(layout)
        return widget

    def time_out(self):
        QMessageBox.warning(self, "Zeit abgelaufen", "Zeit ist um! Eine neue Aufgabe wird geladen.")
        self.wrong_answers += 1
        self.current_problem_number += 1
        self.progress_bar.setValue(self.current_problem_number)
        logging.info("Aufgabe %d: Zeit abgelaufen", self.current_problem_number)
        if self.current_problem_number >= self.total_problems:
            self.end_game()
        else:
            self.generate_problem()

    def generate_problem(self):
        """Wählt basierend auf der Klassenstufe die passende Aufgabenmethode aus."""
        klasse = self.selected_class
        logging.debug("Generiere Aufgabe für %s", klasse)
        if klasse == "Klasse 1":
            self.generate_problem_klasse1()
        elif klasse == "Klasse 2":
            self.generate_problem_klasse2()
        elif klasse == "Klasse 3":
            self.generate_problem_klasse3()
        elif klasse == "Klasse 4":
            self.generate_problem_klasse4()
        else:
            QMessageBox.warning(self, "Fehler", "Unbekannte Klassenstufe.")
            self.go_to_main_menu()
            return
        self.answer_input.clear()
        if not self.timer_checkbox.isChecked():
            self.timer.start(self.timer_duration)
        else:
            self.timer.stop()
        self.start_time = time.time()

    # ---------------- Aufgaben für Klasse 1 ----------------
    def generate_problem_klasse1(self):
        aufgabentypen = ["Addition", "Subtraktion", "Verdoppeln", "Halbieren", "Zählen"]
        aufgabentyp = random.choice(aufgabentypen)
        logging.debug("Klasse 1 - Aufgabentyp: %s", aufgabentyp)
        
        if aufgabentyp == "Zählen":
            richtung = random.choice(["vorwärts", "rückwärts"])
            startzahl = random.randint(1, 19)
            if richtung == "vorwärts":
                self.problem_label.setText(f"Was kommt nach {startzahl}?")
                self.current_solution = startzahl + 1
            else:
                self.problem_label.setText(f"Was kommt vor {startzahl + 1}?")
                self.current_solution = startzahl
        elif aufgabentyp == "Verdoppeln":
            zahl = random.randint(1, 10)
            self.problem_label.setText(f"Verdopple {zahl}")
            self.current_solution = zahl * 2
        elif aufgabentyp == "Halbieren":
            zahl = random.randint(2, 20)
            while zahl % 2 != 0:
                zahl = random.randint(2, 20)
            self.problem_label.setText(f"Halbiere {zahl}")
            self.current_solution = zahl // 2
        else:
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            if aufgabentyp == "Addition":
                self.problem_label.setText(f"{num1} + {num2} = ?")
                self.current_solution = num1 + num2
            elif aufgabentyp == "Subtraktion":
                if num1 < num2:
                    num1, num2 = num2, num1
                self.problem_label.setText(f"{num1} - {num2} = ?")
                self.current_solution = num1 - num2

    # ---------------- Aufgaben für Klasse 2 ----------------
    def generate_problem_klasse2(self):
        aufgabentypen = ["Addition", "Subtraktion", "Multiplikation", "Division", "Sachaufgabe"]
        aufgabentyp = random.choice(aufgabentypen)
        logging.debug("Klasse 2 - Aufgabentyp: %s", aufgabentyp)
        
        if aufgabentyp == "Multiplikation":
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            self.problem_label.setText(f"{num1} × {num2} = ?")
            self.current_solution = num1 * num2
        elif aufgabentyp == "Division":
            num2 = random.randint(1, 10)
            self.current_solution = random.randint(1, 10)
            num1 = self.current_solution * num2
            self.problem_label.setText(f"{num1} ÷ {num2} = ?")
        elif aufgabentyp == "Sachaufgabe":
            sachaufgabe, loesung = self.generate_sachaufgabe_klasse2()
            self.problem_label.setText(sachaufgabe)
            self.current_solution = loesung
        else:
            num1 = random.randint(10, 100)
            num2 = random.randint(10, 100)
            if aufgabentyp == "Addition":
                self.problem_label.setText(f"{num1} + {num2} = ?")
                self.current_solution = num1 + num2
            elif aufgabentyp == "Subtraktion":
                if num1 < num2:
                    num1, num2 = num2, num1
                self.problem_label.setText(f"{num1} - {num2} = ?")
                self.current_solution = num1 - num2

    def generate_sachaufgabe_klasse2(self):
        dinge = ["Äpfel", "Bananen", "Kirschen", "Orangen"]
        ding = random.choice(dinge)
        anzahl1 = random.randint(1, 10)
        anzahl2 = random.randint(1, 10)
        loesung = anzahl1 + anzahl2
        sachaufgabe = f"Anna hat {anzahl1} {ding}, Ben hat {anzahl2} {ding}. Wie viele {ding} haben sie zusammen?"
        return sachaufgabe, loesung

    # ---------------- Aufgaben für Klasse 3 ----------------
    def generate_problem_klasse3(self):
        aufgabentypen = ["Addition", "Subtraktion", "Multiplikation", "Division mit Rest", "Sachaufgabe"]
        aufgabentyp = random.choice(aufgabentypen)
        logging.debug("Klasse 3 - Aufgabentyp: %s", aufgabentyp)
        
        if aufgabentyp == "Multiplikation":
            num1 = random.randint(1, 12)
            num2 = random.randint(1, 12)
            self.problem_label.setText(f"{num1} × {num2} = ?")
            self.current_solution = num1 * num2
        elif aufgabentyp == "Division mit Rest":
            divisor = random.randint(2, 12)
            dividend = random.randint(divisor + 1, 100)
            ganzzahl = dividend // divisor
            rest = dividend % divisor
            self.problem_label.setText(f"{dividend} ÷ {divisor} = ? (Ganze Zahl, Rest)")
            self.current_solution = (ganzzahl, rest)
        elif aufgabentyp == "Sachaufgabe":
            sachaufgabe, loesung = self.generate_sachaufgabe_klasse3()
            self.problem_label.setText(sachaufgabe)
            self.current_solution = loesung
        else:
            num1 = random.randint(100, 1000)
            num2 = random.randint(100, 1000)
            if aufgabentyp == "Addition":
                self.problem_label.setText(f"{num1} + {num2} = ?")
                self.current_solution = num1 + num2
            elif aufgabentyp == "Subtraktion":
                if num1 < num2:
                    num1, num2 = num2, num1
                self.problem_label.setText(f"{num1} - {num2} = ?")
                self.current_solution = num1 - num2

    def generate_sachaufgabe_klasse3(self):
        personen = ["Tom", "Sophie", "Max", "Lea"]
        person = random.choice(personen)
        geld = random.randint(50, 200)
        ausgabe1 = random.randint(10, 50)
        ausgabe2 = random.randint(5, 30)
        loesung = geld - ausgabe1 - ausgabe2
        sachaufgabe = f"{person} hat {geld}€. Er gibt {ausgabe1}€ für ein Buch und {ausgabe2}€ für Essen aus. Wie viel Geld hat {person} noch?"
        return sachaufgabe, loesung

    # ---------------- Aufgaben für Klasse 4 ----------------
    def generate_problem_klasse4(self):
        aufgabentypen = ["Addition", "Subtraktion", "Multiplikation", "Division", "Brüche", "Dezimalzahlen", "Sachaufgabe"]
        aufgabentyp = random.choice(aufgabentypen)
        logging.debug("Klasse 4 - Aufgabentyp: %s", aufgabentyp)
        
        if aufgabentyp == "Brüche":
            numerator = random.randint(1, 9)
            denominator = random.choice([2, 4, 5, 8, 10])
            self.problem_label.setText(f"Berechne den Wert von {numerator}/{denominator}")
            self.current_solution = numerator / denominator
        elif aufgabentyp == "Dezimalzahlen":
            num1 = round(random.uniform(1, 100), 2)
            num2 = round(random.uniform(1, 100), 2)
            op = random.choice(["+", "-"])
            self.problem_label.setText(f"{num1} {op} {num2} = ?")
            self.current_solution = num1 + num2 if op == "+" else num1 - num2
        elif aufgabentyp == "Sachaufgabe":
            sachaufgabe, loesung = self.generate_sachaufgabe_klasse4()
            self.problem_label.setText(sachaufgabe)
            self.current_solution = loesung
        else:
            if aufgabentyp == "Addition":
                num1 = random.randint(1000, 1000000)
                num2 = random.randint(1000, 1000000)
                self.problem_label.setText(f"{num1} + {num2} = ?")
                self.current_solution = num1 + num2
            elif aufgabentyp == "Subtraktion":
                num1 = random.randint(1000, 1000000)
                num2 = random.randint(1000, 1000000)
                if num1 < num2:
                    num1, num2 = num2, num1
                self.problem_label.setText(f"{num1} - {num2} = ?")
                self.current_solution = num1 - num2
            elif aufgabentyp == "Multiplikation":
                num1 = random.randint(100, 1000)
                num2 = random.randint(10, 100)
                self.problem_label.setText(f"{num1} × {num2} = ?")
                self.current_solution = num1 * num2
            elif aufgabentyp == "Division":
                num2 = random.randint(10, 100)
                self.current_solution = random.randint(100, 10000)
                num1 = self.current_solution * num2
                self.problem_label.setText(f"{num1} ÷ {num2} = ?")
    
    def generate_sachaufgabe_klasse4(self):
        firmen = ["Firma A", "Firma B", "Firma C"]
        firma = random.choice(firmen)
        produktionsrate = random.randint(50, 200)
        tage = random.randint(5, 20)
        loesung = produktionsrate * tage
        sachaufgabe = f"{firma} produziert täglich {produktionsrate} Artikel. Wie viele Artikel werden in {tage} Tagen produziert?"
        return sachaufgabe, loesung

    # ---------------- ENDE Klassenstufen-Aufgaben ----------------

    def start_trainer(self):
        name = self.name_input.text().strip()
        if name == "":
            QMessageBox.warning(self, "Fehler", "Bitte gib deinen Namen ein!")
            return
        self.current_user = name
        if name not in self.user_profiles:
            self.user_profiles[name] = {
                "score": 0,
                "level": 1,
                "xp": 0,
                "achievements": []
            }
            logging.info("Neues Profil für '%s' erstellt", name)
        else:
            self.user_profiles[name].setdefault("score", 0)
            self.user_profiles[name].setdefault("level", 1)
            self.user_profiles[name].setdefault("xp", 0)
            self.user_profiles[name].setdefault("achievements", [])
        self.save_profiles()
        
        self.selected_class = self.class_selection.currentText()
        self.selected_difficulty = self.difficulty_selection.currentText()
        
        num_problems = self.num_problems_input.text().strip()
        if num_problems.isdigit():
            self.total_problems = int(num_problems)
        else:
            self.total_problems = 10  # Standardwert

        self.score = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.total_time = 0
        self.current_problem_number = 0
        self.progress_bar.setMaximum(self.total_problems)
        self.progress_bar.setValue(0)
        level = self.user_profiles[self.current_user]['level']
        self.highscore_label.setText(f"Punkte: 0 | Level: {level}")
        self.stacked_widget.setCurrentIndex(1)
        logging.info("Training gestartet für Benutzer '%s' (Klasse: %s, Schwierigkeitsgrad: %s)",
                     self.current_user, self.selected_class, self.selected_difficulty)
        self.generate_problem()

    def get_user_answer(self):
        """
        Liest die Antwort aus dem Eingabefeld aus.
        Bei Division mit Rest wird das Format "Quotient, Rest" erwartet.
        """
        text = self.answer_input.text().strip()
        if isinstance(self.current_solution, tuple):
            teile = text.split(',')
            if len(teile) != 2:
                raise ValueError("Bitte gib deine Antwort im Format 'Quotient, Rest' ein.")
            try:
                quotient = int(teile[0].strip())
                rest = int(teile[1].strip())
                return (quotient, rest)
            except ValueError:
                raise ValueError("Die Antwort muss im Format 'Quotient, Rest' als Zahlen eingegeben werden.")
        else:
            return float(text)

    def validate_answer(self, user_answer):
        """
        Validiert die Antwort.
        Bei normalen Aufgaben wird eine Toleranz von 0.001 verwendet.
        """
        if isinstance(self.current_solution, tuple):
            return user_answer == self.current_solution
        else:
            return abs(user_answer - self.current_solution) < 0.001

    def check_answer(self):
        try:
            end_time = time.time()
            time_taken = end_time - self.start_time
            self.total_time += time_taken
            user_answer = self.get_user_answer()
            if self.validate_answer(user_answer):
                self.score += 10
                self.correct_answers += 1
                self.user_profiles[self.current_user]['xp'] += 10
                QMessageBox.information(self, "Richtig!", "Super, die Antwort ist korrekt!")
                logging.info("Aufgabe %d richtig gelöst", self.current_problem_number + 1)
            else:
                self.wrong_answers += 1
                QMessageBox.warning(self, "Falsch!", f"Leider falsch, die richtige Antwort war {self.current_solution}.")
                logging.info("Aufgabe %d falsch gelöst", self.current_problem_number + 1)
            self.update_level()
            self.current_problem_number += 1
            self.progress_bar.setValue(self.current_problem_number)
            level = self.user_profiles[self.current_user]['level']
            self.highscore_label.setText(f"Punkte: {self.score} | Level: {level}")
            if self.current_problem_number >= self.total_problems:
                self.end_game()
            else:
                self.generate_problem()
        except ValueError as e:
            QMessageBox.warning(self, "Fehler", str(e))
            logging.error("Fehler bei der Eingabe: %s", e)

    def update_level(self):
        """
        Aktualisiert das Level basierend auf den gesammelten XP.
        Jedes Level erfordert XP = aktuelles Level * 100.
        Zudem werden Achievements freigeschaltet.
        """
        xp = self.user_profiles[self.current_user]['xp']
        level = self.user_profiles[self.current_user]['level']
        required_xp = level * 100
        if xp >= required_xp:
            self.user_profiles[self.current_user]['level'] += 1
            new_level = self.user_profiles[self.current_user]['level']
            # Achievement hinzufügen, falls noch nicht vorhanden
            achievement_msg = f"Level {new_level} erreicht!"
            if achievement_msg not in self.user_profiles[self.current_user]['achievements']:
                self.user_profiles[self.current_user]['achievements'].append(achievement_msg)
                QMessageBox.information(self, "Level up!", f"Gratulation! Du bist jetzt Level {new_level}!\n{achievement_msg}")
                logging.info("Benutzer '%s' hat %s", self.current_user, achievement_msg)
            self.save_profiles()

    def end_game(self):
        self.timer.stop()
        avg_time = self.total_time / max(self.correct_answers + self.wrong_answers, 1)
        tip = get_tip_of_the_day()
        self.statistics_label.setText(
            f"Du hast {self.score} Punkte erzielt!\n"
            f"Korrekte Antworten: {self.correct_answers}\n"
            f"Falsche Antworten: {self.wrong_answers}\n"
            f"Durchschnittliche Zeit pro Aufgabe: {avg_time:.2f} Sekunden\n\n"
            f"Tipp des Tages: {tip}"
        )
        # Zeige alle freigeschalteten Achievements an (sofern vorhanden)
        achievements = self.user_profiles[self.current_user].get("achievements", [])
        if achievements:
            self.achievement_label.setText("Erreichte Achievements: " + ", ".join(achievements))
        else:
            self.achievement_label.setText("")
        self.save_profiles()
        self.stacked_widget.setCurrentIndex(2)
        logging.info("Training beendet für %s", self.current_user)

    def restart_game(self):
        self.score = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.total_time = 0
        self.current_problem_number = 0
        self.progress_bar.setValue(0)
        level = self.user_profiles[self.current_user]['level']
        self.highscore_label.setText(f"Punkte: 0 | Level: {level}")
        self.stacked_widget.setCurrentIndex(1)
        self.generate_problem()
        logging.info("Training neu gestartet für %s", self.current_user)

    def go_to_main_menu(self):
        self.stacked_widget.setCurrentIndex(0)
        self.timer.stop()
        logging.info("Zurück zum Hauptmenü")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MathTrainer()
    sys.exit(app.exec())
