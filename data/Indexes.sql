--6.1 B-tree
CREATE INDEX idx_observacao_parametro_valor ON observacao (parametro, valor); --Most Important

CREATE INDEX idx_paciente_ssn ON paciente (ssn);
CREATE INDEX idx_consulta_ssn ON consulta (ssn);
CREATE INDEX idx_consulta_id ON consulta (id);
CREATE INDEX idx_observacao_id ON observacao (id);

--6.2 B-tree
CREATE INDEX idx_consulta_data ON consulta (data); --Most Important

CREATE INDEX idx_medico_especialidade ON medico (nif);
CREATE INDEX idx_consulta_nif ON consulta (nif);
CREATE INDEX idx_receita_codigo_ssn ON receita (codigo_ssn);