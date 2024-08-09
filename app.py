from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import date
import MySQLdb.cursors

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'CRUD2023'
app.config['MYSQL_DB'] = 'clients_db'

mysql = MySQL(app)

def get_next_sessions(clients):
    currentDay = date.today()
    nextSessions = []

    for i, client in enumerate(clients):
        nextSessions.append({'id': client['id'], 'name': client['name'], 'dayofthesession': client['dayofthesession']})
                        
    print(nextSessions)
    return clients if clients else None

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    print(type(clients))
    get_next_sessions(clients)
    return render_template('index.html', clients=clients)

@app.route('/add', methods=['POST'])
def add_client():
    name = request.form['name']
    birthdate = request.form['birthdate']
    dayOfTheSession = request.form['dayofthesession']
    sessionTime = request.form['sessiontime']
    packagePrice = request.form['packageprice']
    payDay = request.form['payday']

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO clients (name, birthdate, dayofthesession, sessiontime, packageprice, payday) VALUES (%s, %s, %s, %s, %s, %s)', (name, birthdate, dayOfTheSession, sessionTime, packagePrice, payDay))
    mysql.connection.commit()

    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']
        dayOfTheSession = request.form['dayofthesession']
        sessionTime = request.form['sessiontime']
        packagePrice = request.form['packageprice']
        payDay = request.form['payday']

        cursor.execute('UPDATE clients SET name=%s, birthdate=%s, dayofthesession=%s, sessiontime=%s, packageprice=%s, payday=%s WHERE id=%s', (name, birthdate, dayOfTheSession, sessionTime, packagePrice, payDay, id))
        mysql.connection.commit()
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM clients WHERE id = %s', (id,))
    client = cursor.fetchone()
    print(client)
    daysOfTheWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return render_template('edit.html', client=client, daysOfTheWeek=daysOfTheWeek)

@app.route('/delete/<int:id>')
def delete_client(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM clients WHERE id = %s', (id,))
    mysql.connection.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)