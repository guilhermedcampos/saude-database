#!/usr/bin/python3
# Copyright (c) BDist Development Team
# Distributed under the terms of the Modified BSD License.
import os
from logging.config import dictConfig

from flask import Flask, jsonify, request
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
import datetime

# Set timezone to Lisbon
os.environ["TZ"] = "Europe/Lisbon"

# Use the DATABASE_URL environment variable if it exists, otherwise use the default.
# Use the format postgres://username:password@hostname/database_name to connect to the database.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://saude:saude@postgres/saude")

pool = ConnectionPool(
	conninfo=DATABASE_URL,
	kwargs={
		"autocommit": True,  # If True don’t start transactions automatically.
		"row_factory": namedtuple_row,
	},
	min_size=4,
	max_size=10,
	open=True,
	# check=ConnectionPool.check_connection,
	name="postgres_pool",
	timeout=5,
)

dictConfig(
	{
		"version": 1,
		"formatters": {
			"default": {
				"format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
			}
		},
		"handlers": {
			"wsgi": {
				"class": "logging.StreamHandler",
				"stream": "ext://flask.logging.wsgi_errors_stream",
				"formatter": "default",
			}
		},
		"root": {"level": "INFO", "handlers": ["wsgi"]},
	}
)

app = Flask(__name__)
app.config.from_prefixed_env()
log = app.logger

# Check if a string is a decimal
def is_decimal(value):
	try:
		float(value)
		return True
	except ValueError:
		return False
	
def is_hour_before(hour1, hour2):
    hour1 = hour1.split(":")
    hour2 = hour2.split(":")[0:2]  # Only take the hours and minutes

    if int(hour1[0]) < int(hour2[0]):
        return True
    elif int(hour1[0]) == int(hour2[0]) and int(hour1[1]) < int(hour2[1]):
        return True
    else:
        return False
	
# Check if a string is a date
def is_date(value):
	try:
		datetime.datetime.strptime(value, '%Y-%m-%d')
		return True
	except ValueError:
		return False
	
# Check if a string is a time
def is_time(value):
	try:
		datetime.datetime.strptime(value, '%H:%M')
		return True
	except ValueError:
		return False

@app.route("/", methods=("GET",))
def get_clinics():
	"""Show all the accounts, most recent first."""
	clinics = []

	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					clinics = cur.execute("""SELECT nome, morada FROM clinica;""").fetchall()
					log.debug(f"Found {cur.rowcount} rows.")
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			else:
				log.debug("Showing all clinics.")
				return jsonify(clinics)


@app.route("/c/<clinic>/", methods=("GET",))
def get_specializations(clinic):
	"""Show all the specializations for a clinic."""

	# Check if the clinic exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM clinica WHERE nome = %s
					""", (clinic,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Clínica não encontrada.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
	
	# Get the list of specializations	
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT DISTINCT m.especialidade
						FROM medico m
						JOIN trabalha t ON m.nif = t.nif
						WHERE t.nome = %s;
					""", (clinic,))
					specializations = cur.fetchall()
					log.debug(f"Found {cur.rowcount} rows.")
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			else:
				log.debug(f"Showing all specializations for clinic {clinic}.")
				return jsonify(specializations)


