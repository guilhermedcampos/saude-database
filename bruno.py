from flask import Flask, request, jsonify
import psycopg2
import datetime

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname='saude',  # Update to your database name
        user='saude',    # Update to your database user
        password='saude',  # Update to your database password
        host = 'localhost',  # Update to your database host
        port='5432'      # Update to your database port
    )
    return conn

@app.route('/')
def list_clinics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nome, morada FROM clinica;')
    clinics = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(clinics)

@app.route('/c/<clinic>/')
def list_specialties(clinic):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT m.especialidade
        FROM medico m
        JOIN trabalha t ON m.nif = t.nif
        WHERE t.nome = %s;
    ''', (clinic,))
    specialties = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(specialties)

@app.route('/c/<clinic>/<specialty>/')
def list_doctors(clinic, specialty):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the list of doctors
    cursor.execute('''
        SELECT m.nome
        FROM medico m
        JOIN trabalha t ON m.nif = t.nif
        WHERE t.nome = %s AND m.especialidade = %s
    ''', (clinic, specialty))
    doctors = [row[0] for row in cursor.fetchall()]

    # Initialize the result
    result = {doctor: [] for doctor in doctors}

    # Start from today
    date = datetime.date.today()

    # Loop until we have 3 slots for each doctor
    while any(len(slots) < 3 for slots in result.values()):
        cursor.execute('''
            WITH possible_times (time) AS (
                VALUES ('08:00'::time), ('08:30'::time), ('09:00'::time), ('09:30'::time), 
                       ('10:00'::time), ('10:30'::time), ('11:00'::time), ('11:30'::time), 
                       ('12:00'::time), ('12:30'::time), ('14:00'::time), ('14:30'::time), 
                       ('15:00'::time), ('15:30'::time), ('16:00'::time), ('16:30'::time), 
                       ('17:00'::time), ('17:30'::time), ('18:00'::time), ('18:30'::time)
            ), doctor_times AS (
                SELECT m.nome, p.time
                FROM medico m
                JOIN trabalha t ON m.nif = t.nif
                CROSS JOIN possible_times p
                WHERE t.nome = %s AND m.especialidade = %s AND t.dia_da_semana = EXTRACT(ISODOW FROM %s::date)
            ), numbered_available_times AS (
                SELECT dt.nome, dt.time,
                    ROW_NUMBER() OVER(PARTITION BY dt.nome ORDER BY dt.time) AS rn
                FROM doctor_times dt
                LEFT JOIN consulta c ON dt.nome = c.nome AND dt.time = c.hora AND c.data = %s
                WHERE c.nome IS NULL
            )
            SELECT nome, time
            FROM numbered_available_times
            WHERE rn <= 3
            ORDER BY nome, time;
        ''', (clinic, specialty, date, date))

        # Add the available slots to the result
        for nome, time in cursor.fetchall():
            if len(result[nome]) < 3:
                result[nome].append((date, time))

        # Go to the next day
        date += datetime.timedelta(days=1)

    cursor.close()
    conn.close()

    return jsonify(result)

@app.route('/a/<clinic>/registar/', methods=['POST'])
def register_consultation(clinic):
    data = request.json
    ssn = data['ssn']
    nif = data['nif']
    data_consulta = data['data']
    hora_consulta = data['hora']
    codigo_sns = data.get('codigo_sns', None)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    ''', (ssn, nif, clinic, data_consulta, hora_consulta, codigo_sns))
    consulta_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'consulta_id': consulta_id})

@app.route('/a/<clinic>/cancelar/', methods=['POST'])
def cancel_consultation(clinic):
    data = request.json
    ssn = data['ssn']
    data_consulta = data['data']
    hora_consulta = data['hora']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM consulta
        WHERE ssn = %s AND nome = %s AND data = %s AND hora = %s
        RETURNING id;
    ''', (ssn, clinic, data_consulta, hora_consulta))
    consulta_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if consulta_id:
        return jsonify({'consulta_id': consulta_id[0]})
    else:
        return jsonify({'error': 'Consulta not found or cannot be canceled.'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)