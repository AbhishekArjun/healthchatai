from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os, pickle, openai
from pathlib import Path

# ---------------------- Flask App ----------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------- Database ----------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# ---------------------- Login ----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------- Load ML Model ----------------------
BASE = Path(__file__).parent
MODEL_PATH = BASE / "model" / "model.pkl"
VECT_PATH = BASE / "model" / "vect.pkl"

if MODEL_PATH.exists() and VECT_PATH.exists():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VECT_PATH, "rb") as f:
        vect = pickle.load(f)
else:
    model = None
    vect = None

# ---------------------- OpenAI API ----------------------
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ---------------------- Health Tips ----------------------
health_tips = [
    "Drink at least 8 glasses of water daily.",
    "Take a 10-minute walk after meals.",
    "Maintain a balanced diet with fruits and vegetables.",
    "Get 7-8 hours of sleep every night.",
]

# ---------------------- Doctors (50+) ----------------------
doctors = [
    {"name": "Dr. Aakash Kumar", "specialty": "General Physician", "location": "Raxaul"},
    {"name": "Dr. Priya Sharma", "specialty": "Cardiologist", "location": "Patna"},
    {"name": "Dr. Ravi Singh", "specialty": "Dermatologist", "location": "Gorakhpur"},
    {"name": "Dr. Neha Gupta", "specialty": "Pediatrician", "location": "Patna"},
    {"name": "Dr. Ankit Verma", "specialty": "Orthopedic", "location": "Raxaul"},
    {"name": "Dr. Pooja Yadav", "specialty": "ENT", "location": "Gorakhpur"},
    {"name": "Dr. Rohan Mehta", "specialty": "Neurologist", "location": "Patna"},
    {"name": "Dr. Sneha Rao", "specialty": "Cardiologist", "location": "Raxaul"},
    {"name": "Dr. Karan Malhotra", "specialty": "Dermatologist", "location": "Gorakhpur"},
    {"name": "Dr. Shreya Singh", "specialty": "General Physician", "location": "Patna"},
    {"name": "Dr. Vivek Sharma", "specialty": "Pediatrician", "location": "Raxaul"},
    {"name": "Dr. Aarti Joshi", "specialty": "Orthopedic", "location": "Gorakhpur"},
    {"name": "Dr. Siddharth Roy", "specialty": "ENT", "location": "Patna"},
    {"name": "Dr. Meera Nair", "specialty": "Cardiologist", "location": "Raxaul"},
    {"name": "Dr. Aditya Kapoor", "specialty": "Dermatologist", "location": "Gorakhpur"},
    {"name": "Dr. Tanya Singh", "specialty": "General Physician", "location": "Patna"},
    {"name": "Dr. Mohit Arora", "specialty": "Neurologist", "location": "Raxaul"},
    {"name": "Dr. Priyanka Das", "specialty": "Pediatrician", "location": "Gorakhpur"},
    {"name": "Dr. Rajat Gupta", "specialty": "Cardiologist", "location": "Patna"},
    {"name": "Dr. Ishita Mehra", "specialty": "Orthopedic", "location": "Raxaul"},
    {"name": "Dr. Anshuman Jain", "specialty": "ENT", "location": "Gorakhpur"},
    {"name": "Dr. Ritu Kapoor", "specialty": "Dermatologist", "location": "Patna"},
    {"name": "Dr. Saurabh Saxena", "specialty": "General Physician", "location": "Raxaul"},
    {"name": "Dr. Neelam Roy", "specialty": "Pediatrician", "location": "Gorakhpur"},
    {"name": "Dr. Abhishek Malhotra", "specialty": "Cardiologist", "location": "Patna"},
    {"name": "Dr. Ananya Sharma", "specialty": "Orthopedic", "location": "Raxaul"},
    {"name": "Dr. Kunal Gupta", "specialty": "ENT", "location": "Gorakhpur"},
    {"name": "Dr. Rhea Mehta", "specialty": "Dermatologist", "location": "Patna"},
    {"name": "Dr. Vikas Joshi", "specialty": "General Physician", "location": "Raxaul"},
    {"name": "Dr. Simran Singh", "specialty": "Neurologist", "location": "Gorakhpur"},
    {"name": "Dr. Manish Kumar", "specialty": "Pediatrician", "location": "Patna"},
    {"name": "Dr. Anjali Rao", "specialty": "Cardiologist", "location": "Raxaul"},
    {"name": "Dr. Arjun Verma", "specialty": "Dermatologist", "location": "Gorakhpur"},
    {"name": "Dr. Shalini Gupta", "specialty": "General Physician", "location": "Patna"},
    {"name": "Dr. Rohan Singh", "specialty": "Orthopedic", "location": "Raxaul"},
    {"name": "Dr. Neha Mehta", "specialty": "ENT", "location": "Gorakhpur"},
    {"name": "Dr. Akash Sharma", "specialty": "Cardiologist", "location": "Patna"},
    {"name": "Dr. Tanya Joshi", "specialty": "Dermatologist", "location": "Raxaul"},
    {"name": "Dr. Mohit Verma", "specialty": "General Physician", "location": "Gorakhpur"},
    {"name": "Dr. Priya Malhotra", "specialty": "Neurologist", "location": "Patna"},
    {"name": "Dr. Ankit Sharma", "specialty": "Pediatrician", "location": "Raxaul"},
    {"name": "Dr. Meera Kapoor", "specialty": "Cardiologist", "location": "Gorakhpur"},
    {"name": "Dr. Siddharth Joshi", "specialty": "Orthopedic", "location": "Patna"},
    {"name": "Dr. Ishita Gupta", "specialty": "ENT", "location": "Raxaul"},
    {"name": "Dr. Raj Malhotra", "specialty": "Dermatologist", "location": "Gorakhpur"},
    {"name": "Dr. Neha Roy", "specialty": "General Physician", "location": "Patna"},
    {"name": "Dr. Vivek Singh", "specialty": "Pediatrician", "location": "Raxaul"},
    {"name": "Dr. Tanya Sharma", "specialty": "Cardiologist", "location": "Gorakhpur"},
    {"name": "Dr. Arjun Mehta", "specialty": "Orthopedic", "location": "Patna"},
    {"name": "Dr. Ritu Verma", "specialty": "ENT", "location": "Raxaul"},
]

