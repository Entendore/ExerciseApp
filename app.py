#!/usr/bin/env python3
"""
FitTrack - Exercise App (Single File)
A modern PySide6 desktop application for tracking workouts and exercises.
All modules combined into one file. No external dependencies except PySide6 + matplotlib.

Usage:
    pip install PySide6 matplotlib
    python fittrack.py
"""

import sys
import os
import csv
import sqlite3
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════
# SECTION 1: LIBRARY PATH FIX (Linux)
# ═══════════════════════════════════════════════════════════
try:
    import ctypes
    _base = os.path.dirname(os.path.abspath(__file__))
    for _p in [
        os.path.join(_base, "..", ".venv", "lib", "python3.12", "site-packages", "PySide6", "Qt", "lib"),
        os.path.join(_base, "..", ".local", "lib", "python3.13", "site-packages", "PySide6", "Qt", "lib"),
    ]:
        if os.path.isdir(_p):
            os.environ["LD_LIBRARY_PATH"] = _p + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
            _egl = os.path.join(_p, "libEGL.so.1")
            if os.path.exists(_egl):
                ctypes.CDLL(_egl, mode=ctypes.RTLD_GLOBAL)
            break
except Exception:
    pass

# ═══════════════════════════════════════════════════════════
# SECTION 2: COLOR PALETTE & STYLES
# ═══════════════════════════════════════════════════════════
COLORS = {
    "bg_dark": "#1a1a2e", "bg_medium": "#16213e", "bg_light": "#0f3460",
    "bg_card": "#1e2a45", "bg_hover": "#263352", "accent": "#e94560",
    "accent_hover": "#ff6b81", "accent_green": "#00d2a0", "accent_blue": "#4fc3f7",
    "accent_yellow": "#ffd54f", "accent_orange": "#ffab40", "text_primary": "#e8e8e8",
    "text_secondary": "#a0a8b8", "text_dim": "#6c7589", "border": "#2a3a5c",
    "white": "#ffffff", "danger": "#ef5350", "success": "#66bb6a", "sidebar_bg": "#12122a",
}
CATEGORY_ACCENTS = {"Cardio": COLORS["accent"], "Strength": COLORS["accent_blue"], "Flexibility": COLORS["accent_green"]}

GLOBAL_STYLE = f"""
QScrollBar:vertical {{ border:none; background:{COLORS['bg_dark']}; width:8px; border-radius:4px; }}
QScrollBar::handle:vertical {{ background:{COLORS['border']}; min-height:30px; border-radius:4px; }}
QScrollBar::handle:vertical:hover {{ background:{COLORS['text_dim']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0px; }}
QScrollBar:horizontal {{ border:none; background:{COLORS['bg_dark']}; height:8px; border-radius:4px; }}
QScrollBar::handle:horizontal {{ background:{COLORS['border']}; min-width:30px; border-radius:4px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0px; }}
QMainWindow {{ background-color:{COLORS['bg_dark']}; }}
QWidget {{ color:{COLORS['text_primary']}; font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif; }}
QPushButton {{ background-color:{COLORS['accent']}; color:{COLORS['white']}; border:none; border-radius:8px; padding:10px 24px; font-size:14px; font-weight:600; min-height:20px; }}
QPushButton:hover {{ background-color:{COLORS['accent_hover']}; }}
QPushButton:pressed {{ background-color:{COLORS['bg_light']}; }}
QPushButton:disabled {{ background-color:{COLORS['bg_hover']}; color:{COLORS['text_dim']}; }}
QPushButton#secondary {{ background-color:{COLORS['bg_light']}; color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; }}
QPushButton#secondary:hover {{ background-color:{COLORS['bg_hover']}; border-color:{COLORS['accent']}; }}
QPushButton#ghost {{ background-color:transparent; color:{COLORS['text_secondary']}; border:none; padding:8px 16px; }}
QPushButton#ghost:hover {{ background-color:{COLORS['bg_hover']}; color:{COLORS['text_primary']}; }}
QPushButton#danger {{ background-color:{COLORS['danger']}; }}
QPushButton#danger:hover {{ background-color:{COLORS['accent']}; }}
QPushButton#success {{ background-color:{COLORS['success']}; }}
QPushButton#success:hover {{ background-color:{COLORS['accent_green']}; }}
QLineEdit, QTextEdit, QPlainTextEdit {{ background-color:{COLORS['bg_card']}; color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; border-radius:8px; padding:10px 14px; font-size:14px; }}
QLineEdit:focus, QTextEdit:focus {{ border-color:{COLORS['accent']}; }}
QComboBox {{ background-color:{COLORS['bg_card']}; color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 14px; font-size:14px; min-height:20px; }}
QComboBox:hover {{ border-color:{COLORS['accent']}; }}
QComboBox::drop-down {{ border:none; width:30px; }}
QComboBox::down-arrow {{ image:none; border-left:5px solid transparent; border-right:5px solid transparent; border-top:6px solid {COLORS['text_secondary']}; margin-right:10px; }}
QComboBox QAbstractItemView {{ background-color:{COLORS['bg_card']}; color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; selection-background-color:{COLORS['accent']}; border-radius:4px; padding:4px; }}
QSpinBox, QDoubleSpinBox {{ background-color:{COLORS['bg_card']}; color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 14px; font-size:14px; min-height:20px; }}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color:{COLORS['accent']}; }}
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ background-color:{COLORS['bg_hover']}; border:none; width:20px; }}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{ border-left:4px solid transparent; border-right:4px solid transparent; border-bottom:5px solid {COLORS['text_secondary']}; width:0; height:0; }}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{ border-left:4px solid transparent; border-right:4px solid transparent; border-top:5px solid {COLORS['text_secondary']}; width:0; height:0; }}
QLabel {{ color:{COLORS['text_primary']}; font-size:14px; background:transparent; }}
QLabel#title {{ font-size:28px; font-weight:700; color:{COLORS['white']}; }}
QLabel#subtitle {{ font-size:16px; color:{COLORS['text_secondary']}; }}
QTableWidget, QTableView {{ background-color:{COLORS['bg_card']}; alternate-background-color:{COLORS['bg_hover']}; color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; border-radius:8px; gridline-color:{COLORS['border']}; font-size:13px; selection-background-color:{COLORS['bg_light']}; selection-color:{COLORS['white']}; }}
QHeaderView::section {{ background-color:{COLORS['bg_medium']}; color:{COLORS['text_secondary']}; border:none; border-bottom:2px solid {COLORS['border']}; padding:10px 14px; font-size:13px; font-weight:600; }}
QProgressBar {{ background-color:{COLORS['bg_card']}; border:none; border-radius:10px; text-align:center; color:{COLORS['white']}; font-weight:600; font-size:13px; min-height:24px; }}
QProgressBar::chunk {{ background-color:{COLORS['accent']}; border-radius:10px; }}
QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; padding:0px; }}
QFrame#card_hover {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}
QFrame#card_hover:hover {{ border-color:{COLORS['accent']}; background-color:{COLORS['bg_hover']}; }}
QGroupBox {{ color:{COLORS['text_primary']}; border:1px solid {COLORS['border']}; border-radius:10px; margin-top:14px; padding-top:18px; font-size:14px; font-weight:600; }}
QGroupBox::title {{ subcontrol-origin:margin; left:16px; padding:0 8px; color:{COLORS['accent']}; }}
QSlider::groove:horizontal {{ height:6px; background:{COLORS['bg_card']}; border-radius:3px; }}
QSlider::handle:horizontal {{ background:{COLORS['accent']}; width:18px; height:18px; margin:-6px 0; border-radius:9px; }}
QSlider::sub-page:horizontal {{ background:{COLORS['accent']}; border-radius:3px; }}
"""
SIDEBAR_BTN_NORMAL = f"QPushButton {{ background-color:transparent; color:{COLORS['text_secondary']}; border:none; border-radius:10px; padding:12px 20px; font-size:14px; font-weight:500; text-align:left; min-height:20px; }} QPushButton:hover {{ background-color:{COLORS['bg_hover']}; color:{COLORS['text_primary']}; }}"
SIDEBAR_BTN_ACTIVE = f"QPushButton {{ background-color:{COLORS['accent']}; color:{COLORS['white']}; border:none; border-radius:10px; padding:12px 20px; font-size:14px; font-weight:600; text-align:left; min-height:20px; }}"
TIMER_DISPLAY_STYLE = f"QLabel {{ font-size:72px; font-weight:700; color:{COLORS['white']}; background:transparent; font-family:\"Consolas\",\"Courier New\",monospace; }}"

