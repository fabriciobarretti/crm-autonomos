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

daysOfTheWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_next_sessions(clients):
    currentDate = date.today()
    nextSessions = []

    # Busca todos os clientes e coloca algumas informações na variável nextSessions
    for i, client in enumerate(clients):
        if client['dayofthesession'] in daysOfTheWeek:
            #Transforma o nome do dia em número da semana
            dayOfTheSession = daysOfTheWeek.index(client['dayofthesession'])
            nextSessions.append({'id': client['id'], 'name': client['name'], 'dayofthesession': dayOfTheSession, 'sessiontime': client['sessiontime']})
        else:
            print("Invalid date.")
    
    # Ordena primeiramente por dia da sessão e, depois, por horário da sessão
    nextSessions.sort(key=lambda x: (x['dayofthesession'], x['sessiontime']))
    
    # print(nextSessions)
    # print(daysOfTheWeek[currentDate.weekday()])
    return nextSessions if nextSessions else None

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    nextSessions = get_next_sessions(clients)
    return render_template('index.html', clients=clients, nextSessions=nextSessions, daysOfTheWeek=daysOfTheWeek)

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
    
    return render_template('edit.html', client=client, daysOfTheWeek=daysOfTheWeek)

@app.route('/delete/<int:id>')
def delete_client(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM clients WHERE id = %s', (id,))
    mysql.connection.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)