import random
from datetime import date, timedelta

# Function to generate random date of birth
def random_date(start, end):
	return start + timedelta(days=random.randint(0, (end - start).days))

# 5 Clinics
clinics = []
clinics.append(('Clinica Cascais', '214123456', 'Rua da Clinica Cascais, 2750-123 Cascais'))
clinics.append(('Clinica Amadora', '213123456', 'Rua da Clinica Amadora, 1000-123 Lisboa'))
clinics.append(('Clinica Loures', '226123456', 'Rua da Clinica Loures, 1685-015 Loures'))
clinics.append(('Clinica Oeiras', '289123456', 'Rua da Clinica Oeiras, 2780-175 Oeiras'))
clinics.append(('Clinica Carcavelos', '253123456', 'Rua da Clinica Carcavelos, 2775-123 Carcavelos'))

# 5 Nurses per Clinic
nurses = []
for i, x in enumerate(clinics):
	for day in range(1, 6):
		nif = str(i * 5 + day + 248102125).zfill(9)
		name = f'Nurse {day} {x[0]}'
		phone = str(i * 5 + day + 968825161).zfill(9)
		address = f'Rua do Enfermeiro {i * 5 + day}, 2780-015 Oeiras'
		clinic = x[0]
		nurses.append((nif, name, phone, address, clinic))
print("Nurses generated.")

# 60 Medics
medics = []
# 20 Medics with speciality "clinica geral"
for i in range(1, 21):
	nif = str(i + 167879014).zfill(9)
	name = f'Medic {i}'
	phone = str(i + 926114778).zfill(9)
	address = f'Rua do Medico {i}, 2780-015 Oeiras'
	speciality = "clinica geral"
	medics.append((nif, name, phone, address, speciality))
# 40 medics with random speciality
for i in range(21, 61):
	nif = str(i + 167879014).zfill(9)
	name = f'Medic {i}'
	phone = str(i + 926114778).zfill(9)
	address = f'Rua do Medico {i}, 2780-015 Oeiras'
	speciality = random.choice(["cardiologia", "pediatria", "cardiologia", "oftalmologia", "ortopedia"])
	medics.append((nif, name, phone, address, speciality))
# random.shuffle(medics)
print("Medics generated.")

# 420 Work Orders
work_orders = []
for group in range(5):
	for weekday in range(7):
		for medic in range(12):
			clinic = (group + weekday) % 5
			work_order = (medics[group * 12 + medic][0], clinics[clinic][0], weekday + 1)
			work_orders.append(work_order)
print("Work Orders generated.")

# 5000 Patients
patients = []
for i in range(1, 5001):
	ssn = str(i + 11932603870).zfill(11)
	nif = str(i + 273279432).zfill(9)
	name = f'Little John {i}'
	phone = str(i + 918115714).zfill(9)
	address = f'Rua Sao Vicente {i}, 2750-123 Cascais'
	dob = random_date(date(1980, 1, 1), date(2020, 12, 31)).strftime('%Y-%m-%d')
	patients.append((ssn, nif, name, phone, address, dob))
print("Patients generated.")

# Receives a medic NIF and a date and where the medic is working that day
def get_clinic(NIF: int, date: date):
	for work_order in work_orders:
		if work_order[0] == NIF and work_order[2] == date.weekday() + 1:
			return work_order[1]
	return None

# 87720 Appointments
appointments = []
sns_code = 1
start_date = date(2023, 1, 1)
end_date = date(2024, 12, 31)
delta = timedelta(days=1)
current_date = start_date
while current_date <= end_date:
	for medic in range(60):
		clinic = get_clinic(medics[medic][0], current_date)
		hour = random.sample([f"{h}:00" for h in range(8, 19) if h != 13] + [f"{h}:30" for h in range(8, 19) if h != 13], 2)
		appointment1 = (patients[(sns_code - 1) % 5000][0], medics[medic][0], clinic, current_date.strftime('%Y-%m-%d'), hour[0], sns_code)
		sns_code += 1
		appointment2 = (patients[(sns_code - 1) % 5000][0], medics[medic][0], clinic, current_date.strftime('%Y-%m-%d'), hour[1], sns_code)
		sns_code += 1
		appointments.append(appointment1)
		appointments.append(appointment2)
		
	current_date += delta
print("Appointments generated.")

# 70176 Appointments with Perscriptions
medications = ["Paracetamol", "Ibuprofeno", "Aspirina", "Benadril", "Ritalina", "Prozac"]
perscriptions = []

