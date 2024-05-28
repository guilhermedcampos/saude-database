WITH timespans AS (
	SELECT 
		ssn,
		MAX(data) - MIN(data) as max_timespan
	FROM 
		historial_paciente 
	WHERE 
		especialidade = 'ortopedia' AND 
		tipo = 'observacao' AND 
		valor IS NULL
	GROUP BY 
		ssn
)
SELECT 
	ssn, 
	MAX(data) - MIN(data) as max_timespan
FROM 
	timespans
GROUP BY 
	ssn,
	max_timespan
HAVING 
	max_timespan >= ALL (
		SELECT 
			max_timespan
		FROM 
			timespans
		GROUP BY 
			ssn,
			max_timespan
	)
ORDER BY 
	max_timespan DESC;