# ═══════════════════════════════════════════════════════════
# SECTION 3: DATABASE
# ═══════════════════════════════════════════════════════════
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fittrack.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, muscle_group TEXT, description TEXT, difficulty TEXT DEFAULT 'intermediate', calories_per_min REAL DEFAULT 5.0)")
        c.execute("CREATE TABLE IF NOT EXISTS workout_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, exercise_name TEXT NOT NULL, category TEXT NOT NULL, duration_min REAL NOT NULL, calories_burned REAL, sets INTEGER, reps INTEGER, weight_kg REAL, notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, goal_type TEXT NOT NULL, target_value REAL NOT NULL, current_value REAL DEFAULT 0, unit TEXT, deadline TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS user_profile (id INTEGER PRIMARY KEY DEFAULT 1, name TEXT DEFAULT '', age INTEGER DEFAULT 25, weight_kg REAL DEFAULT 70.0, height_cm REAL DEFAULT 170.0, gender TEXT DEFAULT 'male', fitness_level TEXT DEFAULT 'intermediate', weekly_goal_min REAL DEFAULT 150.0)")
        c.execute("CREATE TABLE IF NOT EXISTS routines (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, difficulty TEXT DEFAULT 'intermediate', description TEXT, is_default INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS routine_exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, routine_id INTEGER NOT NULL, exercise_name TEXT NOT NULL, sets INTEGER DEFAULT 3, reps INTEGER DEFAULT 10, rest_sec INTEGER DEFAULT 60, order_num INTEGER DEFAULT 0, FOREIGN KEY (routine_id) REFERENCES routines(id))")
        c.execute("CREATE TABLE IF NOT EXISTS personal_records (id INTEGER PRIMARY KEY AUTOINCREMENT, exercise_name TEXT NOT NULL, max_weight_kg REAL, max_reps INTEGER, max_duration_min REAL, max_sets INTEGER, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        c.execute("SELECT COUNT(*) FROM user_profile")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO user_profile (id, name, age, weight_kg, height_cm, gender, fitness_level, weekly_goal_min) VALUES (1, '', 25, 70.0, 170.0, 'male', 'intermediate', 150.0)")
        self._seed_exercises(c)
        self._seed_routines(c)
        self.conn.commit()

    def _seed_exercises(self, c):
        c.execute("SELECT COUNT(*) FROM exercises")
        if c.fetchone()[0] > 0: return
        c.executemany("INSERT INTO exercises (name, category, muscle_group, description, difficulty, calories_per_min) VALUES (?,?,?,?,?,?)", [
            ("Running","Cardio","Legs","Run at steady pace outdoors or on treadmill. Great for cardiovascular health and burning calories.","beginner",10.0),
            ("Cycling","Cardio","Legs","Ride a bicycle at moderate intensity. Low impact cardio exercise.","beginner",8.0),
            ("Jump Rope","Cardio","Full Body","Skip rope continuously. Excellent full body cardio.","intermediate",12.0),
            ("Swimming","Cardio","Full Body","Swim laps in pool. Full body workout with minimal joint stress.","beginner",9.0),
            ("HIIT","Cardio","Full Body","High Intensity Interval Training. Alternate between intense bursts and rest.","advanced",14.0),
            ("Push-Ups","Strength","Chest","Standard push-ups. Keep body straight, lower chest to floor.","beginner",7.0),
            ("Bench Press","Strength","Chest","Lie on bench, lower barbell to chest, press up. Use spotter.","intermediate",6.0),
            ("Pull-Ups","Strength","Back","Hang from bar, pull body up until chin clears bar.","intermediate",7.0),
            ("Bicep Curls","Strength","Biceps","Stand with dumbbells, curl up keeping elbows fixed.","beginner",4.0),
            ("Shoulder Press","Strength","Shoulders","Press dumbbells or barbell overhead from shoulder height.","intermediate",5.0),
            ("Tricep Dips","Strength","Triceps","Dip body down using parallel bars or bench edge.","intermediate",6.0),
            ("Squats","Strength","Quadriceps","Stand with feet shoulder-width, lower hips until thighs parallel to floor.","beginner",7.0),
            ("Deadlifts","Strength","Hamstrings","Lift barbell from floor with straight back. Keep core engaged.","intermediate",8.0),
            ("Lunges","Strength","Quadriceps","Step forward and lower back knee toward floor, alternating legs.","beginner",6.0),
            ("Calf Raises","Strength","Calves","Stand on edge of step, raise up on toes, lower slowly.","beginner",3.0),
            ("Leg Press","Strength","Quadriceps","Push weighted platform away while seated on leg press machine.","intermediate",6.0),
            ("Plank","Strength","Core","Hold body in straight line on forearms and toes. Engage core.","beginner",4.0),
            ("Crunches","Strength","Core","Lie on back, lift shoulders off floor using abs.","beginner",4.0),
            ("Russian Twists","Strength","Core","Sit with torso leaned back, twist side to side with weight.","intermediate",5.0),
            ("Leg Raises","Strength","Core","Lie flat, raise straight legs to 90 degrees, lower slowly.","intermediate",5.0),
            ("Yoga Flow","Flexibility","Full Body","Flowing sequence of yoga poses. Focus on breath and movement.","beginner",4.0),
            ("Hamstring Stretch","Flexibility","Hamstrings","Sit with legs extended, reach toward toes. Hold 30 seconds.","beginner",2.0),
            ("Hip Flexor Stretch","Flexibility","Hips","Kneel on one knee, push hips forward. Hold 30 seconds each side.","beginner",2.0),
            ("Shoulder Stretch","Flexibility","Shoulders","Pull arm across chest with opposite hand. Hold 30 seconds.","beginner",2.0),
            ("Pilates","Flexibility","Core","Low-impact exercises focusing on core strength and flexibility.","intermediate",5.0),
        ])

    def _seed_routines(self, c):
        c.execute("SELECT COUNT(*) FROM routines")
        if c.fetchone()[0] > 0: return
        c.executemany("INSERT INTO routines (name, category, difficulty, description, is_default) VALUES (?,?,?,?,?)", [
            ("Full Body Blast","Strength","intermediate","A complete full body workout targeting all major muscle groups.",1),
            ("Cardio Burn","Cardio","beginner","Cardio-focused routine to improve heart health and burn calories.",1),
            ("Core Crusher","Strength","intermediate","Intense core workout for a strong and stable midsection.",1),
            ("Upper Body Power","Strength","advanced","Advanced upper body routine for serious strength gains.",1),
            ("Flexibility Flow","Flexibility","beginner","Gentle stretching routine to improve flexibility and reduce tension.",1),
        ])
        c.executemany("INSERT INTO routine_exercises (routine_id, exercise_name, sets, reps, rest_sec, order_num) VALUES (?,?,?,?,?,?)", [
            (1,"Squats",4,12,90,0),(1,"Push-Ups",3,15,60,1),(1,"Pull-Ups",3,8,90,2),(1,"Plank",3,1,60,3),(1,"Lunges",3,12,60,4),(1,"Russian Twists",3,20,45,5),
            (2,"Running",1,1,0,0),(2,"Jump Rope",1,1,0,1),(2,"Cycling",1,1,0,2),(2,"Swimming",1,1,0,3),
            (3,"Crunches",3,20,45,0),(3,"Plank",3,1,60,1),(3,"Russian Twists",3,20,45,2),(3,"Leg Raises",3,15,45,3),(3,"Yoga Flow",1,1,0,4),
            (4,"Bench Press",4,8,120,0),(4,"Pull-Ups",4,8,90,1),(4,"Shoulder Press",4,10,90,2),(4,"Bicep Curls",3,12,60,3),(4,"Tricep Dips",3,12,60,4),
            (5,"Yoga Flow",1,1,0,0),(5,"Hamstring Stretch",1,1,0,1),(5,"Hip Flexor Stretch",1,1,0,2),(5,"Shoulder Stretch",1,1,0,3),(5,"Pilates",1,1,0,4),
        ])

    # ── Exercise methods ──
    def get_exercises(self, category=None, search=None):
        c = self.conn.cursor()
        if category and category != "All":
            c.execute("SELECT * FROM exercises WHERE category = ? ORDER BY name", (category,))
        elif search:
            c.execute("SELECT * FROM exercises WHERE name LIKE ? OR muscle_group LIKE ? OR description LIKE ? ORDER BY name", (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            c.execute("SELECT * FROM exercises ORDER BY category, name")
        return c.fetchall()

    def get_categories(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT category FROM exercises ORDER BY category")
        return [r["category"] for r in c.fetchall()]

    def add_custom_exercise(self, name, category, muscle_group, description, difficulty, calories_per_min):
        c = self.conn.cursor()
        c.execute("INSERT INTO exercises (name,category,muscle_group,description,difficulty,calories_per_min) VALUES (?,?,?,?,?,?)", (name, category, muscle_group, description, difficulty, calories_per_min))
        self.conn.commit()
        return c.lastrowid

    def get_exercise_by_name(self, name):
        c = self.conn.cursor()
        c.execute("SELECT * FROM exercises WHERE name = ?", (name,))
        return c.fetchone()

    # ── Workout log ──
    def log_workout(self, exercise_name, category, duration_min, calories=None, sets=None, reps=None, weight_kg=None, notes=None):
        c = self.conn.cursor()
        c.execute("INSERT INTO workout_logs (date,exercise_name,category,duration_min,calories_burned,sets,reps,weight_kg,notes) VALUES (?,?,?,?,?,?,?,?,?)", (datetime.now().strftime("%Y-%m-%d"), exercise_name, category, duration_min, calories, sets, reps, weight_kg, notes))
        self.conn.commit()
        lid = c.lastrowid
        if weight_kg and weight_kg > 0: self._update_pr(exercise_name, "max_weight_kg", weight_kg)
        if reps and reps > 0: self._update_pr(exercise_name, "max_reps", reps)
        if duration_min and duration_min > 0: self._update_pr(exercise_name, "max_duration_min", duration_min)
        if sets and sets > 0: self._update_pr(exercise_name, "max_sets", sets)
        return lid

    def get_workout_logs(self, date_from=None, date_to=None, category=None):
        c = self.conn.cursor()
        q = "SELECT * FROM workout_logs WHERE 1=1"; p = []
        if date_from: q += " AND date >= ?"; p.append(date_from)
        if date_to: q += " AND date <= ?"; p.append(date_to)
        if category and category != "All": q += " AND category = ?"; p.append(category)
        q += " ORDER BY date DESC, created_at DESC"
        c.execute(q, p); return c.fetchall()

    def export_logs_to_csv(self, filepath, date_from=None, date_to=None, category=None):
        logs = self.get_workout_logs(date_from=date_from, date_to=date_to, category=category)
        with open(filepath, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["Date","Exercise","Category","Duration (min)","Calories","Sets","Reps","Weight (kg)","Notes"])
            for l in logs:
                w.writerow([l["date"],l["exercise_name"],l["category"],l["duration_min"],l["calories_burned"] or "",l["sets"] or "",l["reps"] or "",l["weight_kg"] or "",l["notes"] or ""])
        return len(logs)

    def delete_workout_log(self, log_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM workout_logs WHERE id = ?", (log_id,))
        self.conn.commit()

    # ── Stats ──
    def get_stats(self, days=7):
        c = self.conn.cursor()
        df = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) as tw, SUM(duration_min) as td, SUM(COALESCE(calories_burned,0)) as tc, COUNT(DISTINCT date) as ad FROM workout_logs WHERE date >= ?", (df,))
        row = c.fetchone()
        c.execute("SELECT category, COUNT(*) as count, SUM(duration_min) as duration FROM workout_logs WHERE date >= ? GROUP BY category ORDER BY count DESC", (df,))
        cat_stats = c.fetchall()
        c.execute("SELECT date, COUNT(*) as workouts, SUM(duration_min) as duration FROM workout_logs WHERE date >= ? GROUP BY date ORDER BY date", (df,))
        daily = c.fetchall()
        return {"total_workouts": row["tw"] or 0, "total_duration": round(row["td"] or 0, 1), "total_calories": round(row["tc"] or 0, 1), "active_days": row["ad"] or 0, "category_stats": cat_stats, "daily_stats": daily}

    def get_streak(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT date FROM workout_logs ORDER BY date DESC")
        dates = [r["date"] for r in c.fetchall()]
        if not dates: return 0
        streak = 0
        cd = datetime.now().strftime("%Y-%m-%d")
        if dates[0] != cd:
            yd = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if dates[0] != yd: return 0
            cd = yd
        while cd in dates:
            streak += 1
            cd = (datetime.strptime(cd, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        return streak

    def get_longest_streak(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT date FROM workout_logs ORDER BY date ASC")
        dates = [r["date"] for r in c.fetchall()]
        if not dates: return 0
        longest = current = 1
        for i in range(1, len(dates)):
            if (datetime.strptime(dates[i], "%Y-%m-%d") - datetime.strptime(dates[i-1], "%Y-%m-%d")).days == 1:
                current += 1; longest = max(longest, current)
            else: current = 1
        return longest

    # ── Profile ──
    def get_profile(self):
        c = self.conn.cursor(); c.execute("SELECT * FROM user_profile WHERE id = 1"); return c.fetchone()

    def update_profile(self, name, age, weight_kg, height_cm, gender, fitness_level, weekly_goal_min):
        c = self.conn.cursor()
        c.execute("UPDATE user_profile SET name=?,age=?,weight_kg=?,height_cm=?,gender=?,fitness_level=?,weekly_goal_min=? WHERE id=1", (name,age,weight_kg,height_cm,gender,fitness_level,weekly_goal_min))
        self.conn.commit()

    def calculate_bmi(self, weight_kg=None, height_cm=None):
        if weight_kg is None or height_cm is None:
            p = self.get_profile(); weight_kg = p["weight_kg"]; height_cm = p["height_cm"]
        if height_cm <= 0: return 0
        return round(weight_kg / ((height_cm/100)**2), 1)

    # ── Routines ──
    def get_routines(self, category=None):
        c = self.conn.cursor()
        if category and category != "All": c.execute("SELECT * FROM routines WHERE category = ? ORDER BY name", (category,))
        else: c.execute("SELECT * FROM routines ORDER BY category, name")
        return c.fetchall()

    def get_routine_exercises(self, rid):
        c = self.conn.cursor(); c.execute("SELECT * FROM routine_exercises WHERE routine_id = ? ORDER BY order_num", (rid,)); return c.fetchall()

    def add_routine(self, name, category, difficulty, description, exercises):
        c = self.conn.cursor()
        c.execute("INSERT INTO routines (name,category,difficulty,description) VALUES (?,?,?,?)", (name,category,difficulty,description))
        rid = c.lastrowid
        for i, ex in enumerate(exercises):
            c.execute("INSERT INTO routine_exercises (routine_id,exercise_name,sets,reps,rest_sec,order_num) VALUES (?,?,?,?,?,?)", (rid, ex["name"], ex["sets"], ex["reps"], ex["rest_sec"], i))
        self.conn.commit(); return rid

    # ── Personal Records ──
    def _update_pr(self, ex_name, field, value):
        c = self.conn.cursor()
        c.execute(f"SELECT id, {field} FROM personal_records WHERE exercise_name = ?", (ex_name,))
        row = c.fetchone()
        if row:
            cur = row[field] if row[field] else 0
            if value > cur:
                c.execute(f"UPDATE personal_records SET {field} = ?, updated_at = ? WHERE exercise_name = ?", (value, datetime.now().strftime("%Y-%m-%d %H:%M"), ex_name))
        else:
            c.execute("INSERT INTO personal_records (exercise_name,max_weight_kg,max_reps,max_duration_min,max_sets) VALUES (?,?,?,?,?)", (ex_name, value if field=="max_weight_kg" else None, value if field=="max_reps" else None, value if field=="max_duration_min" else None, value if field=="max_sets" else None))
        self.conn.commit()

    def get_personal_records(self):
        c = self.conn.cursor(); c.execute("SELECT * FROM personal_records ORDER BY updated_at DESC"); return c.fetchall()

    def get_weekly_goal_progress(self):
        p = self.get_profile()
        goal = p["weekly_goal_min"] if p else 150.0
        stats = self.get_stats(days=7)
        cur = stats["total_duration"]
        return {"goal": goal, "current": cur, "percentage": round(min(cur/goal*100, 100), 1) if goal > 0 else 0}

    def close(self):
        self.conn.close()

# ═══════════════════════════════════════════════════════════
# SECTION 4: PYQT IMPORTS & UI PAGES
# ═══════════════════════════════════════════════════════════
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QComboBox, QScrollArea, QDialog, QDialogButtonBox,
    QFormLayout, QDoubleSpinBox, QSpinBox, QTextEdit, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QDateEdit, QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QColor

# ═══════════════════════════════════════════════════════════
# SECTION 5: DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════
class StatCard(QFrame):
    def __init__(self, icon, value_text, label_text, color, parent=None):
        super().__init__(parent)
        self.setObjectName("card"); self.setFixedHeight(120)
        self.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; border-left:4px solid {color}; }}")
        lo = QVBoxLayout(self); lo.setContentsMargins(20,16,20,16)
        top = QHBoxLayout(); il = QLabel(icon); il.setStyleSheet("font-size:24px;background:transparent;")
        top.addWidget(il); top.addStretch(); lo.addLayout(top)
        vl = QLabel(str(value_text)); vl.setObjectName("stat_value")
        vl.setStyleSheet(f"font-size:32px;font-weight:700;color:{color};background:transparent;")
        lo.addWidget(vl)
        ll = QLabel(label_text); ll.setStyleSheet(f"font-size:13px;color:{COLORS['text_secondary']};background:transparent;")
        lo.addWidget(ll)

    def update_value(self, nv):
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel) and item.widget().objectName() == "stat_value":
                item.widget().setText(str(nv))

class CategoryBar(QFrame):
    def __init__(self, category, count, total, color, parent=None):
        super().__init__(parent); self.setFixedHeight(48)
        self.setStyleSheet("QFrame { background:transparent; border-radius:6px; }")
        lo = QHBoxLayout(self); lo.setContentsMargins(12,6,12,6); lo.setSpacing(12)
        dot = QFrame(); dot.setFixedSize(12,12); dot.setStyleSheet(f"QFrame {{ background-color:{color}; border-radius:6px; }}")
        lo.addWidget(dot)
        nl = QLabel(category); nl.setFixedWidth(90); nl.setStyleSheet(f"background:transparent;font-weight:600;font-size:13px;color:{COLORS['text_primary']};")
        lo.addWidget(nl)
        bg = QFrame(); bg.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border-radius:4px; }}"); bg.setFixedHeight(10)
        bl = QVBoxLayout(bg); bl.setContentsMargins(0,0,0,0)
        pct = int(count/total*100) if total>0 else 0; bf = QFrame(); bf.setFixedWidth(int(pct*3)); bf.setStyleSheet(f"QFrame {{ background-color:{color}; border-radius:4px; }}"); bl.addWidget(bf)
        lo.addWidget(bg,1)
        cl = QLabel(f"{count}"); cl.setFixedWidth(30); cl.setStyleSheet(f"background:transparent;font-size:13px;font-weight:600;color:{COLORS['text_secondary']};")
        cl.setAlignment(Qt.AlignRight|Qt.AlignVCenter); lo.addWidget(cl)

class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db
        lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28); lo.setSpacing(24)
        lo.addWidget(self._make_label("Dashboard", "title"))
        lo.addWidget(self._make_label("Your weekly workout overview", "subtitle"))
        cards = QHBoxLayout(); cards.setSpacing(16)
        self.card_workouts = StatCard("\U0001f525","0","Workouts",COLORS["accent"])
        self.card_duration = StatCard("\u23f1","0 min","Total Duration",COLORS["accent_blue"])
        self.card_calories = StatCard("\u26a1","0","Calories Burned",COLORS["accent_orange"])
        self.card_active = StatCard("\U0001f4c5","0","Active Days",COLORS["accent_green"])
        self.card_streak = StatCard("\U0001f525","0","Day Streak",COLORS["accent_orange"])
        for c in [self.card_workouts,self.card_duration,self.card_calories,self.card_active,self.card_streak]: cards.addWidget(c)
        lo.addLayout(cards)
        bottom = QHBoxLayout(); bottom.setSpacing(16)
        cat_frame = self._card_frame("Workout Categories"); self.cat_container = QVBoxLayout(); self.cat_container.setSpacing(4)
        cat_frame.layout().addLayout(self.cat_container); cat_frame.layout().addStretch(); bottom.addWidget(cat_frame,1)
        rec_frame = self._card_frame("Recent Activity"); self.recent_container = QVBoxLayout(); self.recent_container.setSpacing(6)
        rec_frame.layout().addLayout(self.recent_container); rec_frame.layout().addStretch(); bottom.addWidget(rec_frame,1)
        lo.addLayout(bottom,1)
        self.refresh()

    def _make_label(self, text, oid):
        l = QLabel(text); l.setObjectName(oid); return l

    def _card_frame(self, title):
        f = QFrame(); f.setObjectName("card"); f.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}")
        vl = QVBoxLayout(f); vl.setContentsMargins(20,20,20,20); vl.setSpacing(4)
        t = QLabel(title); t.setStyleSheet(f"font-size:18px;font-weight:600;color:{COLORS['white']};background:transparent;padding-bottom:12px;")
        vl.addWidget(t); return f

    def refresh(self):
        stats = self.db.get_stats(days=7)
        self.card_workouts.update_value(stats["total_workouts"])
        self.card_duration.update_value(f"{stats['total_duration']:.0f} min")
        self.card_calories.update_value(f"{stats['total_calories']:.0f}")
        self.card_active.update_value(stats["active_days"])
        self.card_streak.update_value(self.db.get_streak())
        self._clear(self.cat_container)
        tw = stats["total_workouts"] or 1
        cc = {"Cardio":COLORS["accent"],"Strength":COLORS["accent_blue"],"Flexibility":COLORS["accent_green"]}
        for cat in stats["category_stats"]:
            self.cat_container.addWidget(CategoryBar(cat["category"],cat["count"],tw,cc.get(cat["category"],COLORS["text_dim"])))
        if not stats["category_stats"]:
            e = QLabel("No workouts this week.\nStart exercising!"); e.setStyleSheet(f"color:{COLORS['text_dim']};background:transparent;font-size:14px;padding:20px;"); e.setAlignment(Qt.AlignCenter); self.cat_container.addWidget(e)
        self._clear(self.recent_container)
        logs = self.db.get_workout_logs()[:5]
        if not logs:
            e = QLabel("No workouts recorded yet.\nHead to Exercises to get started!"); e.setStyleSheet(f"color:{COLORS['text_dim']};background:transparent;font-size:14px;padding:20px;"); e.setAlignment(Qt.AlignCenter); self.recent_container.addWidget(e)
        else:
            for log in logs:
                row = QFrame(); row.setFixedHeight(44); row.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border-radius:8px; }}")
                rl = QHBoxLayout(row); rl.setContentsMargins(14,8,14,8)
                nl = QLabel(log["exercise_name"]); nl.setFixedWidth(120); nl.setStyleSheet(f"background:transparent;font-weight:600;font-size:13px;color:{COLORS['text_primary']};")
                rl.addWidget(nl)
                cd = QFrame(); cd.setFixedSize(8,8); cd.setStyleSheet(f"QFrame {{ background-color:{cc.get(log['category'],COLORS['text_dim'])}; border-radius:4px; }}"); rl.addWidget(cd)
                dl = QLabel(f"{log['duration_min']:.0f} min"); dl.setStyleSheet(f"background:transparent;font-size:12px;color:{COLORS['text_secondary']};"); rl.addWidget(dl)
                rl.addStretch()
                dtl = QLabel(log["date"]); dtl.setStyleSheet(f"background:transparent;font-size:12px;color:{COLORS['text_dim']};"); rl.addWidget(dtl)
                self.recent_container.addWidget(row)

    def _clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