# ---------------------- Routes ----------------------
@app.route('/')
@login_required
def home():
    return render_template("index.html", tips=health_tips, doctors=doctors, user=current_user.username)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('signup'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

# ---------------------- AI Chat ----------------------
COMMON_SYMPTOMS = {
    "fever": "🤖 You mentioned fever. Rest, hydrate, and consult a doctor if it persists.",
    "cold": "🤖 Cold noted. Stay warm and hydrated.",
    "headache": "🤖 Headache noted. Rest, hydrate, and reduce screen time.",
    "cough": "🤖 Cough may be due to cold, flu, or allergies. Monitor symptoms.",
    "fatigue": "🤖 Fatigue can be caused by multiple reasons. Rest and nutrition are important."
}

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() or {}
    message = data.get("message","").strip()
    if not message:
        return jsonify({"reply": "Please describe your symptoms or say hello."})

    if "conversation" not in session:
        session["conversation"] = []

    session["conversation"].append({"role":"user","content":message})

    # Check common symptoms first
    for symptom, reply_text in COMMON_SYMPTOMS.items():
        if symptom in message.lower():
            session["conversation"].append({"role":"assistant","content":reply_text})
            session.modified = True
            return jsonify({"reply": reply_text})

    # GPT fallback
    reply = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system","content":"You are a helpful healthcare assistant."}] + session["conversation"],
            max_tokens=200, temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        if model and vect:
            X = vect.transform([message])
            pred = model.predict(X)[0]
            proba = float(model.predict_proba(X).max())
            reply = f"🤖 May relate to *{pred}* (confidence: {proba:.2f}). Not a medical diagnosis."
        else:
            reply = "🤖 Sorry, I can’t respond right now. Try again."

    session["conversation"].append({"role":"assistant","content":reply})
    session.modified = True
    return jsonify({"reply": reply})

@app.route('/reset_chat', methods=['POST'])
@login_required
def reset_chat():
    session["conversation"] = []
    session.modified = True
    return jsonify({"status":"ok","message":"Chat reset."})

# ---------------------- Doctor Search ----------------------
@app.route('/find_doctor', methods=['GET'])
@login_required
def find_doctor():
    query = request.args.get("query","").lower().strip()
    specialty = request.args.get("specialty","").lower()
    location = request.args.get("location","").lower()
    results = [
        d for d in doctors
        if (query in d["name"].lower() or query in d["specialty"].lower() or query in d["location"].lower() or not query)
        and (specialty in d["specialty"].lower() or not specialty)
        and (location in d["location"].lower() or not location)
    ]
    return jsonify({"doctors": results})

# ---------------------- Book Appointment ----------------------
@app.route('/book', methods=['POST'])
@login_required
def book():
    data = request.get_json() or {}
    name = data.get("name")
    doctor = data.get("doctor")
    date = data.get("date")
    time = data.get("time")
    if not (name and doctor and date):
        return jsonify({"status":"error","message":"Name, doctor, and date required"}), 400
    return jsonify({"status":"ok","message":f"Appointment booked with {doctor} on {date} {('at '+time) if time else ''} for {name}."})

# ---------------------- Run ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    data = request.get_json() or request.form
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    if not (name and email and phone and message):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    # For now, just print to console (you can later send an email or save to DB)
    print(f"New message from {name} ({email}, {phone}): {message}")

    return jsonify({"status": "ok", "message": "Your message has been sent successfully!"})
