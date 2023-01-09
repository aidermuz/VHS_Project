from flask import Flask, render_template, session, redirect, request

from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)


def admin():
    if session['username'] != 'admin':
        return redirect('/')
    cursor = mysql.connection.cursor()
    msg = ''
    msgr = ''
    if request.method == 'POST' and 'movie' in request.form and 'status' in request.form and 'genre' in request.form \
            and 'img' in request.form and 'description' in request.form and 'price' in request.form:
        mov = request.form['movie']
        status = request.form['status']
        rtype = request.form['genre']
        image = request.form['img']
        desc = request.form['description']
        pr = request.form['price']
        print(mov, status, rtype, image, desc, pr)
        try:
            cursor.execute(f"SELECT * FROM movie WHERE nameMovie='{mov}' ")
            x = cursor.fetchone()
            print(x)
            if x is None:
                cursor.execute(f'''INSERT INTO `genre` (`description`, `price`, `img`, `genre`) 
                                        VALUES ('{desc}', '{pr}', '{image}', '{rtype}')''')
                cursor.execute(f'''SELECT idGenre FROM `genre` WHERE description = '{desc}' ''')
                idg = cursor.fetchone()
                cursor.execute(f'''INSERT INTO `movie` (`nameMovie`, `status`, `Genre_idGenre`) 
                           VALUES ('{mov}', '{status}', '{idg['idGenre']}')''')
                mysql.connection.commit()
                msgr = 'Фильм успешно создан'
            elif x['nameMovie'] == mov:
                msg = 'Такой Фильм уже существует'
        except(Exception,):
            msg = 'Данные неверны'

    cursor.execute(f"SELECT * FROM guest")
    guest = cursor.fetchall()
    return render_template('admin.html', msg=msg, msgr=msgr, guest=guest)