# ═══════════════════════════════════════════════════════════
# SECTION 6: EXERCISE LIBRARY PAGE
# ═══════════════════════════════════════════════════════════
class ExerciseCard(QFrame):
    start_workout = Signal(str, str, float)
    def __init__(self, ex, parent=None):
        super().__init__(parent); self.data = ex; self.setObjectName("card_hover"); self.setFixedHeight(140); self.setCursor(Qt.PointingHandCursor)
        cc = CATEGORY_ACCENTS.get(ex["category"], COLORS["accent"])
        self.setStyleSheet(f"QFrame#card_hover {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; border-top:3px solid {cc}; }} QFrame#card_hover:hover {{ border-color:{cc}; background-color:{COLORS['bg_hover']}; }}")
        lo = QVBoxLayout(self); lo.setContentsMargins(20,14,20,14); lo.setSpacing(6)
        top = QHBoxLayout(); nl = QLabel(ex["name"]); nl.setStyleSheet(f"font-size:17px;font-weight:700;color:{COLORS['white']};background:transparent;"); top.addWidget(nl); top.addStretch()
        diff = ex["difficulty"] if "difficulty" in ex.keys() else "intermediate"
        dc = {"beginner":COLORS["accent_green"],"intermediate":COLORS["accent_yellow"],"advanced":COLORS["danger"]}.get(diff,COLORS["text_dim"])
        dl = QLabel(diff.capitalize()); dl.setFixedHeight(24); dl.setAlignment(Qt.AlignCenter); dl.setStyleSheet(f"QLabel {{ background-color:{dc}22; color:{dc}; border:1px solid {dc}44; border-radius:12px; font-size:11px; font-weight:600; padding:2px 12px; }}")
        top.addWidget(dl); lo.addLayout(top)
        desc = ex["description"] if ex["description"] else ""
        if len(desc)>80: desc = desc[:77]+"..."
        desc_l = QLabel(desc); desc_l.setWordWrap(True); desc_l.setStyleSheet(f"font-size:12px;color:{COLORS['text_secondary']};background:transparent;"); lo.addWidget(desc_l)
        bot = QHBoxLayout(); ml = QLabel(f"\U0001f4aa {ex['muscle_group']}"); ml.setStyleSheet(f"font-size:12px;color:{COLORS['text_dim']};background:transparent;"); bot.addWidget(ml)
        cl = QLabel(f"\U0001f525 {ex['calories_per_min']:.0f} cal/min"); cl.setStyleSheet(f"font-size:12px;color:{COLORS['accent_orange']};background:transparent;"); bot.addWidget(cl); bot.addStretch()
        sb = QPushButton("Start"); sb.setFixedSize(70,30); sb.setCursor(Qt.PointingHandCursor)
        sb.setStyleSheet(f"QPushButton {{ background-color:{cc}; color:{COLORS['white']}; border:none; border-radius:6px; font-size:12px; font-weight:600; }} QPushButton:hover {{ background-color:{COLORS['white']}; color:{cc}; }}")
        sb.clicked.connect(lambda: self.start_workout.emit(ex["name"],ex["category"],ex["calories_per_min"]))
        bot.addWidget(sb); lo.addLayout(bot)

