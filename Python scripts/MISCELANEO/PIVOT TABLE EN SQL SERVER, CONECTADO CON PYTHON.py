# -*- coding: utf-8 -*-
import pyodbc
import pandas as pd

#%%
#PIVOT TABLE EN SQL SERVER

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')


df = pd.read_sql_query('''                     
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
                     
''', conn)

del conn

