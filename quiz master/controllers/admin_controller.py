from flask import current_app as app, render_template, request, redirect, url_for, flash, jsonify, abort
from models.model import *
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from flask_login import login_required, current_user
from functools import wraps

def admin_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            abort(403)
        
        return func(*args, **kwargs) 
    return decorated_function
    


#verified
@app.route("/admin/dashboard")
@app.route("/admin")
@login_required
@admin_only
def admin_dashboard():
    if current_user.id != 1:
        return "you are not admin"

    if request.args.get("q"):
        id = request.args.get("q")
        subject = db.session.query(Subject).filter(Subject.id == id).first()

        if subject:
            subject_list = [{"id": id, "name": subject.name, "chapters": get_chapters(id)}]

            return render_template("admin/dashboard.html", subjects = subject_list)


    subjects = db.session.query(Subject).all()
    subject_list = [{"id":subject.id, "name": subject.name, "chapters" : get_chapters(subject.id)} for subject in subjects]
    
    return render_template("admin/dashboard.html", subjects = subject_list)


#verified
@app.route("/admin/quiz", methods = ["POST", "GET"])
@login_required
@admin_only
def quiz():
    q = request.args.get("q")

    if q == "all":
        quizes = db.session.query(Quiz, Chapter).join(Chapter).all()
        quiz_list = [{"questions": get_questions(quiz.id) ,"id":quiz.id, "chapter": chapter.name, "date_of_quiz": quiz.date_of_quiz, "time_duration": quiz.time_duration} for quiz, chapter in quizes]

        return render_template("/admin/quiz.html" , quizes = quiz_list)
    
    if q:
        quizes = db.session.query(Quiz, Chapter).join(Chapter).filter(Quiz.chapter_id == q).all()
        quiz_list = [{"questions": get_questions(quiz.id), "id":quiz.id, "chapter": chapter.name, "date_of_quiz": quiz.date_of_quiz, "time_duration": quiz.time_duration} for quiz, chapter in quizes]
        return render_template("/admin/quiz.html" , quizes = quiz_list)

    

    quizes = db.session.query(Quiz, Chapter).join(Chapter).filter(Quiz.date_of_quiz >= date.today()).all()
    quiz_list = [{"questions": get_questions(quiz.id) ,"id":quiz.id, "chapter": chapter.name, "date_of_quiz": quiz.date_of_quiz, "time_duration": quiz.time_duration} for quiz, chapter in quizes]

    return render_template("/admin/quiz.html" , quizes = quiz_list)



