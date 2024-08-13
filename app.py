from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import date
from datetime import datetime
import MySQLdb.cursors

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'CRUD2023'
app.config['MYSQL_DB'] = 'clients_db'

mysql = MySQL(app)

daysOfTheWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def parse_time(time_string):
    return datetime.strptime(time_string, "%H:%M").time()

def get_next_sessions(clients):
    currentDate = date.today()
    currentDateIndex = currentDate.weekday()
    currentTime = datetime.now().time()
    nextSessions = []

    # Busca todos os clientes e coloca algumas informações na variável nextSessions
    for i, client in enumerate(clients):
        if client['dayofthesession'] in daysOfTheWeek:
            #Transforma o nome do dia em número da semana
            dayOfTheSession = daysOfTheWeek.index(client['dayofthesession'])
            adjustedDay = (dayOfTheSession - currentDateIndex) % 7
            sessionTime = parse_time(client['sessiontime'])

            sessionHasPassed = (adjustedDay == 0 and sessionTime < currentTime)
            sortKey = (sessionHasPassed, adjustedDay, sessionTime)
    

            nextSessions.append({'id': client['id'], 'name': client['name'], 'adjustedDay': adjustedDay, 'dayofthesession': dayOfTheSession, 'sessiontime': sessionTime, 'sortKey': sortKey})
        else:
            print("Invalid date.")
    
    # Ordena primeiramente por dia da sessão e, depois, por horário da sessão
    nextSessions.sort(key=lambda x: (x['sortKey']))
    
    return nextSessions if nextSessions else None

def get_next_payments(clients):
    currentDate = date.today()
    currentDayOfTheMonth = currentDate.day
    nextPayments = []

    for i, client in enumerate(clients):
        adjustedPayday = (client['payday'] - currentDayOfTheMonth) % 31

        nextPayments.append({'id': client['id'], 'name': client['name'], 'adjustedPayday': adjustedPayday, 'payday': client['payday'], 'packagePrice': client['packageprice']})

    nextPayments.sort(key=lambda x: (x['adjustedPayday'], x['packagePrice'], x['name']))

    return nextPayments if nextPayments else None
        

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    nextSessions = get_next_sessions(clients)
    nextPayments = get_next_payments(clients)
    
    return render_template('index.html', clients=clients, nextSessions=nextSessions, nextPayments = nextPayments, daysOfTheWeek=daysOfTheWeek)

@app.route('/clients')
def clients():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()    
    return render_template('clients.html', clients=clients)

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