class LogWorkoutDialog(QDialog):
    def __init__(self, en, cpm, db, parent=None):
        super().__init__(parent); self.db = db; self.exercise_name = en; self.calories_per_min = cpm
        self.setWindowTitle(f"Log: {en}"); self.setMinimumWidth(380)
        self.setStyleSheet(f"QDialog {{ background-color:{COLORS['bg_dark']}; color:{COLORS['text_primary']}; }}")
        lo = QVBoxLayout(self); lo.setSpacing(16)
        t = QLabel(f"\U0001f4aa Log Workout: {en}"); t.setStyleSheet(f"font-size:18px;font-weight:700;color:{COLORS['white']};"); lo.addWidget(t)
        form = QFormLayout(); form.setSpacing(14)
        self.dur = QDoubleSpinBox(); self.dur.setRange(0.5,300); self.dur.setValue(10); self.dur.setSuffix(" min"); self.dur.valueChanged.connect(self._uc); form.addRow("Duration:",self.dur)
        self.cal_l = QLabel(f"{cpm*10:.0f} cal"); self.cal_l.setStyleSheet(f"color:{COLORS['accent_orange']};font-weight:600;"); form.addRow("Calories:",self.cal_l)
        self.sets = QSpinBox(); self.sets.setRange(0,100); self.sets.setValue(3); form.addRow("Sets:",self.sets)
        self.reps = QSpinBox(); self.reps.setRange(0,1000); self.reps.setValue(10); form.addRow("Reps:",self.reps)
        self.wt = QDoubleSpinBox(); self.wt.setRange(0,500); self.wt.setValue(0); self.wt.setSuffix(" kg"); form.addRow("Weight:",self.wt)
        self.notes = QTextEdit(); self.notes.setMaximumHeight(60); self.notes.setPlaceholderText("Optional notes..."); form.addRow("Notes:",self.notes)
        lo.addLayout(form)
        bb = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.button(QDialogButtonBox.Ok).setText("Save Workout"); bb.button(QDialogButtonBox.Cancel).setText("Cancel"); bb.accepted.connect(self._save); bb.rejected.connect(self.reject); lo.addWidget(bb)
    def _uc(self): self.cal_l.setText(f"{self.dur.value()*self.calories_per_min:.0f} cal")
    def _save(self):
        ex = self.db.get_exercise_by_name(self.exercise_name); cat = ex["category"] if ex else "Other"
        self.db.log_workout(self.exercise_name,cat,self.dur.value(),self.dur.value()*self.calories_per_min,self.sets.value() if self.sets.value()>0 else None,self.reps.value() if self.reps.value()>0 else None,self.wt.value() if self.wt.value()>0 else None,self.notes.toPlainText() or None); self.accept()

class _AddExerciseDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db = db; self.setWindowTitle("Add Custom Exercise"); self.setMinimumWidth(400)
        self.setStyleSheet(f"QDialog {{ background-color:{COLORS['bg_dark']}; color:{COLORS['text_primary']}; }}")
        lo = QVBoxLayout(self); lo.setSpacing(16)
        lo.addWidget(self._hl("Add Custom Exercise"))
        form = QFormLayout(); form.setSpacing(14)
        self.ni = QLineEdit(); self.ni.setPlaceholderText("e.g., Kettlebell Swings"); form.addRow("Name:",self.ni)
        self.ci = QComboBox(); self.ci.addItems(["Strength","Cardio","Flexibility"]); form.addRow("Category:",self.ci)
        self.mi = QLineEdit(); self.mi.setPlaceholderText("e.g., Full Body"); form.addRow("Muscle Group:",self.mi)
        self.di = QComboBox(); self.di.addItems(["beginner","intermediate","advanced"]); form.addRow("Difficulty:",self.di)
        self.cs = QDoubleSpinBox(); self.cs.setRange(1,30); self.cs.setValue(6.0); self.cs.setSuffix(" cal/min"); self.cs.setDecimals(1); form.addRow("Calories/min:",self.cs)
        self.de = QTextEdit(); self.de.setMaximumHeight(60); self.de.setPlaceholderText("Describe the exercise..."); form.addRow("Description:",self.de)
        lo.addLayout(form)
        bb = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.button(QDialogButtonBox.Ok).setText("Add Exercise"); bb.accepted.connect(self._save); bb.rejected.connect(self.reject); lo.addWidget(bb)
    def _hl(self, t): l = QLabel(t); l.setStyleSheet(f"font-size:18px;font-weight:700;color:{COLORS['white']};"); return l
    def _save(self):
        n = self.ni.text().strip()
        if n: self.db.add_custom_exercise(n,self.ci.currentText(),self.mi.text().strip() or "Other",self.de.toPlainText().strip(),self.di.currentText(),self.cs.value()); self.accept()

class ExerciseLibraryPage(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db; self.current_category = "All"
        lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28); lo.setSpacing(20)
        h = QHBoxLayout(); t = QLabel("Exercise Library"); t.setObjectName("title"); h.addWidget(t); h.addStretch(); lo.addLayout(h)
        lo.addWidget(self._mk("Browse exercises and start your workout","subtitle"))
        fr = QHBoxLayout(); fr.setSpacing(12)
        self.sb = QLineEdit(); self.sb.setPlaceholderText("\U0001f50d  Search exercises..."); self.sb.setFixedWidth(350); self.sb.setFixedHeight(42); self.sb.textChanged.connect(self._af); fr.addWidget(self.sb)
        self.cc = QComboBox(); self.cc.setFixedWidth(180); self.cc.setFixedHeight(42); self.cc.addItem("All Categories")
        for cat in self.db.get_categories(): self.cc.addItem(cat)
        self.cc.currentTextChanged.connect(self._occ); fr.addWidget(self.cc)
        self.cl = QLabel("0 exercises"); self.cl.setStyleSheet(f"color:{COLORS['text_dim']};font-size:13px;"); fr.addWidget(self.cl); fr.addStretch(); lo.addLayout(fr)
        pr = QHBoxLayout(); pr.setSpacing(8); self.pills = {}
        for cat in ["All","Cardio","Strength","Flexibility"]:
            b = QPushButton(cat); b.setFixedHeight(34); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _, c=cat: self._sp(c)); self._sp2(b, cat=="All"); pr.addWidget(b); self.pills[cat] = b
        pr.addStretch(); lo.addLayout(pr)
        aeb = QPushButton("+ Add Custom Exercise"); aeb.setFixedHeight(38); aeb.setObjectName("success"); aeb.setCursor(Qt.PointingHandCursor); aeb.clicked.connect(self._ace); lo.addWidget(aeb)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); sc.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.ec = QWidget(); self.el = QVBoxLayout(self.ec); self.el.setContentsMargins(0,0,0,0); self.el.setSpacing(10)
        sc.setWidget(self.ec); lo.addWidget(sc,1); self._le()

    def _mk(self,t,oid): l = QLabel(t); l.setObjectName(oid); return l
    def _sp2(self, btn, active):
        btn.setStyleSheet(f"QPushButton {{ background-color:{COLORS['accent'] if active else COLORS['bg_card']}; color:{COLORS['white'] if active else COLORS['text_secondary']}; border:{'none' if active else '1px solid '+COLORS['border']}; border-radius:17px; padding:6px 20px; font-size:13px; font-weight:{'600' if active else '500'}; }}")
    def _sp(self, cat):
        self.current_category = cat
        idx = self.cc.findText(cat if cat!="All" else "All Categories")
        if idx>=0: self.cc.setCurrentIndex(idx)
        for c,b in self.pills.items(): self._sp2(b, c==cat)
        self._le()
    def _occ(self, text): cat = text.replace(" Categories","") if text!="All Categories" else "All"; self.current_category = cat; for c,b in self.pills.items(): self._sp2(b, c==cat); self._le()
    def _af(self): self._le()
    def _le(self):
        while self.el.count():
            item = self.el.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        s = self.sb.text().strip()
        exs = self.db.get_exercises(category=self.current_category, search=s if s else None)
        self.cl.setText(f"{len(exs)} exercise{'s' if len(exs)!=1 else ''}")
        if not exs:
            e = QLabel("No exercises found."); e.setStyleSheet(f"color:{COLORS['text_dim']};font-size:15px;padding:40px;background:transparent;"); e.setAlignment(Qt.AlignCenter); self.el.addWidget(e); return
        for ex in exs:
            card = ExerciseCard(ex); card.start_workout.connect(self._old); self.el.addWidget(card)
        self.el.addStretch()
    def _old(self, n, c, cpm): LogWorkoutDialog(n, cpm, self.db, self).exec()
    def _ace(self):
        d = _AddExerciseDialog(self.db, self)
        if d.exec(): self._le()

