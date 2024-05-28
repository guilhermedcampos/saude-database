SELECT 
	hp.especialidade as especialidade_medico, 
	medico.nome as nome_medico, 
	hp.chave as medicamento, 
	SUM(hp.valor) as total_quantidade
FROM 
	historial_paciente hp
JOIN medico ON hp.nif = medico.nif
WHERE 
	hp.ano = 2023 AND
	hp.tipo = 'receita'
GROUP BY 
	hp.especialidade, 
	medico.nome, 
	hp.chave
ORDER BY 
	hp.especialidade, 
	medico.nome;