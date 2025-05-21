from flask import Flask,flash, current_app as app, abort
from flask import render_template , request, redirect, url_for
from flask_login import login_required, logout_user, current_user
from models.model import *
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from functools import wraps

def user_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            abort(403)
        
        return func(*args, **kwargs) 
    return decorated_function
    

@app.route("/dashboard")
@login_required
@user_only
def dashboard():
    if current_user.is_authenticated:
        today_date = date.today()

        quizes = db.session.query(
            Quiz.id.label("id"),
            Quiz.date_of_quiz.label("date"),
            Quiz.time_duration.label("time"),
            Chapter.name.label("chapter"),
            Subject.name.label("subject"),
            db.func.count(Question.id).label("question_count")
        ).join(Chapter, Quiz.chapter_id == Chapter.id) \
        .join(Subject, Chapter.subject_id == Subject.id) \
        .outerjoin(Question, Question.quiz_id == Quiz.id) \
        .filter(Quiz.date_of_quiz >= today_date) \
        .group_by(Quiz.id, Chapter.name, Subject.name) \
        .order_by(Quiz.date_of_quiz.asc()) \
        .all()

        return render_template("user/dashboard.html", quizes = quizes)

    return redirect(url_for("index"))

@app.route("/quiz/<int:id>", methods = ["POST", "GET"])
@login_required
@user_only
def quiz_start(id):
    quiz = db.session.query(Quiz).filter(Quiz.id == id).first()
    questions = db.session.query(Question).filter(Question.quiz_id == id).all()

    if current_user.is_authenticated and request.method == "POST":
        question_answer = {question.id : question.correct_option for question in questions}
        answers_dict = {int(q_id): request.form.get(q_id) for q_id in request.form}  
        score = 0
        
        for key, value in answers_dict.items():
            if value == question_answer[key]:
                score += 1
        
        if db.session.query(Score).filter(Score.user_id == current_user.id, Score.quiz_id == id).first():
            flash("Already attempted the quiz", "danger")
            return redirect(url_for("dashboard"))


        new_score = Score(user_id = current_user.id, quiz_id = id, total_scored = score)
        db.session.add(new_score)
        db.session.commit()
        flash("Quiz submitted successfully", "success")
        return redirect(url_for("dashboard"))

    if current_user.is_authenticated:
        quiz_questions = {"id":quiz.id, "time" : quiz.time_duration, "questions":questions}

        if quiz.date_of_quiz != date.today():
            flash("Attempt at the date of the quiz", "danger")
            return redirect(url_for("dashboard"))

        if db.session.query(Score).filter(Score.user_id == current_user.id, Score.quiz_id == id).first():
            flash("Already attempted the quiz", "danger")
            return redirect(url_for("dashboard"))
        
        return render_template("user/quiz.html", quiz_questions = quiz_questions)
        
    return redirect(url_for("index"))

@app.route("/view-quiz/<int:id>")
@login_required
@user_only
def view_quiz(id):
    if current_user.is_authenticated:
        quiz = db.session.query(
        Quiz.id,
        Subject.name.label("subject"),
        Chapter.name.label("chapter"),
        db.func.count(Question.id).label("question_count"),
        Quiz.date_of_quiz.label("date"),
        Quiz.time_duration.label("time"),
        Quiz.remarks
        ).join(Chapter, Quiz.chapter_id == Chapter.id) \
        .join(Subject, Chapter.subject_id == Subject.id) \
        .outerjoin(Question, Question.quiz_id == Quiz.id) \
        .filter(Quiz.id == id) \
        .group_by(Quiz.id, Subject.name, Chapter.name, Quiz.date_of_quiz, Quiz.time_duration, Quiz.remarks) \
        .first() 


        return render_template("user/view_quiz.html", quiz = quiz)
    
@app.route("/score")
@login_required
@user_only
def quiz_score():
    if current_user.is_authenticated:
        scores = db.session.query(
        Subject.name.label("subject"),
        Chapter.name.label("chapter"),
        Quiz.date_of_quiz.label("date"),
        Score.total_scored.label("score"),
        db.func.count(Question.id).label("question_count") 
        ).join(Quiz, Score.quiz_id == Quiz.id) \
        .join(Chapter, Quiz.chapter_id == Chapter.id) \
        .join(Subject, Chapter.subject_id == Subject.id) \
        .join(Question, Quiz.id == Question.quiz_id) \
        .filter(Score.user_id == current_user.id) \
        .order_by(Score.time_stamp_of_attempt.asc()) \
        .group_by(Quiz.id)

        return render_template("user/score.html", scores = scores)
    
    return redirect(url_for("index"))

@app.route("/summary")
@login_required
@user_only
def summary():
    if current_user.is_authenticated:
        id = current_user.id
        if current_user.is_authenticated:
            quiz_attempted = db.session.query(
                Score.user_id.label("id"),
                Subject.name.label("Subject"),
                db.func.count(Chapter.id).label("Chapter_Count")
            ).join(Quiz, Score.quiz_id == Quiz.id) \
            .join(Chapter, Chapter.id == Quiz.chapter_id) \
            .join(Subject, Chapter.subject_id == Subject.id) \
            .filter(Score.user_id == current_user.id)\
            .group_by(Subject.id, ) \
            .all()

            month_quiz = (
                db.session.query(
                    db.func.strftime('%m', Score.time_stamp_of_attempt).label("month"), 
                    db.func.strftime('%Y', Score.time_stamp_of_attempt).label("year"),
                    db.func.count(Score.user_id).label("attempts") 
                )
                .filter(Score.user_id == current_user.id)
                .group_by("month")
                .order_by("month")
                .all()
            )
            months = [f'{quiz.month} {quiz.year}' for quiz in month_quiz]
            attempt = [quiz.attempts for quiz in month_quiz]

            plt.pie(attempt, labels=months, autopct=lambda p: '{:.0f}'.format(p * sum(attempt) / 100),  startangle=90)
            file_path = os.path.join("static/charts/piechart", f'{current_user.id}piechart.png')
            plt.savefig(file_path)
            plt.close()


            subjects = [quiz.Subject for quiz in quiz_attempted]
            chapter_counts = [quiz.Chapter_Count for quiz in quiz_attempted]

            if chapter_counts: 
                plt.yticks([i for i in range(1, max(chapter_counts) + 2)])
            else:
                plt.yticks([1])
             
            plt.bar(subjects, chapter_counts)
            file_path = os.path.join("static/charts/histogram", f'{current_user.id}histogram.png')
            plt.savefig(file_path)
            plt.close()

            return render_template("user/summary.html", month_quiz = month_quiz)

    return render_template("user/summary.html")

