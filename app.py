from flask import Flask, render_template, request, redirect, session, jsonify
import random, time, csv, os

app = Flask(__name__)
app.secret_key = 'supersecret'  # Needed for session
CSV_FILE = "addition_scores.csv"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/start', methods=['POST'])
def start():
    name = request.form['name'].strip()
    if not name:
        return redirect('/')
    
    session['name'] = name
    session['questions'] = [(random.randint(1, 20), random.randint(1, 20)) for _ in range(10)]
    session['answers'] = []
    session['timings'] = []
    session['start_time'] = time.time()
    session['current'] = 0

    return redirect('/quiz')

@app.route('/quiz')
def quiz():
    if session['current'] >= 10:
        return redirect('/results')
    q = session['questions'][session['current']]
    return render_template("quiz.html", question=q, index=session['current'] + 1)

@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form['answer']
    if not answer.isdigit():
        return jsonify({"result": "invalid"})

    q = session['questions'][session['current']]
    correct = q[0] + q[1]
    time_taken = round(time.time() - session['start_time'], 2)

    session['answers'].append(int(answer))
    session['timings'].append(time_taken)
    session['start_time'] = time.time()
    session['current'] += 1

    if int(answer) == correct:
        return jsonify({"result": "correct"})
    else:
        return jsonify({"result": "incorrect"})

@app.route('/results')
def results():
    name = session.get('name')
    questions = session.get('questions')
    answers = session.get('answers')
    timings = session.get('timings')
    score = sum(1 for i, q in enumerate(questions) if q[0]+q[1] == answers[i])
    total_time = sum(timings)

    # Save to CSV
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, score, *timings])

    # Previous attempts
    past_attempts = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == name:
                    try:
                        t = sum(float(x) for x in row[2:])
                        past_attempts.append(round(t, 2))
                    except:
                        continue

    return render_template("results.html",
                           name=name,
                           questions=questions,
                           answers=answers,
                           timings=timings,
                           score=score,
                           total_time=round(total_time, 2),
                           previous=past_attempts[:-1])  # last one is current

if __name__ == '__main__':
    app.run(debug=True)