# ═══════════════════════════════════════════════════════════
# SECTION 7: WORKOUT TIMER PAGE
# ═══════════════════════════════════════════════════════════
class WorkoutTimerPage(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db
        self.timer = QTimer(self); self.timer.setInterval(1000); self.timer.timeout.connect(self._tick)
        self.elapsed = 0; self.running = False; self.is_countdown = False; self.cd_total = 0
        self._build()

    def _build(self):
        lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28); lo.setSpacing(24)
        lo.addWidget(self._ml("Workout Timer","title")); lo.addWidget(self._ml("Track your workout duration","subtitle"))
        mr = QHBoxLayout(); self.mode_btns = {}
        for label, mode in [("Stopwatch","stopwatch"),("Countdown","countdown")]:
            b = QPushButton(label); b.setFixedHeight(38); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _, m=mode: self._sm(m)); self.mode_btns[mode] = b; mr.addWidget(b)
        mr.addStretch()
        self.cd_settings = QFrame(); cdl = QHBoxLayout(self.cd_settings); cdl.setContentsMargins(0,0,0,0); cdl.setSpacing(12)
        cdl.addWidget(self._sl("Set time:"))
        self.cd_min = QSpinBox(); self.cd_min.setRange(0,180); self.cd_min.setValue(5); self.cd_min.setSuffix(" min"); self.cd_min.setFixedWidth(120); cdl.addWidget(self.cd_min)
        self.cd_sec = QSpinBox(); self.cd_sec.setRange(0,59); self.cd_sec.setValue(0); self.cd_sec.setSuffix(" sec"); self.cd_sec.setFixedWidth(120); cdl.addWidget(self.cd_sec); cdl.addStretch(); self.cd_settings.hide()
        lo.addLayout(mr); lo.addWidget(self.cd_settings)
        er = QHBoxLayout(); er.setSpacing(12); er.addWidget(self._sl("Exercise:"))
        self.ex_combo = QComboBox(); self.ex_combo.setFixedWidth(250); self.ex_combo.addItem("-- Select Exercise --")
        for ex in self.db.get_exercises(): self.ex_combo.addItem(ex["name"])
        er.addWidget(self.ex_combo); er.addStretch(); lo.addLayout(er)
        self.tf = QFrame(); self.tf.setFixedHeight(180); self.tf.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border:2px solid {COLORS['border']}; border-radius:20px; }}")
        tl = QVBoxLayout(self.tf); tl.setAlignment(Qt.AlignCenter)
        self.td = QLabel("00:00"); self.td.setAlignment(Qt.AlignCenter); self.td.setStyleSheet(TIMER_DISPLAY_STYLE); tl.addWidget(self.td)
        self.ml = QLabel("STOPWATCH"); self.ml.setAlignment(Qt.AlignCenter); self.ml.setStyleSheet(f"font-size:13px;font-weight:600;color:{COLORS['text_dim']};background:transparent;letter-spacing:2px;"); tl.addWidget(self.ml)
        lo.addWidget(self.tf, alignment=Qt.AlignCenter)
        ctrls = QHBoxLayout(); ctrls.setSpacing(16)
        self.start_btn = QPushButton("\u25b6  Start"); self.start_btn.setFixedSize(140,50); self.start_btn.setCursor(Qt.PointingHandCursor); self.start_btn.clicked.connect(self._start); ctrls.addWidget(self.start_btn)
        self.pause_btn = QPushButton("\u23f8  Pause"); self.pause_btn.setFixedSize(140,50); self.pause_btn.setCursor(Qt.PointingHandCursor); self.pause_btn.setObjectName("secondary"); self.pause_btn.setEnabled(False); self.pause_btn.clicked.connect(self._pause); ctrls.addWidget(self.pause_btn)
        self.reset_btn = QPushButton("\u21ba  Reset"); self.reset_btn.setFixedSize(140,50); self.reset_btn.setCursor(Qt.PointingHandCursor); self.reset_btn.setObjectName("secondary"); self.reset_btn.clicked.connect(self._reset); ctrls.addWidget(self.reset_btn)
        ctrls.addStretch()
        self.log_btn = QPushButton("\U0001f4dd  Log Workout"); self.log_btn.setFixedSize(160,50); self.log_btn.setCursor(Qt.PointingHandCursor); self.log_btn.setObjectName("success"); self.log_btn.setEnabled(False); self.log_btn.clicked.connect(self._old); ctrls.addWidget(self.log_btn)
        lo.addLayout(ctrls)
        self.prog = QFrame(); self.prog.setFixedHeight(8); self.prog.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_card']}; border-radius:4px; }}")
        self.pbf = QFrame(self.prog); self.pbf.setGeometry(0,0,0,8); self.pbf.setStyleSheet(f"QFrame {{ background-color:{COLORS['accent']}; border-radius:4px; }}")
        lo.addWidget(self.prog); self._sm("stopwatch")

    def _ml(self, t, oid): l = QLabel(t); l.setObjectName(oid); return l
    def _sl(self, t): l = QLabel(t); l.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;background:transparent;"); return l

    def _sm(self, mode):
        self.is_countdown = mode == "countdown"
        if not self.running: self._reset()
        for m, b in self.mode_btns.items():
            b.setStyleSheet(f"QPushButton {{ background-color:{COLORS['accent'] if m==mode else COLORS['bg_card']}; color:{COLORS['white'] if m==mode else COLORS['text_secondary']}; border:{'none' if m==mode else '1px solid '+COLORS['border']}; border-radius:8px; padding:8px 24px; font-size:13px; font-weight:{'600' if m==mode else '500'}; }}")
        self.cd_settings.setVisible(self.is_countdown)
        self.ml.setText("COUNTDOWN" if self.is_countdown else "STOPWATCH")

    def _start(self):
        if self.is_countdown:
            total = self.cd_min.value()*60+self.cd_sec.value()
            if total<=0 and self.elapsed==0: return
            if self.elapsed==0: self.cd_total = total; self.elapsed = total
        self.running = True; self.timer.start()
        self.start_btn.setEnabled(False); self.pause_btn.setEnabled(True); self.log_btn.setEnabled(False); self.ex_combo.setEnabled(False); self.cd_settings.setEnabled(False)
        self.tf.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border:2px solid {COLORS['accent']}; border-radius:20px; }}")

    def _pause(self):
        self.running = False; self.timer.stop()
        self.start_btn.setEnabled(True); self.pause_btn.setEnabled(False); self.log_btn.setEnabled(True); self.ex_combo.setEnabled(True); self.cd_settings.setEnabled(True)
        self.tf.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border:2px solid {COLORS['accent_yellow']}; border-radius:20px; }}")

    def _reset(self):
        self.running = False; self.timer.stop(); self.elapsed = 0; self.cd_total = 0; self.td.setText("00:00")
        self.start_btn.setEnabled(True); self.pause_btn.setEnabled(False); self.log_btn.setEnabled(False); self.ex_combo.setEnabled(True); self.cd_settings.setEnabled(True)
        self.pbf.setGeometry(0,0,0,8)
        self.tf.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border:2px solid {COLORS['border']}; border-radius:20px; }}")

    def _tick(self):
        if self.is_countdown:
            self.elapsed -= 1
            if self.elapsed<=0: self.elapsed=0; self._pause(); self.tf.setStyleSheet(f"QFrame {{ background-color:{COLORS['accent']}22; border:2px solid {COLORS['accent_green']}; border-radius:20px; }}"); self.td.setText("DONE!"); self.log_btn.setEnabled(True); return
            pct = self.elapsed/self.cd_total if self.cd_total>0 else 0; bw = int(pct*self.prog.width()) if self.prog.width()>0 else 0; self.pbf.setGeometry(0,0,max(bw,4),8)
        else: self.elapsed += 1; self.log_btn.setEnabled(True)
        m,s = divmod(self.elapsed,60); self.td.setText(f"{m:02d}:{s:02d}")

    def _old(self):
        en = self.ex_combo.currentText()
        if en == "-- Select Exercise --": en = "Custom Workout"; cal = 5.0
        else: ex = self.db.get_exercise_by_name(en); cal = ex["calories_per_min"] if ex else 5.0
        dur = self.elapsed/60.0
        if dur < 0.1: return
        _TimerLogDialog(en, cal, dur, self.db, self).exec()

class _TimerLogDialog(QDialog):
    def __init__(self, en, cpm, dm, db, parent=None):
        super().__init__(parent); self.db = db; self._en = en; self._cpm = cpm; self._dm = dm
        self.setWindowTitle("Log Workout"); self.setMinimumWidth(350); self.setStyleSheet(f"QDialog {{ background-color:{COLORS['bg_dark']}; color:{COLORS['text_primary']}; }}")
        lo = QVBoxLayout(self); lo.setSpacing(16)
        t = QLabel(f"\U0001f4aa {en}"); t.setStyleSheet(f"font-size:18px;font-weight:700;color:{COLORS['white']};"); lo.addWidget(t)
        lo.addWidget(self._il(f"Duration: {dm:.1f} min  \u2022 Est. Calories: {cpm*dm:.0f}"))
        form = QFormLayout(); form.setSpacing(12)
        self.ss = QSpinBox(); self.ss.setRange(0,100); self.ss.setValue(0); self.ss.setSpecialValueText("N/A"); form.addRow("Sets:",self.ss)
        self.rs = QSpinBox(); self.rs.setRange(0,1000); self.rs.setValue(0); self.rs.setSpecialValueText("N/A"); form.addRow("Reps:",self.rs)
        self.ws = QDoubleSpinBox(); self.ws.setRange(0,500); self.ws.setValue(0); self.ws.setSuffix(" kg"); self.ws.setSpecialValueText("N/A"); form.addRow("Weight:",self.ws)
        self.nt = QTextEdit(); self.nt.setMaximumHeight(60); self.nt.setPlaceholderText("Optional notes..."); form.addRow("Notes:",self.nt)
        lo.addLayout(form)
        bb = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.button(QDialogButtonBox.Ok).setText("Save"); bb.accepted.connect(self._save); bb.rejected.connect(self.reject); lo.addWidget(bb)
    def _il(self, t): l = QLabel(t); l.setStyleSheet(f"color:{COLORS['accent_orange']};font-size:14px;"); return l
    def _save(self):
        ex = self.db.get_exercise_by_name(self._en); cat = ex["category"] if ex else "Other"
        self.db.log_workout(self._en, cat, self._dm, self._cpm*self._dm, self.ss.value() if self.ss.value()>0 else None, self.rs.value() if self.rs.value()>0 else None, self.ws.value() if self.ws.value()>0 else None, self.nt.toPlainText() or None); self.accept()

# ═══════════════════════════════════════════════════════════
# SECTION 8: PROGRESS CHARTS PAGE
# ═══════════════════════════════════════════════════════════
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib
    matplotlib.use("QtAgg")
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

