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
    if request.method == 'POST' and 'number' in request.form and 'status' in request.form and 'genre' in request.form:
        num = request.form['number']
        status = request.form['status']
        rtype = request.form['genre']
        print(num, status, rtype)
        try:
            cursor.execute(f"SELECT * FROM Movies WHERE saleNumber={num}")
            x = cursor.fetchone()
            if x is None:
                cursor.execute(f'''INSERT INTO `Movies` (`saleNumber`, `status`, `Genre_idGenre`) 
                                VALUES ('{num}', '{status}', '{rtype}')''')
                mysql.connection.commit()
                msgr = 'Фильм успешно создан'
            elif x['saleNumber'] == int(num):
                msg = 'Такой Фильм уже существует'
        except(Exception,):
            msg = 'Данные неверны'

    cursor.execute(f"SELECT * FROM guest")
    guest = cursor.fetchall()
    return render_template('admin.html', msg=msg, msgr=msgr, guest=guest)