@app.route("/admin/summary", methods = ["POST", "GET"])
@login_required
@admin_only
def admin_summary():
    users = db.session.query(User).filter(User.id != 1).all()
    subjects_all = db.session.query(Subject)

    if request.args.get("subject") and request.args.get("chapter"):
        subject_id = request.args.get("subject")
        chapter_id = request.args.get("chapter")

        quiz_scores = db.session.query(
            User.full_name.label("name"),
            Score.total_scored.label("total_scored"),
            Subject.name.label("subject_name"),
            Chapter.name.label("chapter_name"),
            Quiz.date_of_quiz.label("quiz_date"),
            Quiz.time_duration.label("quiz_time"))\
            .join(User, Score.user_id == User.id)\
            .join(Quiz, Score.quiz_id == Quiz.id)\
            .join(Chapter, Quiz.chapter_id == Chapter.id)\
            .join(Subject, Chapter.subject_id == Subject.id)\
            .filter(Subject.id == subject_id, Chapter.id == chapter_id)\
            .order_by(Quiz.date_of_quiz.desc(), Score.total_scored.desc()).all()
        
        return render_template("admin/summary.html", quiz_scores = quiz_scores, users = users, subjects = subjects_all)




    if request.args.get("user"):
        user_id = int(request.args.get("user"))
        user = db.session.query(User).filter(User.id == user_id).first()
        

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
            .filter(Score.user_id == user_id) \
            .order_by(Score.time_stamp_of_attempt.asc()) \
            .group_by(Quiz.id).all()

        quiz_attempted = db.session.query(
                Score.user_id.label("id"),
                Subject.name.label("Subject"),
                db.func.count(Chapter.id).label("Chapter_Count")
            ).join(Quiz, Score.quiz_id == Quiz.id) \
            .join(Chapter, Chapter.id == Quiz.chapter_id) \
            .join(Subject, Chapter.subject_id == Subject.id) \
            .filter(Score.user_id == user_id)\
            .group_by(Subject.id, ) \
            .all()

        month_quiz = (
            db.session.query(
                db.func.strftime('%m', Score.time_stamp_of_attempt).label("month"), 
                db.func.strftime('%Y', Score.time_stamp_of_attempt).label("year"),
                db.func.count(Score.user_id).label("attempts") 
            )
            .filter(Score.user_id == user_id)
            .group_by("month")
            .order_by("month")
            .all()
        )
        months = [f'{quiz.month} {quiz.year}' for quiz in month_quiz]
        attempt = [quiz.attempts for quiz in month_quiz]

        plt.pie(attempt, labels=months, autopct=lambda p: '{:.0f}'.format(p * sum(attempt) / 100),  startangle=90)
        file_path = os.path.join("static/charts/piechart", f'{user_id}piechart.png')
        plt.savefig(file_path)
        plt.close()


        subjects = [quiz.Subject for quiz in quiz_attempted]
        chapter_counts = [quiz.Chapter_Count for quiz in quiz_attempted]
        
        if chapter_counts: 
            plt.yticks([i for i in range(1, max(chapter_counts) + 2)])
        else:
            plt.yticks([1])

        plt.bar(subjects, chapter_counts)
        file_path = os.path.join("static/charts/histogram", f'{user_id}histogram.png')
        plt.savefig(file_path)
        plt.close()

        return render_template("admin/summary.html", scores = scores, user = user, users = users , subjects= subjects_all)

    return render_template("admin/summary.html", users = users , subjects = subjects_all)


#verified
@app.route("/admin/add_subject", methods= ["POST", "GET"])
@login_required
@admin_only
def add_subject():
    if request.method == 'POST':
        subject_name = request.form['subject_name'].strip()
        description = request.form['description']

        if not subject_name:
            flash("Please Enter Subject Name...", "danger")
            return redirect(request.url)

        existing_subject = Subject.query.filter(Subject.name==subject_name).first()

        if existing_subject:
            flash("Subject Already Exits..." , "danger")
            return redirect(request.url)

        new_subject = Subject(name = subject_name, description = description)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject Added Succeffully.." ,"success")
        return redirect(request.url)

    return render_template("admin/subject.html", add_subject = True)


#verified
@app.route("/admin/edit_subject", methods = ["POST", "GET"])
@login_required
@admin_only
def edit_subject():
    subject_id = request.args.get("subject_id")

    if not subject_id:
        flash("Something went Wrong! Try Again..." , "danger")
        return redirect(request.url)

    if request.method == "POST":

        subject = db.session.query(Subject).filter(Subject.id == subject_id).first()

        subject_name = request.form['subject_name'].strip()
        description = request.form['description']

        if not subject_name:
            flash("Please Enter Subject Name...", "danger")
            return redirect(request.url)
        
        if subject_name == subject.name:
            subject.description = description
            db.session.commit()
            flash("Subject Edited Successfully...", "success")
            return redirect(request.url)

        existing_subject = db.session.query(Subject).filter(Subject.name==subject_name).first()
        if existing_subject:
            flash("Subject Already Exits..." ,"danger")
            return redirect(request.url)

        subject.name = subject_name
        subject.description = description
        db.session.commit()

        flash("Subject Edited Successfully...", "success")
        return redirect(request.url)
    

    subject = db.session.query(Subject).filter(Subject.id == subject_id).first()

    if not subject:
        flash("Something Went Wrong! Try Again...", "danger")
        return redirect(request.referrer)

    return render_template("admin/subject.html", edit_subject=True, subject = subject)