if HAS_MATPLOTLIB:
    def _mp_style():
        matplotlib.rcParams.update({"figure.facecolor":COLORS["bg_card"],"axes.facecolor":COLORS["bg_card"],"axes.edgecolor":COLORS["border"],"axes.labelcolor":COLORS["text_secondary"],"xtick.color":COLORS["text_dim"],"ytick.color":COLORS["text_dim"],"text.color":COLORS["text_primary"],"grid.color":COLORS["border"],"grid.alpha":0.4,"font.size":11})

    class ChartCanvas(FigureCanvas):
        def __init__(self):
            _mp_style(); self.fig = Figure(figsize=(5,3),dpi=100); self.fig.patch.set_facecolor(COLORS["bg_card"]); super().__init__(self.fig); self.setMinimumHeight(280)

    class ProgressChartsPage(QWidget):
        def __init__(self, db):
            super().__init__(); self.db = db; self.period_days = 30
            lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28); lo.setSpacing(20)
            h = QHBoxLayout(); t = QLabel("Progress Charts"); t.setObjectName("title"); h.addWidget(t); h.addStretch()
            h.addWidget(self._sl("Period:"))
            self.pc = QComboBox(); self.pc.setFixedWidth(160); self.pc.setFixedHeight(38)
            for label, days in [("Last 7 Days",7),("Last 14 Days",14),("Last 30 Days",30),("Last 90 Days",90)]: self.pc.addItem(label, days)
            self.pc.currentIndexChanged.connect(self._opc); h.addWidget(self.pc); lo.addLayout(h)
            lo.addWidget(self._mk("Visualize your workout trends","subtitle"))
            gf = QFrame(); gf.setFixedHeight(60); gf.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; border-left:4px solid {COLORS['accent_green']}; }}")
            gl = QHBoxLayout(gf); gl.setContentsMargins(20,12,20,12)
            gl.addWidget(self._bl("Weekly Goal",f"font-weight:600;font-size:14px;color:{COLORS['white']};background:transparent;"))
            self.gp_l = self._bl("0 / 150 min",f"font-weight:600;font-size:14px;color:{COLORS['accent_green']};background:transparent;"); gl.addWidget(self.gp_l); gl.addStretch()
            self.gp_p = self._bl("0%",f"font-size:22px;font-weight:700;color:{COLORS['accent_green']};background:transparent;"); gl.addWidget(self.gp_p); lo.addWidget(gf)
            tr = QHBoxLayout(); tr.setSpacing(16)
            df = self._cf("Duration Trend"); self.dc = ChartCanvas(); df.layout().addWidget(self.dc); tr.addWidget(df,3)
            pf = self._cf("Category Split"); self.pic = ChartCanvas(); pf.layout().addWidget(self.pic); tr.addWidget(pf,2)
            lo.addLayout(tr,1); br = QHBoxLayout(); br.setSpacing(16)
            cf = self._cf("Calories Burned"); self.cac = ChartCanvas(); cf.layout().addWidget(self.cac); br.addWidget(cf,1)
            wf = self._cf("Workout Frequency"); self.wfc = ChartCanvas(); wf.layout().addWidget(self.wfc); br.addWidget(wf,1)
            lo.addLayout(br,1); self.refresh()

        def _sl(self, t): l = QLabel(t); l.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;background:transparent;"); return l
        def _bl(self, t, ss): l = QLabel(t); l.setStyleSheet(ss); return l
        def _mk(self, t, oid): l = QLabel(t); l.setObjectName(oid); return l
        def _cf(self, t):
            f = QFrame(); f.setObjectName("card"); f.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}")
            vl = QVBoxLayout(f); vl.setContentsMargins(16,16,16,8); vl.addWidget(self._bl(t,f"font-size:16px;font-weight:600;color:{COLORS['white']};background:transparent;")); return f
        def _opc(self, i): self.period_days = self.pc.itemData(i) or 7; self.refresh()
        def refresh(self):
            stats = self.db.get_stats(days=self.period_days)
            goal = self.db.get_weekly_goal_progress()
            self.gp_l.setText(f"{goal['current']:.0f} / {goal['goal']:.0f} min")
            self.gp_p.setText(f"{goal['percentage']:.0f}%")
            pc = COLORS["accent_green"] if goal["percentage"]>=100 else COLORS["accent_yellow"]
            self.gp_p.setStyleSheet(f"font-size:22px;font-weight:700;color:{pc};background:transparent;")
            daily = stats["daily_stats"]
            self.dc.fig.clear(); ax = self.dc.fig.add_subplot(111)
            if daily:
                ds = [d["date"][5:] for d in daily]; dv = [d["duration"] for d in daily]
                ax.fill_between(range(len(ds)),dv,alpha=0.3,color=COLORS["accent_blue"]); ax.plot(range(len(ds)),dv,color=COLORS["accent_blue"],linewidth=2.5,marker="o",markersize=5)
                ax.set_xticks(range(len(ds))); ax.set_xticklabels(ds,rotation=45,fontsize=9); ax.set_ylabel("Minutes"); ax.set_title("Daily Duration",fontsize=12,fontweight="bold",pad=8); ax.grid(True,alpha=0.3)
            else: ax.text(0.5,0.5,"No data yet",ha="center",va="center",fontsize=16,color=COLORS["text_dim"],transform=ax.transAxes)
            self.dc.fig.tight_layout(); self.dc.draw()
            self.pic.fig.clear(); ax2 = self.pic.fig.add_subplot(111)
            cs = stats["category_stats"]
            if cs:
                cm = {"Cardio":COLORS["accent"],"Strength":COLORS["accent_blue"],"Flexibility":COLORS["accent_green"]}
                ax2.pie([c["count"] for c in cs],[c["category"] for c in cs],colors=[cm.get(c["category"],COLORS["text_dim"]) for c in cs],autopct="%1.0f%%",startangle=90,textprops={"fontsize":10,"color":COLORS["text_primary"]})
            else: ax2.text(0.5,0.5,"No data yet",ha="center",va="center",fontsize=16,color=COLORS["text_dim"],transform=ax2.transAxes)
            ax2.set_title("Categories",fontsize=12,fontweight="bold",pad=8); self.pic.fig.tight_layout(); self.pic.draw()
            self.cac.fig.clear(); ax3 = self.cac.fig.add_subplot(111)
            if daily:
                from datetime import datetime as _dt, timedelta as _td
                cur = self.db.conn.cursor(); df = (_dt.now()-_td(days=self.period_days)).strftime("%Y-%m-%d")
                cur.execute("SELECT date, SUM(COALESCE(calories_burned,0)) as cal FROM workout_logs WHERE date >= ? GROUP BY date ORDER BY date",(df,))
                cd = cur.fetchall(); cds = [d["date"][5:] for d in cd]; cvs = [d["cal"] for d in cd]
                ax3.bar(range(len(cds)),cvs,color=COLORS["accent_orange"],alpha=0.8,border_radius=4); ax3.set_xticks(range(len(cds))); ax3.set_xticklabels(cds,rotation=45,fontsize=9); ax3.set_ylabel("Calories"); ax3.set_title("Daily Calories",fontsize=12,fontweight="bold",pad=8); ax3.grid(True,axis="y",alpha=0.3)
            else: ax3.text(0.5,0.5,"No data yet",ha="center",va="center",fontsize=16,color=COLORS["text_dim"],transform=ax3.transAxes)
            self.cac.fig.tight_layout(); self.cac.draw()
            self.wfc.fig.clear(); ax4 = self.wfc.fig.add_subplot(111)
            if daily:
                fds = [d["date"][5:] for d in daily]; fvs = [d["workouts"] for d in daily]
                ax4.bar(range(len(fds)),fvs,color=COLORS["accent_green"],alpha=0.8,border_radius=4); ax4.set_xticks(range(len(fds))); ax4.set_xticklabels(fds,rotation=45,fontsize=9); ax4.set_ylabel("Workouts"); ax4.set_title("Frequency",fontsize=12,fontweight="bold",pad=8); ax4.grid(True,axis="y",alpha=0.3)
            else: ax4.text(0.5,0.5,"No data yet",ha="center",va="center",fontsize=16,color=COLORS["text_dim"],transform=ax4.transAxes)
            self.wfc.fig.tight_layout(); self.wfc.draw()
else:
    class ProgressChartsPage(QWidget):
        def __init__(self, db):
            super().__init__(); self.db = db
            lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28)
            lo.addWidget(QLabel("Progress Charts")); lo.addStretch()
            lo.addWidget(QLabel("matplotlib is required for charts.\npip install matplotlib"))
            lo.addWidget(QLabel("Charts will appear after installation."))

