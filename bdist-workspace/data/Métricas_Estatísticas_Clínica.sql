SELECT
	hp.nome as clinica,
	hp.especialidade as especialidade_medico, 
	medico.nome as nome_medico, 
	hp.chave as metrica,
	AVG(hp.valor) as media_quantidade,
	STDDEV(hp.valor) as desvio_padrao_quantidade
FROM 
	historial_paciente hp
JOIN medico ON hp.nif = medico.nif
WHERE 
	hp.tipo = 'observacao' AND
	hp.valor IS NOT NULL
GROUP BY
	hp.clinica,
	hp.especialidade, 
	medico.nome, 
	hp.chave
ORDER BY
	hp.nome,
	hp.especialidade, 
	medico.nome;