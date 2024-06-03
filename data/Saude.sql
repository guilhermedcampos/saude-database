DROP TABLE IF EXISTS clinica CASCADE;
DROP TABLE IF EXISTS enfermeiro CASCADE;
DROP TABLE IF EXISTS medico CASCADE;
DROP TABLE IF EXISTS trabalha CASCADE;
DROP TABLE IF EXISTS paciente CASCADE;
DROP TABLE IF EXISTS receita CASCADE;
DROP TABLE IF EXISTS consulta CASCADE;
DROP TABLE IF EXISTS observacao CASCADE;

CREATE TABLE clinica(
	nome VARCHAR(80) PRIMARY KEY,
	telefone VARCHAR(15) UNIQUE NOT NULL CHECK (telefone ~ '^[0-9]+$'),
	morada VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE enfermeiro(
	nif CHAR(9) PRIMARY KEY CHECK (nif ~ '^[0-9]+$'),
	nome VARCHAR(80) UNIQUE NOT NULL,
	telefone VARCHAR(15) NOT NULL CHECK (telefone ~ '^[0-9]+$'),
	morada VARCHAR(255) NOT NULL,
	nome_clinica VARCHAR(80) NOT NULL REFERENCES clinica (nome)
);

CREATE TABLE medico(
	nif CHAR(9) PRIMARY KEY CHECK (nif ~ '^[0-9]+$'),
	nome VARCHAR(80) UNIQUE NOT NULL,
	telefone VARCHAR(15) NOT NULL CHECK (telefone ~ '^[0-9]+$'),
	morada VARCHAR(255) NOT NULL,
	especialidade VARCHAR(80) NOT NULL
);

CREATE TABLE trabalha(
nif CHAR(9) NOT NULL REFERENCES medico,
nome VARCHAR(80) NOT NULL REFERENCES clinica,
dia_da_semana SMALLINT,
PRIMARY KEY (nif, dia_da_semana)
);

CREATE TABLE paciente(
	ssn CHAR(11) PRIMARY KEY CHECK (ssn ~ '^[0-9]+$'),
nif CHAR(9) UNIQUE NOT NULL CHECK (nif ~ '^[0-9]+$'),
	nome VARCHAR(80) NOT NULL,
	telefone VARCHAR(15) NOT NULL CHECK (telefone ~ '^[0-9]+$'),
	morada VARCHAR(255) NOT NULL,
	data_nasc DATE NOT NULL
);

CREATE TABLE consulta(
	id SERIAL PRIMARY KEY,
	ssn CHAR(11) NOT NULL REFERENCES paciente,
	nif CHAR(9) NOT NULL REFERENCES medico,
	nome VARCHAR(80) NOT NULL REFERENCES clinica,
	data DATE NOT NULL,
	hora TIME NOT NULL,
	codigo_sns CHAR(12) UNIQUE CHECK (codigo_sns ~ '^[0-9]+$'),
	UNIQUE(ssn, data, hora),
	UNIQUE(nif, data, hora)
);

CREATE TABLE receita(
	codigo_sns VARCHAR(12) NOT NULL REFERENCES consulta (codigo_sns),
	medicamento VARCHAR(155) NOT NULL,
	quantidade SMALLINT NOT NULL CHECK (quantidade > 0),
	PRIMARY KEY (codigo_sns, medicamento)
);

CREATE TABLE observacao(
	id INTEGER NOT NULL REFERENCES consulta,
	parametro VARCHAR(155) NOT NULL,
	valor FLOAT,
PRIMARY KEY (id, parametro)
);

-- (RI-1)
ALTER TABLE consulta
ADD CONSTRAINT chk_appointment_hour
CHECK (
	(EXTRACT(HOUR FROM hora) BETWEEN 8 AND 12 OR EXTRACT(HOUR FROM hora) BETWEEN 14 AND 18)
	AND (EXTRACT(MINUTE FROM hora) IN (0, 30))
);

-- (RI-2)
CREATE OR REPLACE FUNCTION check_doctor_patient_constraint(nif_ CHAR(9), ssn_ CHAR(11))
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if the doctor is trying to consult themselves
    IF EXISTS (
        SELECT 1 
        FROM paciente p 
        WHERE p.ssn = ssn_ AND p.nif = nif_
    ) THEN
        RETURN FALSE;
    ELSE
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE consulta
ADD CONSTRAINT chk_doctor_patient
CHECK (check_doctor_patient_constraint(nif, ssn));


-- (RI-3)
CREATE OR REPLACE FUNCTION check_clinic_workday_constraint(doctor_nif CHAR(9), clinic_name VARCHAR(80), consultation_date DATE)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if the doctor works at the clinic on the given day of the week
    IF EXISTS (
        SELECT 1
        FROM trabalha t
        WHERE t.nif = doctor_nif
          AND t.nome = clinic_name
          AND t.dia_da_semana = EXTRACT(ISODOW FROM consultation_date)
    ) THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE consulta
ADD CONSTRAINT chk_clinic_workday
CHECK (check_clinic_workday_constraint(nif, nome, data));