# ═══════════════════════════════════════════════════════════
# SECTION 9: PROFILE PAGE
# ═══════════════════════════════════════════════════════════
class ProfilePage(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db
        lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28); lo.setSpacing(24)
        lo.addWidget(self._ml("Profile & Settings","title")); lo.addWidget(self._ml("Manage your profile and track your fitness metrics","subtitle"))
        content = QHBoxLayout(); content.setSpacing(20)
        ff = QFrame(); ff.setObjectName("card"); ff.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}")
        fl = QVBoxLayout(ff); fl.setContentsMargins(24,24,24,24); fl.setSpacing(18)
        fl.addWidget(self._sl("Personal Information",f"font-size:18px;font-weight:600;color:{COLORS['white']};background:transparent;padding-bottom:8px;"))
        self.ni = QLineEdit(); self.ni.setPlaceholderText("Enter your name")
        fl.addWidget(self._row("Name:",self.ni)); self.age_s = QSpinBox(); self.age_s.setRange(10,120); self.age_s.setValue(25); fl.addWidget(self._row("Age:",self.age_s))
        self.gen_c = QComboBox(); self.gen_c.addItems(["Male","Female","Other"]); fl.addWidget(self._row("Gender:",self.gen_c))
        self.wt_s = QDoubleSpinBox(); self.wt_s.setRange(20,300); self.wt_s.setValue(70.0); self.wt_s.setSuffix(" kg"); self.wt_s.valueChanged.connect(self._ub); fl.addWidget(self._row("Weight:",self.wt_s))
        self.ht_s = QDoubleSpinBox(); self.ht_s.setRange(100,250); self.ht_s.setValue(170.0); self.ht_s.setSuffix(" cm"); self.ht_s.valueChanged.connect(self._ub); fl.addWidget(self._row("Height:",self.ht_s))
        self.fit_c = QComboBox(); self.fit_c.addItems(["Beginner","Intermediate","Advanced"]); fl.addWidget(self._row("Fitness Level:",self.fit_c))
        self.goal_s = QDoubleSpinBox(); self.goal_s.setRange(30,600); self.goal_s.setValue(150); self.goal_s.setSuffix(" min"); fl.addWidget(self._row("Weekly Goal:",self.goal_s))
        fl.addSpacing(8); sb = QPushButton("Save Profile"); sb.setFixedHeight(44); sb.setCursor(Qt.PointingHandCursor); sb.clicked.connect(self._save); fl.addWidget(sb)
        content.addWidget(ff,1)
        rc = QVBoxLayout(); rc.setSpacing(16)
        # BMI
        bf = QFrame(); bf.setObjectName("card"); bf.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}")
        bl = QVBoxLayout(bf); bl.setContentsMargins(24,20,24,20)
        bl.addWidget(self._sl("BMI Calculator",f"font-size:18px;font-weight:600;color:{COLORS['white']};background:transparent;"))
        self.bmi_v = QLabel("23.5"); self.bmi_v.setAlignment(Qt.AlignCenter); self.bmi_v.setStyleSheet(f"font-size:56px;font-weight:800;color:{COLORS['accent_green']};background:transparent;"); bl.addWidget(self.bmi_v)
        self.bmi_c = QLabel("Normal Weight"); self.bmi_c.setAlignment(Qt.AlignCenter); bl.addWidget(self.bmi_c)
        sc = QFrame(); sc.setFixedHeight(20); sc.setStyleSheet(f"QFrame {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {COLORS['accent_blue']},stop:0.4 {COLORS['accent_green']},stop:0.65 {COLORS['accent_yellow']},stop:1 {COLORS['danger']}); border-radius:10px; }}"); bl.addWidget(sc)
        bll = QHBoxLayout()
        for t in ["Underweight","Normal","Overweight","Obese"]: bll.addWidget(self._sl(t,f"font-size:10px;color:{COLORS['text_dim']};background:transparent;"))
        bl.addLayout(bll); rc.addWidget(bf)
        # Streaks
        sf = QFrame(); sf.setObjectName("card"); sf.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}")
        sl = QVBoxLayout(sf); sl.setContentsMargins(24,20,24,20)
        sl.addWidget(self._sl("Streak Tracker",f"font-size:18px;font-weight:600;color:{COLORS['white']};background:transparent;"))
        sv = QHBoxLayout(); sv.setSpacing(20)
        cb = QVBoxLayout(); self.cur_sv = QLabel("0"); self.cur_sv.setAlignment(Qt.AlignCenter); self.cur_sv.setStyleSheet(f"font-size:40px;font-weight:800;color:{COLORS['accent_orange']};background:transparent;"); cb.addWidget(self.cur_sv); cb.addWidget(self._sl("Current Streak",f"font-size:12px;color:{COLORS['text_dim']};background:transparent;")); cb.setAlignment(Qt.AlignCenter); sv.addLayout(cb)
        sep = QFrame(); sep.setFixedWidth(1); sep.setStyleSheet(f"background-color:{COLORS['border']};"); sv.addWidget(sep)
        bb2 = QVBoxLayout(); self.best_sv = QLabel("0"); self.best_sv.setAlignment(Qt.AlignCenter); self.best_sv.setStyleSheet(f"font-size:40px;font-weight:800;color:{COLORS['accent']};background:transparent;"); bb2.addWidget(self.best_sv); bb2.addWidget(self._sl("Best Streak",f"font-size:12px;color:{COLORS['text_dim']};background:transparent;")); bb2.setAlignment(Qt.AlignCenter); sv.addLayout(bb2)
        sl.addLayout(sv); sl.addWidget(self._sl("consecutive days",f"font-size:12px;color:{COLORS['text_dim']};background:transparent;padding-top:4px;")); sl.setAlignment(Qt.AlignCenter); rc.addWidget(sf)
        # PR
        pf = QFrame(); pf.setObjectName("card"); pf.setStyleSheet(f"QFrame#card {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; }}")
        pl = QVBoxLayout(pf); pl.setContentsMargins(24,20,24,20)
        pl.addWidget(self._sl("Personal Records",f"font-size:18px;font-weight:600;color:{COLORS['white']};background:transparent;"))
        self.pr_c = QVBoxLayout(); self.pr_c.setSpacing(8); pl.addLayout(self.pr_c); pl.addStretch(); rc.addWidget(pf,1)
        content.addLayout(rc,1); lo.addLayout(content,1)
        self._load(); self._ls(); self._lpr()

    def _ml(self, t, oid): l = QLabel(t); l.setObjectName(oid); return l
    def _sl(self, t, ss=None): l = QLabel(t); if ss: l.setStyleSheet(ss); return l
    def _row(self, t, w):
        r = QHBoxLayout(); r.setSpacing(12); l = QLabel(t); l.setFixedWidth(100); l.setStyleSheet(f"color:{COLORS['text_secondary']};background:transparent;"); r.addWidget(l); r.addWidget(w,1); return r

    def _ub(self):
        bmi = self.db.calculate_bmi(self.wt_s.value(), self.ht_s.value()); self.bmi_v.setText(f"{bmi:.1f}")
        if bmi<18.5: cat,color = "Underweight",COLORS["accent_blue"]
        elif bmi<25: cat,color = "Normal Weight",COLORS["accent_green"]
        elif bmi<30: cat,color = "Overweight",COLORS["accent_yellow"]
        else: cat,color = "Obese",COLORS["danger"]
        self.bmi_c.setText(cat); self.bmi_v.setStyleSheet(f"font-size:56px;font-weight:800;color:{color};background:transparent;"); self.bmi_c.setStyleSheet(f"font-size:16px;font-weight:600;color:{color};background:transparent;")

    def _load(self):
        p = self.db.get_profile()
        if p:
            self.ni.setText(p["name"] or ""); self.age_s.setValue(p["age"] or 25); self.wt_s.setValue(p["weight_kg"] or 70.0); self.ht_s.setValue(p["height_cm"] or 170.0)
            g = p["gender"] or "male"; idx = self.gen_c.findText(g.capitalize()); self.gen_c.setCurrentIndex(idx if idx>=0 else 0)
            f = p["fitness_level"] or "intermediate"; idx = self.fit_c.findText(f.capitalize()); self.fit_c.setCurrentIndex(idx if idx>=0 else 0)
            self.goal_s.setValue(p["weekly_goal_min"] or 150.0)
        self._ub()

    def _ls(self): self.cur_sv.setText(str(self.db.get_streak())); self.best_sv.setText(str(self.db.get_longest_streak()))

    def _lpr(self):
        while self.pr_c.count():
            item = self.pr_c.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        recs = self.db.get_personal_records()
        if not recs:
            e = QLabel("No records yet.\nLog workouts to track your PRs!"); e.setStyleSheet(f"color:{COLORS['text_dim']};background:transparent;font-size:13px;"); e.setAlignment(Qt.AlignCenter); self.pr_c.addWidget(e); return
        for r in recs[:5]:
            row = QFrame(); row.setFixedHeight(36); row.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_medium']}; border-radius:6px; }}")
            rl = QHBoxLayout(row); rl.setContentsMargins(12,6,12,6)
            rl.addWidget(self._bl(r["exercise_name"],f"font-weight:600;font-size:13px;color:{COLORS['text_primary']};background:transparent;"))
            details = []
            if r["max_weight_kg"]: details.append(f"{r['max_weight_kg']:.1f} kg")
            if r["max_reps"]: details.append(f"{r['max_reps']} reps")
            if r["max_duration_min"]: details.append(f"{r['max_duration_min']:.0f} min")
            if r["max_sets"]: details.append(f"{r['max_sets']} sets")
            rl.addWidget(self._bl(" | ".join(details),f"font-size:12px;color:{COLORS['accent_orange']};background:transparent;")); rl.addStretch(); self.pr_c.addWidget(row)

    def _bl(self, t, ss): l = QLabel(t); l.setStyleSheet(ss); return l
    def _save(self):
        self.db.update_profile(self.ni.text().strip(),self.age_s.value(),self.wt_s.value(),self.ht_s.value(),self.gen_c.currentText().lower(),self.fit_c.currentText().lower(),self.goal_s.value())
    def refresh(self): self._ls(); self._lpr()

# ═══════════════════════════════════════════════════════════
# SECTION 10: WORKOUT ROUTINES PAGE
# ═══════════════════════════════════════════════════════════
class RoutineCard(QFrame):
    start_routine = Signal(int)
    def __init__(self, rd, ec, db, parent=None):
        super().__init__(parent); self.data = rd; cc = CATEGORY_ACCENTS.get(rd["category"],COLORS["accent"]); self.setObjectName("card_hover"); self.setFixedHeight(100)
        self.setStyleSheet(f"QFrame#card_hover {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:12px; border-left:4px solid {cc}; }} QFrame#card_hover:hover {{ border-color:{cc}; background-color:{COLORS['bg_hover']}; }}")
        lo = QHBoxLayout(self); lo.setContentsMargins(20,14,20,14); lo.setSpacing(16)
        info = QVBoxLayout(); info.setSpacing(4)
        info.addWidget(self._bl(rd["name"],f"font-size:17px;font-weight:700;color:{COLORS['white']};background:transparent;"))
        desc = rd["description"] or ""; info.addWidget(self._bl(desc[:57]+"..." if len(desc)>60 else desc,f"font-size:12px;color:{COLORS['text_secondary']};background:transparent;"))
        meta = QHBoxLayout()
        meta.addWidget(self._bl(f"\U0001f3f7 {rd['category']}",f"font-size:11px;color:{cc};background:transparent;"))
        dc = {"beginner":COLORS["accent_green"],"intermediate":COLORS["accent_yellow"],"advanced":COLORS["danger"]}
        meta.addWidget(self._bl(f"\u26a1 {rd['difficulty'].capitalize()}",f"font-size:11px;color:{dc.get(rd['difficulty'],COLORS['text_dim'])};background:transparent;"))
        meta.addWidget(self._bl(f"\U0001f4cb {ec} exercises",f"font-size:11px;color:{COLORS['text_dim']};background:transparent;")); meta.addStretch(); info.addLayout(meta); lo.addLayout(info,1)
        bc = QVBoxLayout(); bc.setSpacing(6)
        sb = QPushButton("Start"); sb.setFixedSize(80,34); sb.setCursor(Qt.PointingHandCursor); sb.setStyleSheet(f"QPushButton {{ background-color:{cc}; color:{COLORS['white']}; border:none; border-radius:6px; font-size:12px; font-weight:600; }} QPushButton:hover {{ background-color:{COLORS['white']}; color:{cc}; }}"); sb.clicked.connect(lambda: self.start_routine.emit(rd["id"])); bc.addWidget(sb)
        vb = QPushButton("View"); vb.setFixedSize(80,34); vb.setCursor(Qt.PointingHandCursor); vb.setStyleSheet(f"QPushButton {{ background-color:{COLORS['bg_medium']}; color:{COLORS['text_secondary']}; border:1px solid {COLORS['border']}; border-radius:6px; font-size:12px; font-weight:500; }} QPushButton:hover {{ border-color:{cc}; color:{COLORS['text_primary']}; }}"); vb.clicked.connect(lambda: self._vd(rd["id"])); bc.addWidget(vb)
        lo.addLayout(bc)
    def _bl(self, t, ss): l = QLabel(t); l.setStyleSheet(ss); return l
    def _vd(self, rid): RoutineDetailDialog(self.data["name"], self.db.get_routine_exercises(rid), self.db, self).exec()

class RoutineDetailDialog(QDialog):
    def __init__(self, rn, exercises, db, parent=None):
        super().__init__(parent); self.db = db; self.setWindowTitle(f"Routine: {rn}"); self.setMinimumWidth(500); self.setMaximumHeight(600)
        self.setStyleSheet(f"QDialog {{ background-color:{COLORS['bg_dark']}; color:{COLORS['text_primary']}; }}")
        lo = QVBoxLayout(self); lo.setSpacing(16)
        lo.addWidget(self._bl(f"\U0001f4cb {rn}",f"font-size:20px;font-weight:700;color:{COLORS['white']};"))
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); sc.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        c = QWidget(); el = QVBoxLayout(c); el.setSpacing(8)
        for i, ex in enumerate(exercises):
            row = QFrame(); row.setFixedHeight(52); row.setStyleSheet(f"QFrame {{ background-color:{COLORS['bg_card']}; border:1px solid {COLORS['border']}; border-radius:8px; }}")
            rl = QHBoxLayout(row); rl.setContentsMargins(14,8,14,8)
            rl.addWidget(self._bl(f"#{i+1}",f"font-weight:700;color:{COLORS['accent']};background:transparent;"))
            rl.addWidget(self._bl(ex["exercise_name"],f"font-weight:600;font-size:14px;color:{COLORS['text_primary']};background:transparent;")); rl.addStretch()
            if ex["sets"] and ex["reps"]: rl.addWidget(self._bl(f"{ex['sets']} x {ex['reps']}",f"font-size:13px;color:{COLORS['accent_blue']};background:transparent;font-weight:600;"))
            if ex["rest_sec"]: rl.addWidget(self._bl(f"Rest: {ex['rest_sec']}s",f"font-size:12px;color:{COLORS['text_dim']};background:transparent;"))
            el.addWidget(row)
        el.addStretch(); sc.setWidget(c); lo.addWidget(sc,1)
        cb = QPushButton("Close"); cb.setFixedHeight(40); cb.clicked.connect(self.accept); lo.addWidget(cb)
    def _bl(self, t, ss): l = QLabel(t); l.setStyleSheet(ss); return l

