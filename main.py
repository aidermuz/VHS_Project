from datetime import timedelta

from flask import Flask, render_template, redirect, request, url_for, session
from flask_mysqldb import MySQL, MySQLdb

from form import about, home, auth, admin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

mysql = MySQL(app)


def create_connection(host, user, password, db):
    connection = False
    try:
        app.config['MYSQL_HOST'] = host
        app.config['MYSQL_USER'] = user
        app.config['MYSQL_PASSWORD'] = password
        app.config['MYSQL_DB'] = db
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        print("Connection to MySQL DB successful")
        connection = True
        return connection

    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e

# connect_db = create_connection('Prizmax.mysql.pythonanywhere-services.com', 'Prizmax', 'bobrenock08', 'Prizmax$VHS_Project')
connect_db = create_connection('localhost', 'root', 'bobrenock08', 'VHS_Project_db')

app.add_url_rule('/', view_func=home.index)

app.add_url_rule('/about', view_func=about.about)

# Auth forms
app.add_url_rule('/login', methods=['GET', 'POST'], view_func=auth.login)
app.add_url_rule('/logout', view_func=auth.logout)
app.add_url_rule('/register', methods=['GET', 'POST'], view_func=auth.register)


# Admin panel
app.add_url_rule('/admin', methods=['GET', 'POST'], view_func=admin.admin)


@app.route('/rental', methods=['GET', 'POST'])
def rental():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "select * from genre, movie where movie.genre_idGenre = genre.idGenre and movie.status = 'Можно взять в прокат'")
    movie = cursor.fetchall()
    return render_template("rental.html", movie=movie)


@app.route('/payment/<idMovie>', methods=['GET', 'POST'])
def payment(idMovie):
    if not session.get("username"):
        return redirect("/login")
    if session["username"] == 'admin':
        return redirect('/payment/<idMovie>')
    msg = ''
    cursor = mysql.connection.cursor()
    cursor.execute(f"select status from movie where idMovie={idMovie}")
    status = cursor.fetchone()
    cursor.execute(f"SELECT nameMovie FROM movie WHERE idMovie={idMovie}")
    movie = cursor.fetchone()

    if status['status'] == 'в прокате':
        return redirect(url_for('rental'))

    if request.method == 'POST':
        f = request.form['name']
        l = request.form['lname']
        p = request.form['phone']
        e = request.form['email']
        chkin = request.form['checkIn']
        chkout = request.form['checkOut']
        if chkin > chkout:
            msg = 'Укажите дату верно'
        else:
            try:
                cursor.execute(f'''INSERT INTO `guest` (`fname`, `lname`, `phone`, `email`, `checkIn`, `checkOut`) 
                VALUES ('{f}', '{l}', '{p}', '{e}', '{chkin}', '{chkout}')''')
                cursor.execute(f"SELECT idMovie FROM movie WHERE idMovie={idMovie}")
                id = cursor.fetchone()
                cursor.execute(f'''UPDATE `movie` SET status = 'busy' where idMovie='{id["idMovie"]}' ''')
                mysql.connection.commit()
            except:
                msg = 'Данные неверны'
    cursor.close()
    return render_template('payment.html', msg=msg, movie=movie)


@app.route('/reviews')
def reviews():
    return render_template("reviews.html")


@app.route('/help')
def help():
    return render_template("help.html")


if __name__ == "__main__":
    app.run(debug=True)
