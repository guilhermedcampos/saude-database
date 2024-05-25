import random
from datetime import date, timedelta

# Function to generate random date of birth
def random_date(start, end):
	return start + timedelta(days=random.randint(0, (end - start).days))

# Open a file to write SQL commands
with open("populate_patients.sql", "w") as file:
	for i in range(1, 5001):
		ssn = str(i).zfill(11)
		nif = str(i + 5000).zfill(9)
		name = f'Patient {i}'
		phone = str(i + 10000).zfill(9)
		address = f'Street {i}, 1000-000 City'
		dob = random_date(date(1970, 1, 1), date(2000, 12, 31)).strftime('%Y-%m-%d')
		
		sql = f"INSERT INTO paciente (ssn, nif, nome, telefone, morada, data_nasc) VALUES ('{ssn}', '{nif}', '{name}', '{phone}', '{address}', '{dob}');\n"
		file.write(sql)

print("SQL script for populating patients generated.")