class _CreateRoutineDialog(QDialog):
    def __init__(self, db, existing, parent=None):
        super().__init__(parent); self.db = db; self.setWindowTitle("Create Workout Routine"); self.setMinimumWidth(550); self.setMinimumHeight(500)
        self.setStyleSheet(f"QDialog {{ background-color:{COLORS['bg_dark']}; color:{COLORS['text_primary']}; }}")
        lo = QVBoxLayout(self); lo.setSpacing(16)
        lo.addWidget(self._bl("Create New Routine",f"font-size:20px;font-weight:700;color:{COLORS['white']};"))
        form = QFormLayout(); form.setSpacing(12)
        self.ni = QLineEdit(); self.ni.setPlaceholderText("e.g., Morning Power Routine"); form.addRow("Routine Name:",self.ni)
        self.ci = QComboBox(); self.ci.addItems(["Strength","Cardio","Flexibility"]); form.addRow("Category:",self.ci)
        self.di = QComboBox(); self.di.addItems(["beginner","intermediate","advanced"]); form.addRow("Difficulty:",self.di)
        self.de = QTextEdit(); self.de.setMaximumHeight(50); self.de.setPlaceholderText("Describe..."); form.addRow("Description:",self.de)
        lo.addLayout(form); lo.addWidget(self._bl("Exercises",f"font-size:14px;font-weight:600;color:{COLORS['white']};"))
        self.exc_c = QVBoxLayout(); self.exc_c.setSpacing(8); lo.addLayout(self.exc_c)
        ab = QPushButton("+ Add Exercise"); ab.setObjectName("secondary"); ab.setFixedHeight(36); ab.clicked.connect(lambda: self._aer(existing)); lo.addWidget(ab)
        self._aer(existing)
        lo.addStretch()
        bb = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.button(QDialogButtonBox.Ok).setText("Save Routine"); bb.accepted.connect(self._save); bb.rejected.connect(self.reject); lo.addWidget(bb)
    def _bl(self, t, ss): l = QLabel(t); l.setStyleSheet(ss); return l
    def _aer(self, existing):
        row = QFrame(); row.setFixedHeight(42); rl = QHBoxLayout(row); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)
        nc = QComboBox(); nc.setFixedWidth(180); nc.addItem("-- Select --"); for ex in existing: nc.addItem(ex["name"]); rl.addWidget(nc)
        ss = QSpinBox(); ss.setRange(1,20); ss.setValue(3); rl.addWidget(self._bl("x",f"background:transparent;")); rl.addWidget(ss)
        rs = QSpinBox(); rs.setRange(1,500); rs.setValue(10); rl.addWidget(self._bl("reps",f"background:transparent;")); rl.addWidget(rs)
        rest = QSpinBox(); rest.setRange(0,300); rest.setValue(60); rest.setSuffix("s"); rest.setFixedWidth(80); rl.addWidget(self._bl("rest",f"background:transparent;")); rl.addWidget(rest)
        rl.addStretch()
        db = QPushButton("X"); db.setFixedSize(28,28); db.setObjectName("danger"); db.setStyleSheet(f"QPushButton {{ background-color:{COLORS['danger']}; color:white; border:none; border-radius:4px; font-size:12px; font-weight:700; }}")
        db.clicked.connect(lambda: (self.exc_c.removeWidget(row), row.deleteLater())); rl.addWidget(db)
        row.nc = nc; row.ss = ss; row.rs = rs; row.rest = rest; self.exc_c.addWidget(row)
    def _save(self):
        n = self.ni.text().strip()
        if not n: return
        exs = []
        for i in range(self.exc_c.count()):
            item = self.exc_c.itemAt(i)
            if item and item.widget(): w = item.widget(); en = w.nc.currentText()
            if en != "-- Select --": exs.append({"name":en,"sets":w.ss.value(),"reps":w.rs.value(),"rest_sec":w.rest.value()})
        if not exs: return
        self.db.add_routine(n, self.ci.currentText(), self.di.currentText().lower(), self.de.toPlainText(), exs); self.accept()

class RoutinesPage(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db; self.current_category = "All"
        lo = QVBoxLayout(self); lo.setContentsMargins(32,28,32,28); lo.setSpacing(20)
        h = QHBoxLayout(); t = QLabel("Workout Routines"); t.setObjectName("title"); h.addWidget(t); h.addStretch()
        cb = QPushButton("+ Create Routine"); cb.setFixedHeight(38); cb.setObjectName("success"); cb.setCursor(Qt.PointingHandCursor); cb.clicked.connect(self._cr); h.addWidget(cb); lo.addLayout(h)
        lo.addWidget(self._mk("Follow pre-built plans or create your own routines","subtitle"))
        pr = QHBoxLayout(); pr.setSpacing(8); self.pills = {}
        for cat in ["All","Strength","Cardio","Flexibility"]:
            b = QPushButton(cat); b.setFixedHeight(34); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _,c=cat: self._f(c)); self._sp2(b,cat=="All"); pr.addWidget(b); self.pills[cat]=b
        self.cl = QLabel("0 routines"); self.cl.setStyleSheet(f"color:{COLORS['text_dim']};font-size:13px;"); pr.addWidget(self.cl); pr.addStretch(); lo.addLayout(pr)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); sc.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.rc = QWidget(); self.rl = QVBoxLayout(self.rc); self.rl.setContentsMargins(0,0,0,0); self.rl.setSpacing(10)
        sc.setWidget(self.rc); lo.addWidget(sc,1); self.refresh()
    def _mk(self, t, oid): l = QLabel(t); l.setObjectName(oid); return l
    def _sp2(self, b, a): b.setStyleSheet(f"QPushButton {{ background-color:{COLORS['accent'] if a else COLORS['bg_card']}; color:{COLORS['white'] if a else COLORS['text_secondary']}; border:{'none' if a else '1px solid '+COLORS['border']}; border-radius:17px; padding:6px 20px; font-size:13px; font-weight:{'600' if a else '500'}; }}")
    def _f(self, cat):
        self.current_category = cat
        for c,b in self.pills.items(): self._sp2(b,c==cat); self._lr()
    def _lr(self):
        while self.rl.count():
            item = self.rl.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        routines = self.db.get_routines(category=self.current_category)
        self.cl.setText(f"{len(routines)} routine{'s' if len(routines)!=1 else ''}")
        for r in routines:
            exs = self.db.get_routine_exercises(r["id"]); card = RoutineCard(r,len(exs),self.db); card.start_routine.connect(self._sr); self.rl.addWidget(card)
        self.rl.addStretch()
    def _sr(self, rid):
        for ex in self.db.get_routine_exercises(rid):
            ed = self.db.get_exercise_by_name(ex["exercise_name"]); cal = ed["calories_per_min"] if ed else 5.0
            self.db.log_workout(ex["exercise_name"],ed["category"] if ed else "Other",(ex["sets"] or 3)*0.5,cal*(ex["sets"]or 3)*0.5,ex["sets"],ex["reps"])
    def _cr(self): _CreateRoutineDialog(self.db,self.db.get_exercises(),self).exec(); self._lr()
    def refresh(self): self._lr()

# ═══════════════════════════════════════════════════════════
# SECTION 11: MAIN WINDOW
# ═══════════════════════════════════════════════════════════
class SidebarButton(QPushButton):
    def __init__(self, icon, label, parent=None):
        super().__init__(parent); self.setText(f"  {icon}   {label}"); self.setFixedHeight(48); self.setCursor(Qt.PointingHandCursor); self.set_active(False)
    def set_active(self, active): self.setStyleSheet(SIDEBAR_BTN_ACTIVE if active else SIDEBAR_BTN_NORMAL)

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__(); self.db = db; self.setWindowTitle("FitTrack - Exercise App"); self.setMinimumSize(QSize(1100,700)); self.resize(QSize(1250,780))
        self.setStyleSheet(GLOBAL_STYLE)
        central = QWidget(); self.setCentralWidget(central); ml = QHBoxLayout(central); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)
        sb = QFrame(); sb.setFixedWidth(230); sb.setStyleSheet(f"QFrame {{ background-color:{COLORS['sidebar_bg']}; border-right:1px solid {COLORS['border']}; }}")
        sbl = QVBoxLayout(sb); sbl.setContentsMargins(14,20,14,20); sbl.setSpacing(6)
        sbl.addWidget(self._bl("FitTrack",f"font-size:22px;font-weight:800;color:{COLORS['accent']};background:transparent;padding-left:4px;"))
        sbl.addWidget(self._bl("Your Personal Trainer",f"font-size:11px;color:{COLORS['text_dim']};background:transparent;padding-left:4px;padding-bottom:14px;"))
        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background-color:{COLORS['border']};"); sbl.addWidget(sep); sbl.addSpacing(8)
        self.nav_btns = []
        nav = [("Dashboard","\U0001f4ca"),("Exercises","\U0001f3cb"),("Routines","\U0001f4cb"),("Timer","\u23f1"),("Charts","\U0001f4c8"),("Profile","\U0001f464"),("Log","\U0001f4dd")]
        for name,icon in nav:
            b = SidebarButton(icon,name); b.clicked.connect(lambda _, n=name: self._nav(n)); sbl.addWidget(b); self.nav_btns.append((name,b))
        sbl.addStretch(); sbl.addWidget(self._bl("v2.0 \u2022 Stay Fit!",f"font-size:11px;color:{COLORS['text_dim']};background:transparent;padding:8px;"))
        sbl.alignment = Qt.AlignCenter; sbl.addWidget(sbl)
        self.stack = QStackedWidget()
        self.dp = DashboardPage(db); self.ep = ExerciseLibraryPage(db); self.rp = RoutinesPage(db); self.tp = WorkoutTimerPage(db); self.cp = ProgressChartsPage(db); self.pp = ProfilePage(db); self.lp = WorkoutLogPage(db)
        for p in [self.dp,self.ep,self.rp,self.tp,self.cp,self.pp,self.lp]: self.stack.addWidget(p)
        ml.addWidget(sb); ml.addWidget(self.stack,1); self._nav("Dashboard")

    def _bl(self, t, ss): l = QLabel(t); l.setStyleSheet(ss); return l
    def _nav(self, page):
        pm = {"Dashboard":0,"Exercises":1,"Routines":2,"Timer":3,"Charts":4,"Profile":5,"Log":6}
        self.stack.setCurrentIndex(pm.get(page_name,0))
        for n,b in self.nav_btns: b.set_active(n==page_name)
        refresh_map = {"Dashboard":self.dp,"Exercises":self.ep,"Routines":self.rp,"Timer":self.tp,"Charts":self.cp,"Profile":self.pp,"Log":self.lp}
        if page_name in refresh_map: refresh_map[page_name].refresh()

# ═══════════════════════════════════════════════════════════
# SECTION 12: ENTRY POINT
# ═══════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    db = Database()
    window = MainWindow(db)
    window.show()
    app.aboutToQuit.connect(db.close)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
