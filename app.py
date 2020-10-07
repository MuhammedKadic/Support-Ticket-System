from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import flask_sijax
import socket
import psutil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticket_fixed.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

flask_sijax.Sijax(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    messages = db.Column(db.String(50), nullable=False)
    archive = db.Column(db.String(50), nullable=False)


class Replies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    associationID = db.Column(db.Integer, nullable=False)
    replyee = db.Column(db.String(50), nullable=False)
    replyMessage = db.Column(db.String(500), nullable=False)
    replyTime = db.Column(db.String(50), nullable=False)
    ReplyDate = db.Column(db.String(50), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    rank = db.Column(db.Integer, nullable=False)


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
today = date.today()


@app.route('/', methods=['GET', 'POST'])
def index():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return render_template('index.html', current_time=current_time, today=today, ipaddress=IPAddr, cpu=cpu, memory=memory)


@app.route('/edit_ticket/<id>', methods=['GET', 'POST'])
def edit(id):
    found_ticket = Ticket.query.filter_by(id=id).first()
    if found_ticket.name == session['username'] or session['rank'] == 5:
        if request.method == "POST":
            association_ID = id
            user_replying = session['username']
            reply_message = request.form.get('reply_area')
            reply_time = current_time
            reply_date = today
            newReplyObject = Replies(associationID=association_ID,
                                     replyee=user_replying,
                                     replyMessage=reply_message,
                                     replyTime=reply_time,
                                     ReplyDate=reply_date)

            db.session.add(newReplyObject)
            db.session.commit()
            return redirect(id)
        else:
            pass

        if request.method == 'GET':
            found_replies = Replies.query.filter_by(associationID=id)
            reply_data = []

            for reply in found_replies:
                submitted_replies = {
                    'id': reply.id,
                    'assoid': reply.associationID,
                    'replyee': reply.replyee,
                    'replymessage': reply.replyMessage,
                    'replytime': reply.replyTime,
                    'replydate': reply.ReplyDate
                }

                reply_data.append(submitted_replies)

        if found_ticket:
            return render_template('admin/edit_ticket.html',
                                   id=found_ticket.id, name=found_ticket.name,
                                   priority=found_ticket.priority,
                                   subject=found_ticket.subject,
                                   email=found_ticket.email,
                                   messages=found_ticket.messages,
                                   archive=found_ticket.archive, reply_data=reply_data)
        else:
            pass
    else:
        return redirect(url_for('index'))

    return render_template('admin/edit_ticket.html')


@app.route('/delete_ticket/<id>')
def delete(id):
    found_ticket = Ticket.query.filter_by(id=id).first()
    found_replies = Replies.query.filter_by(associationID=id)
    if found_ticket:
        if found_replies:
            for blank in found_replies:
                db.session.delete(blank)
            db.session.delete(found_ticket)
            db.session.commit()
        else:
            db.session.delete(found_ticket)
            db.session.commit()
        if session['rank'] == 5:
            return redirect(url_for('tickets'))
        else:
            return redirect(url_for('mytickets'))
    else:
        pass
    return render_template('delete.html')


@app.route('/edit_user/<id>', methods=['GET', 'POST'])
def edit_user(id):
    found_user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        form_username = request.form.get('username')
        form_email = request.form.get('email')
        form_id = request.form.get('rank')
        flash('Successfully updated this user\'s profile.')
        found_user.username = form_username
        found_user.email = form_email
        found_user.rank = form_id
        session['username'] = form_username
        session['email'] = form_email
        session['rank'] = form_id
        db.session.commit()
    return render_template('admin/edit_user.html', username=found_user.username,
                           id=found_user.id,
                           email=found_user.email,
                           rank=found_user.rank)


@app.route('/archive/<id>')
def archive(id):
    return render_template('archive.html')


@app.route('/mytickets')
def mytickets():
    if 'username' and 'email' in session:
        tickets = Ticket.query.filter_by(email=session['email'])
        ticket_data = []

        for ticket in tickets:
            submitted_ticket = {
                'id': ticket.id,
                'name': ticket.name,
                'priority': ticket.priority,
                'subject': ticket.subject,
                'email': ticket.email,
                'messages': ticket.messages,
                'archive': ticket.archive

            }

            ticket_data.append(submitted_ticket)

    return render_template('mytickets.html', ticket_data=ticket_data)


@app.route('/tickets')
def tickets():
    if session['rank'] == 5:
        tickets = Ticket.query.all()

        ticket_data = []

        for ticket in tickets:
            submitted_ticket = {
                'id': ticket.id,
                'name': ticket.name,
                'priority': ticket.priority,
                'subject': ticket.subject,
                'email': ticket.email,
                'messages': ticket.messages,
                'archive': ticket.archive

            }

            ticket_data.append(submitted_ticket)
    else:
        return redirect(url_for('index'))
    return render_template('admin/tickets.html', gettickets=ticket_data)


@app.route('/users')
def users():
    if session['rank'] == 5:
        users = User.query.all()

        user_data = []

        for user in users:
            current_users = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'rank': user.rank
            }
            user_data.append(current_users)
    else:
        return redirect(url_for('index'))
    return render_template('admin/users.html', get_users=users)


@app.route('/admin')
def admin():
    if session['rank'] == 5:
        pass
    else:
        return redirect(url_for('index'))
    return render_template('admin.html', username=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if "username" and "email" in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        form_email = request.form.get('email')
        form_password = request.form.get('password')
        found_user = User.query.filter_by(email=form_email).first()
        if found_user:
            if bcrypt.check_password_hash(found_user.password, form_password):
                session['username'] = found_user.username
                session['email'] = found_user.email
                session['rank'] = found_user.rank
                return redirect(url_for('index'))
            else:
                flash("Password or email does not match. Please try again.")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if "username" and "email" in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        error = None
        accountUsername = request.form.get('username')
        accountEmail = request.form.get('email')
        accountPassword = request.form.get('password')
        accountConfirmPass = request.form.get('ConfirmPassword')
        accountRank = '1'

        pw_hash = bcrypt.generate_password_hash(accountPassword)
        newAccountObject = User(username=accountUsername,
                                email=accountEmail, password=pw_hash, rank='1')
        print(newAccountObject)
        if User.query.filter_by(username=accountUsername).first():
            flash('Please use a unique username')
        elif User.query.filter_by(email=accountEmail).first():
            flash('Please make sure you use a unique email address.')
        elif accountPassword != accountConfirmPass:
            flash('Please make sure the passwords match.')
        else:
            session['username'] = accountUsername
            session['email'] = accountEmail
            session['rank'] = accountRank
            db.session.add(newAccountObject)
            db.session.commit()
            return redirect(url_for('register_success'))
    return render_template('register.html')


@app.route('/register_success', methods=['GET', 'POST'])
def register_success():
    if 'username' and 'email' in session:
        username = session['username']
        email = session['email']
        rank = session['rank']
    else:
        return redirect(url_for('login'))
    return render_template('register_success.html', username=username, email=email, rank=rank)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('rank', None)

    session.pop('password', None)
    return redirect(url_for('register_success'))


@app.route('/newticket', methods=['GET', 'POST'])
def newticket():
    if request.method == "POST":
        new_name = session['username']
        new_email = session['email']

        new_priority = request.form.get('priority_level')
        string_value = str(new_priority)
        new_subject = request.form.get('subject')
        new_message = request.form.get('message')
        archive = False

        new_ticket_obj = Ticket(name=new_name, priority=string_value, subject=new_subject,
                                email=new_email, messages=new_message, archive=archive)
        print(new_ticket_obj)
        db.session.add(new_ticket_obj)
        db.session.commit()
        return redirect(url_for('submittedticket'))
    return render_template('newticket.html')


@app.route('/submitted-ticket')
def submittedticket():
    return render_template('thank_you.html')


if __name__ == '__main__':
    app.run(debug=True)
