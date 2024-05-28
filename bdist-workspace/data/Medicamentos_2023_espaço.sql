SELECT 
    localidade, 
    nome as clinica, 
    chave as medicamento, 
    SUM(valor) AS total_quantidade
FROM 
    historial_paciente
WHERE 
    ano = 2023 AND
	tipo = 'receita'
GROUP BY 
    localidade, 
    clinica, 
    medicamento
ORDER BY 
    localidade, 
    clinica;