
-- PIVOT TABLE MÁS SENCILLA
SELECT 
    TipodeCredito19,
    SUM(CASE WHEN ClasificaciondelDeudor14 = '0' THEN Saldodecolocacionescreditosdirectos24 END) AS [Clasificacion 0],
    SUM(CASE WHEN ClasificaciondelDeudor14 = '1' THEN Saldodecolocacionescreditosdirectos24 END) AS [Clasificacion 1],
    SUM(CASE WHEN ClasificaciondelDeudor14 = '2' THEN Saldodecolocacionescreditosdirectos24 END) AS [Clasificacion 2],
    SUM(CASE WHEN ClasificaciondelDeudor14 = '3' THEN Saldodecolocacionescreditosdirectos24 END) AS [Clasificacion 3],
    SUM(CASE WHEN ClasificaciondelDeudor14 = '4' THEN Saldodecolocacionescreditosdirectos24 END) AS [Clasificacion 4]
FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = '20230531'
GROUP BY TipodeCredito19;

--
SELECT 
    TipodeCredito19,
    CASE WHEN ClasificaciondelDeudor14 = '0' THEN Saldodecolocacionescreditosdirectos24 END AS [Clasificacion 0],
    CASE WHEN ClasificaciondelDeudor14 = '1' THEN Saldodecolocacionescreditosdirectos24 END AS [Clasificacion 1],
    CASE WHEN ClasificaciondelDeudor14 = '2' THEN Saldodecolocacionescreditosdirectos24 END AS [Clasificacion 2],
    CASE WHEN ClasificaciondelDeudor14 = '3' THEN Saldodecolocacionescreditosdirectos24 END AS [Clasificacion 3],
    CASE WHEN ClasificaciondelDeudor14 = '4' THEN Saldodecolocacionescreditosdirectos24 END AS [Clasificacion 4]
FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = '20230531'