for i in range(70176):
	appointment_sns_code = appointments[i][5]
	number_of_medications = random.randint(1, 6)
	for medication in random.sample(medications, number_of_medications):
		quantity = random.randint(1, 3)
		perscriptions.append((appointment_sns_code, medication, quantity))
print("Perscriptions generated.")

# Symptoms
symptoms = [f"Symptom {i}" for i in range(1, 51)]
metrics = ["pressão diastólica"] + [f"Metric {i}" for i in range(1, 20)]
# 87720 Appointments with Observations
observations = []
for i, appointment in enumerate(appointments):
	num_symptoms = random.randint(1, 5)
	num_metrics = random.randint(0, 3)
	for symptom in random.sample(symptoms, num_symptoms):
		observations.append((appointment[5], symptom, None))
	for metric in random.sample(metrics, num_metrics):
		value = random.randint(1, 100)
		observations.append((appointment[5], metric, value))
print("Observations generated.")

# Open a file to write SQL commands
with open("populate.sql", "w", encoding="utf-8") as file:
	# Write 5 Clinics
	file.write("INSERT INTO clinica (nome, telefone, morada) VALUES\n")
	for i, clinic in enumerate(clinics):
		name, phone, address = clinic
		sql = f"	('{name}', '{phone}', '{address}')"
		sql += "," if i < 4 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Clinics inserted.")

	# Write 25 Nurses
	file.write("INSERT INTO enfermeiro (nif, nome, telefone, morada, nome_clinica) VALUES\n")
	for i, nurse in enumerate(nurses):
		nif, name, phone, address, clinic = nurse
		sql = f"	('{nif}', '{name}', '{phone}', '{address}', '{clinic}')"
		sql += "," if i < 24 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Nurses inserted.")

	# Write 60 Medics
	file.write("INSERT INTO medico (nif, nome, telefone, morada, especialidade) VALUES\n")
	for i, medic in enumerate(medics):
		nif, name, phone, address, speciality = medic
		sql = f"	('{nif}', '{name}', '{phone}', '{address}', '{speciality}')"
		sql += "," if i < 59 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Medics inserted.")

	# Write 420 Work Orders
	file.write("INSERT INTO trabalha (nif, nome, dia_da_semana) VALUES\n")
	for i, works in enumerate(work_orders):
		medic, clinic, day = works
		sql = f"	('{medic}', '{clinic}', {day})"
		sql += "," if i < 419 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Work Orders inserted.")

	# Write 5000 Patients
	file.write("INSERT INTO paciente (ssn, nif, nome, telefone, morada, data_nasc) VALUES\n")
	for i, patient in enumerate(patients):
		ssn, nif, name, phone, address, dob = patient
		sql = f"	('{ssn}', '{nif}', '{name}', '{phone}', '{address}', '{dob}')"
		sql += "," if i < 4999 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Patients inserted.")

	# Write 87720 Appointments
	file.write("INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns) VALUES\n")
	for i, appointment in enumerate(appointments):
		ssn, nif, clinic, day, hour, sns_code = appointment
		sns_code_str = str(sns_code).zfill(12)
		sql = f"	('{ssn}', '{nif}', '{clinic}', '{day}', '{hour}', '{sns_code_str}')"
		sql += "," if i < 87719 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Appointments inserted.")

	# Write Percriptions for 70176 Appointments
	file.write("INSERT INTO receita (codigo_sns, medicamento, quantidade) VALUES\n")
	for i, perscription in enumerate(perscriptions):
		appointment_sns_code, medication, quantity = perscription
		sns_code_str = str(appointment_sns_code).zfill(12)
		sql = f"	('{sns_code_str}', '{medication}', {quantity})"
		sql += "," if i < len(perscriptions) - 1 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Perscriptions inserted.")

	# Write Observations for 87720 Appointments
	file.write("INSERT INTO observacao (id, parametro, valor) VALUES\n")
	for i, observation in enumerate(observations):
		appointment_sns_code, symptom, value = observation
		sql = f"	({appointment_sns_code}, '{symptom}', {value})" if value is not None else f"	({appointment_sns_code}, '{symptom}', NULL)"
		sql += "," if i < len(observations) - 1 else ";"
		sql += "\n"
		file.write(sql)
	file.write("\n")
	print("Observations inserted.")

print("SQL script for populating database generated.")