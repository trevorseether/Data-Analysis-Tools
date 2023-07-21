-----------------------------
---NÚMERO DE SEMANA EN EL MES
-----------------------------

SELECT
    FechadeDesembolso21,
    'semana '+ str(DATEDIFF(WEEK, DATEADD(MONTH, DATEDIFF(MONTH, 0, FechadeDesembolso21), 0), FechadeDesembolso21) + 1) AS NumeroSemanaMes
FROM
    anexos_riesgos2..Anx06_preliminar AS a
WHERE
    FechaCorte1 = '20230430'
--	and FechadeDesembolso21 = '20230428'
ORDER BY
    a.FechadeDesembolso21

------------------------------------------
--CÓDIGO PARA VER EL NRO DE SEMANA DEL AÑO
------------------------------------------

SELECT
    FechadeDesembolso21
    ,DATEPART(WEEK, FechadeDesembolso21)
FROM
    anexos_riesgos2..Anx06_preliminar AS a
WHERE
    FechaCorte1 = '20230430'
ORDER BY
    a.FechadeDesembolso21

--------------------------------------------
--- NÚMERO DE SEMANA EN EL MES, SIMPLIFICADO
--------------------------------------------

SELECT
    FechadeDesembolso21,
    case
		when day(FechadeDesembolso21) between 1 and 7 then 'semana 1'
		when day(FechadeDesembolso21) between 8 and 14 then 'semana 2'
		when day(FechadeDesembolso21) between 15 and 21 then 'semana 3'
		when day(FechadeDesembolso21) between 22 and 35 then 'semana 4'
		end as 'numero semana'
FROM
    anexos_riesgos2..Anx06_preliminar AS a
WHERE
    FechaCorte1 = '20230430'
	and FechadeDesembolso21 = '20230428'
ORDER BY
    a.FechadeDesembolso21

