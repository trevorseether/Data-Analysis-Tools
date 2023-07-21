
--PIVOT TABLE EN SQL SERVER
--
SELECT *
FROM (
    SELECT TipodeCredito19, ClasificaciondelDeudor14, Saldodecolocacionescreditosdirectos24
    FROM anexos_riesgos2..Anx06_preliminar
	where FechaCorte1 = '20230531'
) AS SourceTable
PIVOT (
    SUM(Saldodecolocacionescreditosdirectos24)
    FOR ClasificaciondelDeudor14 IN ([0],[1],[2],[3],[4])
) AS PivotTable;
--------------------------