@app.route('/c/<clinic>/<specialization>/', methods=("GET",))
def list_doctors(clinic, specialization):
	"""Show all the doctors for a clinic and specialization.
		Aditionally, show the 3 next available slots for each doctor.
	"""

	# Check if the clinic exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM clinica WHERE nome = %s
					""", (clinic,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Clínica não encontrada.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
	
	# Check if the specialization exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM medico WHERE especialidade = %s
					""", (specialization,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Especialidade não encontrada.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500

	# Get the list of doctors
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute('''
						SELECT m.nome
						FROM medico m
						JOIN trabalha t ON m.nif = t.nif
						WHERE t.nome = %s AND m.especialidade = %s
					''', (clinic, specialization))
					doctors = [row[0] for row in cur.fetchall()]

					# Initialize the result
					result = {doctor: [] for doctor in doctors}

					# Start from today
					date = datetime.date.today()

					# Loop until we have 3 slots for each doctor
					while any(len(slots) < 3 for slots in result.values()):
						cur.execute("""
						WITH possible_times (time) AS (
							VALUES ('08:00'::time), ('08:30'::time), ('09:00'::time), ('09:30'::time), 
								('10:00'::time), ('10:30'::time), ('11:00'::time), ('11:30'::time), 
								('12:00'::time), ('12:30'::time), ('14:00'::time), ('14:30'::time), 
								('15:00'::time), ('15:30'::time), ('16:00'::time), ('16:30'::time), 
								('17:00'::time), ('17:30'::time), ('18:00'::time), ('18:30'::time)
						),  doctor_times AS (
							SELECT m.nome, p.time
							FROM medico m
							JOIN trabalha t ON m.nif = t.nif
							CROSS JOIN possible_times p
							WHERE t.nome = %s AND m.especialidade = %s AND t.dia_da_semana = EXTRACT(ISODOW FROM %s::date)
						), existing_appointments as (
							Select m.nome, m.nif, c.data, c.hora
							FROM consulta c, medico m
							WHERE c.nif = m.nif AND c.data = %s AND m.especialidade = %s AND c.nome = %s
						), free_slots AS (
							SELECT dt.nome, dt.time,
								ROW_NUMBER() OVER(PARTITION BY dt.nome ORDER BY dt.time) AS rn
							FROM doctor_times dt
							LEFT JOIN existing_appointments ea ON dt.nome = ea.nome AND dt.time = ea.hora
							WHERE ea.nif IS NULL
						)
						SELECT nome, time
						FROM free_slots
						WHERE rn <= 3
						ORDER BY nome, time;
						""", (clinic, specialization, date, date, specialization, clinic))

						# Add the available slots to the result
						for nome, time in cur.fetchall():
							if len(result[nome]) < 3:
								result[nome].append((str(date), str(time)))

						# Go to the next day
						date += datetime.timedelta(days=1)
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			else:
				log.debug(f"Mostrando os 3 próximos horários disponíveis para os médicos da especialidade {specialization} na clínica {clinic}.")
				return jsonify(result)

@app.route("/a/<clinic>/registar/", methods=("POST",))
def create_consultation(clinic):
	"""Create a new consultation."""

	# Get the parameters from the request
	patient_ssn = request.args.get("paciente")
	doctor_nif = request.args.get("medico")
	date = request.args.get("data")
	time = request.args.get("hora")

	# Check if the parameters are present
	if not patient_ssn:
		return jsonify({"message": "SSN do paciente é obrigatório.", "status": "error"}), 400
	if not doctor_nif:
		return jsonify({"message": "NIF do médico é obrigatório.", "status": "error"}), 400
	if not date:
		return jsonify({"message": "Data é obrigatória.", "status": "error"}), 400
	if not time:
		return jsonify({"message": "Hora é obrigatória.", "status": "error"}), 400
	
	# Check if the parameters are in the correct format
	if not is_decimal(patient_ssn):
		return jsonify({"message": "SSN do paciente deve ser um número.", "status": "error"}), 400
	if not is_decimal(doctor_nif):
		return jsonify({"message": "NIF do médico deve ser um número.", "status": "error"}), 400
	if not is_date(date):
		return jsonify({"message": "Data deve estar no formato YYYY-MM-DD.", "status": "error"}), 400
	if not is_time(time):
		return jsonify({"message": "Hora deve estar no formato HH:MM.", "status": "error"}), 400

	# Check if the clinic exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM clinica WHERE nome = %s
					""", (clinic,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Clínica não encontrada.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			
	# Check if the patient exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM paciente WHERE ssn = %s
					""", (patient_ssn,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Paciente não encontrado.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500


	# Check if the doctor exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM medico WHERE nif = %s
					""", (doctor_nif,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Médico não encontrado.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
	
	cur_time = str(datetime.datetime.now().time())
	# Check if date is in the future or today in a future time
	if date < str(datetime.date.today()):
		return jsonify({"message": "Não é possível marcar consultas em datas passadas.", "status": "error"}), 400
	elif date == str(datetime.date.today()) and is_hour_before(time, cur_time):
		return jsonify({"message": f"Não é possível marcar consultas em horas passadas.", "status": "error"}), 400

	# Insert the consultation
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					# Fetch the highest value of codigo_sns
					cur.execute("""
						SELECT codigo_sns FROM consulta ORDER BY codigo_sns DESC LIMIT 1
					""")
					last_codigo_sns = cur.fetchone()
				
					# Increment the codigo_sns
					next_codigo_sns = str(int(last_codigo_sns[0]) + 1)
					
					# Ensure the codigo_sns has 12 digits by adding leading zeros if necessary
					next_codigo_sns = next_codigo_sns.zfill(12)
				
					# Insert the new consultation with the incremented codigo_sns
					cur.execute("""
						INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns)
						VALUES (%s, %s, %s, %s, %s, %s)
					""", (patient_ssn, doctor_nif, clinic, date, time, next_codigo_sns))
				
			except Exception as e:
				error_message = str(e)
				if "violates check constraint" in error_message:
					if "chk_clinic_workday" in error_message:
						return jsonify({"message": "O médico não trabalha nessa clínica nesse dia da semana.", "status": "error"}), 400
					elif "chk_doctor_patient" in error_message:
						return jsonify({"message": "O médico não pode marcar uma consulta a si mesmo.", "status": "error"}), 400
					elif "chk_appointment_hour" in error_message:
						return jsonify({"message": "Não é possível marcar consultas a essa hora: Os horários das consultas são à hora exata ou meia-hora no horário 8-13h e 14-19h.", "status": "error"}), 400
				elif "duplicate key value violates unique constraint" in error_message:
					return jsonify({"message": "Já existe uma consulta marcada para essa data e hora.", "status": "error"}), 400
				else:
					return jsonify({"message": "Erro ao marcar consulta.", "status": "error"}), 500
			else:
				log.debug(f"Consulta marcada para {date} às {time} com o médico {doctor_nif} para o paciente {patient_ssn}")
				return jsonify({"consulta marcada": f"{date} às {time} com o médico {doctor_nif} para o paciente {patient_ssn}", "status": "success"}), 201

@app.route("/a/<clinic>/cancelar/", methods=("POST",))
def cancel_consultation(clinic):
	"""Cancel a consultation."""

	# Get the parameters from the request
	patient_ssn = request.args.get("paciente")
	doctor_nif = request.args.get("medico")
	date = request.args.get("data")
	time = request.args.get("hora")

	# Check if the parameters are present
	if not patient_ssn:
		return jsonify({"message": "SSN do paciente é obrigatório.", "status": "error"}), 400
	if not doctor_nif:
		return jsonify({"message": "NIF do médico é obrigatório.", "status": "error"}), 400
	if not date:
		return jsonify({"message": "Data é obrigatória.", "status": "error"}), 400
	if not time:
		return jsonify({"message": "Hora é obrigatória.", "status": "error"}), 400
	
	# Check if the parameters are in the correct format
	if not is_decimal(patient_ssn):
		return jsonify({"message": "SSN do paciente deve ser um número.", "status": "error"}), 400
	if not is_decimal(doctor_nif):
		return jsonify({"message": "NIF do médico deve ser um número.", "status": "error"}), 400
	if not is_date(date):
		return jsonify({"message": "Data deve estar no formato YYYY-MM-DD.", "status": "error"}), 400
	if not is_time(time):
		return jsonify({"message": "Hora deve estar no formato HH:MM.", "status": "error"}), 400

	# Check if the clinic exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM clinica WHERE nome = %s
					""", (clinic,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Clínica não encontrada.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			
	# Check if the patient exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM paciente WHERE ssn = %s
					""", (patient_ssn,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Paciente não encontrado.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			
	# Check if the doctor exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM medico WHERE nif = %s
					""", (doctor_nif,))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Médico não encontrado.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
	
	cur_time = str(datetime.datetime.now().time())
	# Check if the consultation is in the future
	if date < str(datetime.date.today()):
		return jsonify({"message": "Não é possível cancelar consultas em datas passadas.", "status": "error"}), 400
	elif date == str(datetime.date.today()) and is_hour_before(time, cur_time):
		return jsonify({"message": f"Não é possível cancelar consultas em horas passadas.", "status": "error"}), 400
	
	# Check if the consultation exists
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						SELECT COUNT(*) FROM consulta WHERE ssn = %s AND nif = %s AND nome = %s AND data = %s AND hora = %s
					""", (patient_ssn, doctor_nif, clinic, date, time))
					if cur.fetchone()[0] == 0:
						return jsonify({"message": "Consulta não encontrada.", "status": "error"}), 404
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
		
	# Delete the consultation
	with pool.connection() as conn:
		with conn.cursor() as cur:
			try:
				with conn.transaction():
					cur.execute("""
						DELETE FROM consulta
						WHERE ssn = %s AND nif = %s AND nome = %s AND data = %s AND hora = %s
					""", (patient_ssn, doctor_nif, clinic, date, time))
				
			except Exception as e:
				return jsonify({"message": str(e), "status": "error"}), 500
			else:
				log.debug(f"Consulta cancelada para {date} às {time} com o médico {doctor_nif} para o paciente {patient_ssn}")
				return jsonify({"consulta cancelada": f"{date} às {time} com o médico {doctor_nif} para o paciente {patient_ssn}", "status": "success"}), 201

@app.route("/ping", methods=("GET",))
def ping():
	log.debug("ping!")
	return jsonify({"message": "pong!", "status": "success"})

if __name__ == "__main__":
	app.run(port=5001)