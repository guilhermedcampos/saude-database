SELECT 
    mes, 
    dia_do_mes, 
    chave as medicamento, 
    SUM(valor) AS total_quantidade
FROM 
    historial_paciente
WHERE 
    ano = 2023 AND
	tipo = 'receita'
GROUP BY 
    mes, 
    dia_do_mes, 
    medicamento
ORDER BY 
    mes, 
    dia_do_mes;