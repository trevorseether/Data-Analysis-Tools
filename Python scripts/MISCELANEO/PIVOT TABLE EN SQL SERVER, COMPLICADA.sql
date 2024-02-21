
DECLARE @columns NVARCHAR(MAX);
DECLARE @sql NVARCHAR(MAX);

SET @columns = STUFF((
    SELECT ', ' + QUOTENAME(ClasificaciondelDeudor14)
    FROM (
        SELECT DISTINCT ClasificaciondelDeudor14
        FROM anexos_riesgos2..Anx06_preliminar
        WHERE FechaCorte1 = '20230531'
    ) AS Subquery
    FOR XML PATH(''), TYPE
).value('.', 'NVARCHAR(MAX)'), 1, 2, '');

SET @sql = '
SELECT *
FROM (
    SELECT TipodeCredito19, ClasificaciondelDeudor14, Saldodecolocacionescreditosdirectos24
    FROM anexos_riesgos2..Anx06_preliminar
    WHERE FechaCorte1 = ''20230531''
) AS SourceTable
PIVOT (
    SUM(Saldodecolocacionescreditosdirectos24)
    FOR ClasificaciondelDeudor14 IN (' + @columns + ')
) AS PivotTable;
';

EXEC(@sql);

-------------
