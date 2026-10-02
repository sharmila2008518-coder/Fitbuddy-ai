from datetime import datetime
from flask import Flask, flash, redirect, render_template_string, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "fitbuddy-secret-key-123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fitbuddy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database Models
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(100), nullable=False)
    duration_mins = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

# HTML Template Embedded
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FitBuddy - Fitness Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1, h2 { color: #2c3e50; }
        .stats { display: flex; gap: 15px; margin-bottom: 25px; }
        .card { flex: 1; background: #eef2f5; padding: 15px; border-radius: 6px; text-align: center; }
        .card h3 { margin: 0 0 5px 0; color: #34495e; }
        .card p { margin: 0; font-size: 24px; font-weight: bold; color: #27ae60; }
        form { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 10px; margin-bottom: 30px; }
        input, button { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
        button { background-color: #27ae60; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #219150; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .action-btn { color: #e74c3c; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💪 FitBuddy Dashboard</h1>
        
        <div class="stats">
            <div class="card">
                <h3>Total Workouts</h3>
                <p>{{ total_workouts }}</p>
            </div>
            <div class="card">
                <h3>Total Active Minutes</h3>
                <p>{{ total_duration }} mins</p>
            </div>
            <div class="card">
                <h3>Total Calories Burned</h3>
                <p>{{ total_calories }} kcal</p>
            </div>
        </div>

        <h2>Log a New Workout</h2>
        <form action="/add" method="POST">
            <input type="text" name="exercise" placeholder="Exercise (e.g. Running)" required>
            <input type="number" name="duration" placeholder="Duration (mins)" min="1" required>
            <input type="number" name="calories" placeholder="Calories Burned" min="0" required>
            <button type="submit">Log Workout</button>
        </form>

        <h2>Recent Activity Log</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Exercise</th>
                    <th>Duration</th>
                    <th>Calories</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for workout in workouts %}
                <tr>
                    <td>{{ workout.date.strftime('%Y-%m-%d') }}</td>
                    <td>{{ workout.exercise }}</td>
                    <td>{{ workout.duration_mins }} mins</td>
                    <td>{{ workout.calories_burned }} kcal</td>
                    <td><a href="/delete/{{ workout.id }}" class="action-btn">Delete</a></td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="5" style="text-align:center;">No workouts logged yet. Start moving!</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    workouts = Workout.query.order_by(Workout.date.desc()).all()
    
    total_workouts = len(workouts)
    total_duration = sum(w.duration_mins for w in workouts)
    total_calories = sum(w.calories_burned for w in workouts)
    
    return render_template_string(
        HTML_TEMPLATE,
        workouts=workouts,
        total_workouts=total_workouts,
        total_duration=total_duration,
        total_calories=total_calories
    )

@app.route("/add", methods=["POST"])
def add_workout():
    exercise = request.form.get("exercise")
    duration = request.form.get("duration")
    calories = request.form.get("calories")

    if exercise and duration and calories:
        new_workout = Workout(
            exercise=exercise,
            duration_mins=int(duration),
            calories_burned=int(calories)
        )
        db.session.add(new_workout)
        db.session.commit()
    
    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete_workout(id):
    workout = Workout.query.get_or_404(id)
    db.session.delete(workout)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Auto-creates SQLite database on first run
    app.run(debug=True)
