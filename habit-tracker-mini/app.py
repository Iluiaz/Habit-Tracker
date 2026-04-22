"""Flask mini-project: Habit Tracker web app."""
from __future__ import annotations

from datetime import date, datetime

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///habits.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db = SQLAlchemy(app)

FREQUENCIES = {"daily", "weekly"}


class Habit(db.Model):
    """Habit entity with progress tracking state."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(40), nullable=False, default="health")
    frequency = db.Column(db.String(12), nullable=False, default="daily")
    streak = db.Column(db.Integer, nullable=False, default=0)
    last_completed = db.Column(db.Date, nullable=True)
    completed_today = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "frequency": self.frequency,
            "streak": self.streak,
            "last_completed": self.last_completed.isoformat() if self.last_completed else None,
            "completed_today": self.completed_today,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def _validate_payload(data: dict) -> tuple[bool, str | None]:
    if not data or not str(data.get("title", "")).strip():
        return False, "title is required"

    frequency = str(data.get("frequency", "daily")).lower()
    if frequency not in FREQUENCIES:
        return False, "frequency must be daily or weekly"

    return True, None


def _refresh_daily_flags(habit: Habit) -> None:
    if habit.last_completed != date.today():
        habit.completed_today = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/habits", methods=["GET"])
def get_habits():
    habits = Habit.query.order_by(Habit.created_at.desc()).all()
    for habit in habits:
        _refresh_daily_flags(habit)
    db.session.commit()
    return jsonify([habit.to_dict() for habit in habits])


@app.route("/api/habits", methods=["POST"])
def create_habit():
    data = request.get_json(silent=True) or {}
    is_valid, error = _validate_payload(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    habit = Habit(
        title=str(data["title"]).strip(),
        category=str(data.get("category", "health")).strip() or "health",
        frequency=str(data.get("frequency", "daily")).lower(),
    )
    db.session.add(habit)
    db.session.commit()
    return jsonify(habit.to_dict()), 201


@app.route("/api/habits/<int:habit_id>", methods=["PUT"])
def update_habit(habit_id: int):
    habit = Habit.query.get_or_404(habit_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify({"error": "title must not be empty"}), 400
        habit.title = title

    if "category" in data:
        category = str(data.get("category", "")).strip()
        habit.category = category or "health"

    if "frequency" in data:
        frequency = str(data.get("frequency", "")).lower()
        if frequency not in FREQUENCIES:
            return jsonify({"error": "frequency must be daily or weekly"}), 400
        habit.frequency = frequency

    db.session.commit()
    return jsonify(habit.to_dict())


@app.route("/api/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id: int):
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    return jsonify({"message": "Habit deleted"})


@app.route("/api/habits/<int:habit_id>/toggle", methods=["PATCH"])
def toggle_habit(habit_id: int):
    habit = Habit.query.get_or_404(habit_id)
    today = date.today()

    if habit.last_completed == today and habit.completed_today:
        habit.completed_today = False
        habit.streak = max(0, habit.streak - 1)
        db.session.commit()
        return jsonify(habit.to_dict())

    if habit.last_completed is None:
        habit.streak = 1
    else:
        delta = (today - habit.last_completed).days
        if delta == 1:
            habit.streak += 1
        elif delta > 1:
            habit.streak = 1

    habit.last_completed = today
    habit.completed_today = True
    db.session.commit()
    return jsonify(habit.to_dict())


@app.route("/api/stats", methods=["GET"])
def get_stats():
    habits = Habit.query.all()
    for habit in habits:
        _refresh_daily_flags(habit)

    total = len(habits)
    done_today = sum(1 for h in habits if h.completed_today)
    longest_streak = max((h.streak for h in habits), default=0)

    db.session.commit()
    return jsonify(
        {
            "total_habits": total,
            "done_today": done_today,
            "completion_rate": round((done_today / total) * 100, 1) if total else 0.0,
            "longest_streak": longest_streak,
        }
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