#verified
@app.route("/admin/add_chapter" , methods = ["POST", "GET"])
@login_required
@admin_only
def add_chapter():
    if request.method=='POST':
        subject_id = request.args.get('subject_id')
        chapter_name = request.form['chapter_name'].strip()
        description = request.form['description']

        if not subject_id or not chapter_name:
            flash("Select Subject and Chapter...", "danger")
            return redirect(request.url)

        existing_chapter = Chapter.query.filter(Chapter.name==chapter_name, Chapter.subject_id==subject_id).first()

        if existing_chapter:
            flash("Chapter Already Exits" , "error")
            return redirect(request.url)
        
        new_chapter = Chapter(name = chapter_name, description = description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter Added Succeffully.." ,"success")
        return redirect(request.url) 
         
    return render_template("admin/chapter.html", add_chapter= True )



#verified
@app.route("/admin/delete-chapter", methods = ["POST", "GET"])
@login_required
@admin_only
def delete_chapter():
    chapter_id = request.args.get('id')
    if not chapter_id:
        flash("Chapter Deletion failed..." , "danger")
        return redirect(request.referrer)
    
    chapter_with_quiz = db.session.query(Chapter)\
        .join(Quiz, Chapter.id == Quiz.chapter_id)\
        .filter(Chapter.id == chapter_id, Quiz.date_of_quiz <= date.today()).first()
    
    if chapter_with_quiz:
        flash("You can't delete a chapter with Quiz..." , "danger")
        return redirect(request.referrer)
    
    try:
        db.session.query(Question).filter(Question.chapter_id == chapter_id).delete()
        db.session.query(Quiz).filter(Quiz.chapter_id == chapter_id).delete()
    except:
        None

    db.session.query(Chapter).filter(Chapter.id == chapter_id).delete()
    
    db.session.commit()
    flash("Chapter Deleted Successfully...", "success")
    return redirect(request.referrer)


#verified
@app.route("/admin/edit-chapter", methods = ["POST", "GET"])
@login_required
@admin_only
def edit_chapter():
    chapter_id = request.args.get('chapter_id')
    subject_id = request.args.get('subject_id')

    if request.method == "POST":
        chapter_name = request.form['chapter_name']
        description = request.form['description']

        if not chapter_id or not subject_id:
            flash("Something Went Wrong! Try Again...", "danger")
            return redirect(url_for("admin_dashboard"))

        if not chapter_name:
            flash("Chapter Name is required...", "danger")
            return redirect(request.url)
        
        chapter = db.session.query(Chapter).filter(Chapter.id == chapter_id).first()
        
        if chapter_name == chapter.name:
            chapter.description = description
            db.session.commit()
            flash("Chapter Edit Successfully..." , "success")
            return redirect(url_for('admin_dashboard'))
            

        existing_chapter = db.session.query(Chapter).filter(Chapter.name==chapter_name, Chapter.subject_id==subject_id).first()
        if existing_chapter:
            flash("Chapter Already Exists...", "danger")
            return redirect(request.url)

        chapter.name = chapter_name
        chapter.description = description
        db.session.commit()
        flash("Chapter Edit Successfully..." , "success")
        return redirect(request.url)
    
    chapter_details = db.session.query(Chapter).filter(Chapter.id == chapter_id).first()

    return render_template("admin/chapter.html", chapter=chapter_details , edit_chapter=True)





#verified
@app.route("/admin/add-quiz", methods = ["POST", "GET"])
@login_required
@admin_only
def add_quiz():
    if request.method == "POST":
        chapter_id = int(request.form['chapter'])
        date_of_quiz_str = request.form['date_of_quiz']
        time = request.form['time'].strip()
        remarks = request.form['remarks']

        date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()

        if not ":" in time:
            time_duration = time + ":00"
        else:
            time_duration = time

        if date_of_quiz < date.today():
            flash("Select a future date for quiz...")
            return redirect(request.url)

        if not chapter_id or not date_of_quiz or not time_duration:
            flash("Selct All Fields...", "danger")
            return redirect(request.url)

        new_quiz = Quiz(chapter_id = chapter_id, date_of_quiz = date_of_quiz, time_duration = time_duration, remarks = remarks)
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz Added Successfully", "success")
        return redirect(request.url) 

    subjects = db.session.query(Subject).all()
    return render_template("/admin/quizform.html", subjects = subjects, add_quiz = True)



#verified
@app.route("/admin/edit-quiz", methods = ["POST", "GET"])
@login_required
@admin_only
def edit_quiz():
    q = request.args.get("q")
    
    if request.method =='POST':
        chapter_id = request.form["chapter"]
        date_of_quiz_str = request.form['date_of_quiz']
        time = request.form['time'].strip()
        remarks = request.form['remarks']

        date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()

        if not ":" in time:
            time_duration = time + ":00"
        else:
            time_duration = time

        if date_of_quiz < date.today():
            flash("Select a future date for quiz...", "danger")
            return redirect(request.url)

        if not date_of_quiz or not time_duration or not chapter_id:
            flash("Fill All the Fields...", "danger")
            return redirect(request.url)
    

        quiz = db.session.query(Quiz).filter(Quiz.id == q ).first()

        if quiz.date_of_quiz < date.today():
            flash("Can't edit Previous quiz...", "danger")
            return redirect(request.url)

        quiz.chapter_id = chapter_id
        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = time_duration
        quiz.remarks = remarks
        db.session.commit()
        flash("Quiz Edited Successfully...", "success")
        return redirect(request.url)         

    if not q:
        flash("Something Went Wrong! Try Again...", "danger")
        return redirect(url_for("quiz"))

    quiz = db.session.query(
        Quiz.id.label("id"),
        Quiz.remarks.label("remarks"),
        Quiz.date_of_quiz.label("date_of_quiz"),
        Quiz.time_duration.label("time"),
        Quiz.chapter_id.label("chapter_id"),
        Chapter.name.label("chapter_name"),
        Quiz.remarks.label("remarks"),
        Subject.name.label("subject_name"))\
        .join(Quiz, Chapter.id == Quiz.chapter_id)\
        .join(Subject, Chapter.subject_id == Subject.id )\
        .filter(Quiz.id == q).first()
    
    subjects = db.session.query(Subject).all()

    return render_template("/admin/quizform.html", subjects = subjects,  quiz = quiz , edit_quiz = True)




#verified
@app.route("/admin/delete-quiz", methods = ["POST", "GET"])
@login_required
@admin_only
def dlt_quiz():
    q = int(request.args.get("q"))

    if q:
        quiz = db.session.query(Quiz).filter(Quiz.id == q).first()
        if quiz.date_of_quiz <= date.today():
            flash("Can't Delete a Past Quiz...", "danger")
            return redirect(request.referrer)
        
        questions = db.session.query(Question).filter(Question.quiz_id == q).all()
        for question in questions:
            db.session.delete(question)
        
        db.session.delete(quiz)

        db.session.commit()
        flash("Quiz Deleted Successfully...", "success")
        return redirect(request.referrer)


    flash("Something Went Wrong...", "danger")
    return redirect(request.referrer)


#verified
@app.route("/admin/add-question", methods = ["POST", "GET"])
@login_required
@admin_only
def add_question():
    if request.method == "POST":
        quiz_id = request.args.get('quiz_id')
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct-option']

        if not quiz_id:
            flash("Quiz is required", "error")
            return redirect(request.url)
        
        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            flash("All fields are required...", "error")
            return redirect(request.url)

        new_question = Question(quiz_id = quiz_id, question_statement = question_statement, option1 = option1, option2 = option2, option3 = option3, option4 = option4, correct_option = correct_option)
        db.session.add(new_question)
        db.session.commit()
        flash("Question Added Successfully...", "success")
        return redirect(request.url)
    
    return render_template("/admin/question.html", add_question = True)



#verified
@app.route("/admin/edit-question", methods = ["POST", "GET"])
@login_required
@admin_only
def edit_question():
    question_id = request.args.get("id")

    if not question_id:
        flash("Something Went Wrong! Try Again..." , "danger")
        return redirect(request.referrer)
    
    if request.method == "POST":

        if db.session.query(Question)\
            .join(Quiz, Question.quiz_id == Quiz.id)\
            .filter(Question.id == question_id , Quiz.date_of_quiz < date.today()).first():
            flash("Can't Edit a Previous Quiz Question...", "danger")
            return redirect(request.referrer)

        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct-option']

        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            flash("All fields are required", "error")
            return redirect(request.url)

        question = Question.query.filter_by(id=question_id).first()
        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = correct_option

        db.session.commit()
        flash("Question Updated Successfully", "success")
        return redirect(request.referrer)
    
    
    question = db.session.query(Question).filter(Question.id == question_id).first()

    if not question:
        flash("Something Went Wrong! Try Again..." , "danger")
        return redirect(request.referrer)
    
    return render_template("admin/question.html", question = question, edit_question = True)
    



#verified
@app.route("/admin/delete-question", methods = ["POST", "GET"])
@login_required
@admin_only
def delete_question():
    question_id = request.args.get('id')

    if not question_id:
        flash("Something Went Wrong! Try Again..." , "danger")
        return redirect(request.referrer)
    
    question = db.session.query(Question).filter(Question.id == question_id).first()
    if not question:
        flash("Something Went Wrong! Try Again..." , "danger")
        return redirect(request.referrer)
    
    if db.session.query(Question)\
            .join(Quiz, Question.quiz_id == Quiz.id)\
            .filter(Question.id == question_id , Quiz.date_of_quiz < date.today()).first():
            flash("Can't Delete a Previous Quiz Question...", "danger")
            return redirect(request.referrer)

    db.session.delete(question)
    db.session.commit()
    flash("Question Deleted Successfully.." , "success")
    return redirect(request.referrer)



#verified
@app.route("/admin/get-chapters", methods = ["POST", "GET"])
@login_required
@admin_only
def get_chapters():
    subject_id = request.args.get('subject_id')
    if not subject_id:

        chapters = db.session.query(Chapter).all()
        chapters = [{"id":chapter.id, "name": chapter.name, "description": chapter.description} for chapter in chapters]
        return jsonify(chapters)

    chapters = db.session.query(Chapter).filter(Chapter.subject_id == subject_id).all()
    chapter_list = [{"id":chapter.id, "name": chapter.name, "description": chapter.description} for chapter in chapters]
    return jsonify(chapter_list)




@app.route("/admin/search", methods = ["POST", "GET"])
@login_required
@admin_only
def search():
    search = request.form["search"]

    subjects = db.session.query(Subject).filter(Subject.name.like(f"%{search}%")).all()
    users = db.session.query(User).filter(User.full_name.like(f"%{search}%")).all()
    quizes = db.session.query(Chapter).join(Quiz, Chapter.id == Quiz.chapter_id).filter(Chapter.name.like(f"%{search}%")).all()


    return render_template("admin/search.html", subjects= subjects, users= users, quizes = quizes)








def question_count(chapter_id):
        question_count = db.session.query(db.func.count(Question.id)) \
                        .join(Quiz,Question.quiz_id == Quiz.id)\
                        .filter(Quiz.chapter_id == chapter_id) \
                        .scalar()
        
        return question_count


def get_chapters(subject_id):
    query = db.session.query(Chapter) \
            .filter(Chapter.subject_id == subject_id).all()
    chapters = [{"id":chapter.id, "name": chapter.name, "questions_count": question_count(chapter.id)} for chapter in query]
    return chapters


def get_questions(quiz_id):
    query = db.session.query(Question)\
            .filter(Question.quiz_id == quiz_id)
    questions = [{"id": question.id ,"question_statement": question.question_statement } for question in query]
    return questions
    