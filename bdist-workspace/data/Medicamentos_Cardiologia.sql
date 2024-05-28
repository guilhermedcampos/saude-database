SELECT
	chave
FROM
	historial_paciente
WHERE
	especialidade = 'cardiologia' AND
	tipo = 'receita'
GROUP BY
	chave
HAVING
	MAX(data) >= NOW() - INTERVAL '1 year';
