from flask import Flask, request, jsonify
import psycopg2

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
    cursor.execute('''
        SELECT m.nome, t.dia_da_semana, MIN(c.data) AS proxima_data, MIN(c.hora) AS proxima_hora
        FROM medico m
        JOIN trabalha t ON m.nif = t.nif
        LEFT JOIN consulta c ON m.nif = c.nif AND t.nome = c.nome AND t.dia_da_semana = EXTRACT(ISODOW FROM c.data)
        WHERE t.nome = %s AND m.especialidade = %s
        GROUP BY m.nome, t.dia_da_semana
        ORDER BY m.nome, t.dia_da_semana;
    ''', (clinic, specialty))
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(doctors)

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