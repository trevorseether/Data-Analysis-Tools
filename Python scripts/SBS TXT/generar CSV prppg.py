# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 16:26:45 2025

@author: Joseph
"""


import pyodbc
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

#%%
f_corte = '03-2024'
os.chdir('C:\\Users\\admin\\Desktop\\prppgs, cortes trimestrales')

#%%
server      = '172.16.1.16,1433'
username    = 'sa'
password    = 'sql'
database    = 'SANMIGUEL'

if 'cuotas' not in globals():

    conn_str = f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password};'
    conn = pyodbc.connect(conn_str)
    
    create_temp_table_query = '''
    IF OBJECT_ID('tempdb.dbo.#TMP_SOCIOBLOQUEAR', 'U') IS NOT NULL
        DROP TABLE #TMP_SOCIOBLOQUEAR;  
	SELECT CODSOCIO INTO #TMP_SOCIOBLOQUEAR FROM Socio   
    WHERE CodSocio IN (
	105,637,1409,1598,1650,1654,1685,1996,2135,2144,2534,4856,6621,10491,21815,34561,
	17206,1650,1654,293,470,508,509,578,582,622,623,625,
    627,631,632,634,642,643,644,646,667,668,669,671,674,675,
    676,679,680,699,704,4724,6642,7211,374,388,391,392,393,
    394,396,397,398,399,400,405,412,413,414,415,416,417,
    420,421,422,424,425,450,451,453)
    '''
    conn.execute(create_temp_table_query)    
    
    query = '''
    	SELECT
			''                                                                 AS 'CIS',    
			RIGHT(CONCAT('00000000',P.Numero),8)                               AS 'CCR',    
			ISNULL(pc.numerocuota,'')                                          AS 'NCUO',   
			''                                                                 AS 'MON',    
			IIF(PC.CodEstado<>379,pc.capital,CD.CAPITAL)                       AS 'MCUO',   
			IIF(PC.CodEstado<>379,pc.interes,CD.INTERES)                       AS 'SIC',    
			IIF(PC.CodEstado<>379,pc.Aporte,CD.APORTE)                         AS 'SCOM',   
			''                                                                 AS 'SEGS',   
			''                                                                 AS 'SIM',    
			iif(pc.codestado=346,0, IIF(PC.CodEstado <> 379,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte),CD.CAPITAL+CD.INTERES+CD.APORTE)) AS 'TCUO',
			ISNULL(CONVERT(VARCHAR(10),pc.FechaVencimiento,103),'')            AS 'FVEP',   
			''                                                                 AS 'FCAN',   
			''                                                                 AS 'SCONK',  
			''                                                                 AS 'SCONINT',
			''                                                                 AS 'DAKC',   
			''                                                                 AS 'FOCAN',  
			''                                                                 AS 'SCA',    


			IIF(PC.CodEstado<>379,pc.aporte,CD.APORTE) AS TotalCargo,
	
			'0' as CargosGenerales,
			'0' as CargosSeguro,

			0 as Ahorros,
			iif(pc.CodEstado in (22,1003,379),'9','0') as Pagado,pc.CodEstado ,
            
            -----------------------
            pc.FechaCreacion,
            FORMAT(pc.FechaCreacion, 'dd/MM/yyyy') as 'FechaCreacion'
            
            
            
        --,pc.CodEstado as EstadoCuota,pc.CuotaFija,P.CodEstado as EstadoPrestamo,P.FechaVentaCartera,P.CodSocio,p.CodPrestamo,p.FechaDesembolso,pc.periodo   
        from prestamocuota pc
        inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
        inner join socio s on p.CodSocio =s.CodSocio
        LEFT JOIN 
        (SELECT SUM(CAPITAL) AS CAPITAL,SUM(INTERES) AS INTERES,SUM(APORTE) AS APORTE,CodPrestamoCuota FROM CobranzaDet GROUP BY CodPrestamoCuota)
        CD ON pc.CodPrestamoCuota =CD.CodPrestamoCuota
        where
        pc.CodEstado not in (24) and p.CodEstado <>563   and CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null --and (pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte)>0
         AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
         AND PC.CodPrestamoCuota NOT IN (
        							 SELECT CodPrestamoCuota  FROM (
        							select
        							PC.CodPrestamoCuota,
        							ISNULL(pc.numerocuota,'') as numerocuota,
        							pc.interes,
        							iif(pc.CodEstado in (22,1003),'9','0') as Pagado,
        							iif(pc.codestado=346,0,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte)) as TotalPago
        							from prestamocuota pc
        							inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
        							inner join socio s on p.CodSocio =s.CodSocio
        							where
        							pc.CodEstado not in (24,379) and p.CodEstado <>563   and CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null 
        							 AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
        							 AND   P.FECHAVENTACARTERA IS NULL
        							 ) TABLA 
        							 WHERE numerocuota =0 AND Interes =0 AND TotalPago =0
         
         )
        -- AND   P.FECHAVENTACARTERA IS NULL
        order by pc.CodPrestamo,  pc.CodPrestamoCuota 
                '''
    
    prppg_cuotas = pd.read_sql_query(query, conn, dtype = str)
    conn.close()
    
    print('nro de filas:')
    print(prppg_cuotas.shape[0])
    
#%%
# Guardar en un archivo CSV
prppg_cuotas.to_csv(f"prppg {f_corte}.csv", 
                     index     = False, 
                     encoding  = "utf-8")

#%%
print('fin')

