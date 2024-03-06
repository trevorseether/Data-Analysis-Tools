
DECLARE @CORTE AS DATETIME = eomonth('20231231')
DECLARE @CORTE_ANTERIOR AS DATETIME = eomonth(DATEADD(DAY, -1, EOMONTH(DATEADD(MONTH, -1, @CORTE))))

SELECT @corte
SELECT @corte_anterior

SELECT 
	/*A.Nro_Fincore,
	A.TipodeCredito19,
	A.SaldosdeCreditosCastigados38, 
	B.SaldosdeCreditosCastigados38,
	A.SaldosdeCreditosCastigados38 - B.SaldosdeCreditosCastigados38*/
	sum(A.SaldosdeCreditosCastigados38 - B.SaldosdeCreditosCastigados38) * -1
FROM anexos_riesgos3..ANX06 AS A

LEFT JOIN anexos_riesgos3..ANX06 AS B ON A.Nro_Fincore = B.Nro_Fincore

WHERE A.FechaCorte1 = @CORTE
AND B.FechaCorte1   = @CORTE_ANTERIOR
AND A.SaldosdeCreditosCastigados38 > 0
AND B.SaldosdeCreditosCastigados38 > 0
AND A.SaldosdeCreditosCastigados38 - B.SaldosdeCreditosCastigados38 != 0
AND a.ApellidosyNombresRazonSocial2 NOT LIKE '%invers%grau%'
;
/*---------------------------------------------------------------------------------*/

select 
	/*a.Nro_Fincore */
	sum(a.SaldosdeCreditosCastigados38)
from anexos_riesgos3..ANX06 as A

LEFT JOIN anexos_riesgos3..ANX06 AS B ON A.Nro_Fincore = B.Nro_Fincore

WHERE A.FechaCorte1 = @corte_anterior
AND A.SaldosdeCreditosCastigados38 > 0
and B.FechaCorte1 = @CORTE
AND B.Nro_Fincore IS NULL

