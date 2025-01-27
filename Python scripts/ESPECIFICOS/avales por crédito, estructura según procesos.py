# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 09:40:31 2025

@author: sanmiguel38
"""

import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\experian rossonero\\avales procesamiento para brenda')

#%%
avales = pd.read_excel('Rpt_Avales.xlsx',
                       dtype    = str,
                       skiprows = 8
                       )

avales = avales.dropna(subset=['Numero'])

#%%
avales1 = avales[['Numero', 'Aval']]

avales1['Fincore'] = avales1['Numero'].str.split('-').str[1]

#%%
import pyodbc
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\mype no morosos')
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''SELECT
		--------------------------------------------------------------
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
        CASE
            WHEN FI.CODIGO IN (34,35,36,37,38,39) THEN 'DXP'
            WHEN FI.CODIGO IN (32) THEN 'MULTIOFICIOS'
            WHEN FI.CODIGO IN (26) THEN 'EMPRENDE MUJER'
            WHEN FI.CODIGO IN (30,31) THEN 'LIBRE DISPONIBILIDAD'
            WHEN FI.CODIGO IN (33) THEN 'LD - INDEPENDIENTE'
            WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
            WHEN FI.CODIGO IN (21,22,23,24,25,27,28,29) THEN 'MICRO EMPRESA'
            WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
            WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIA'
            ELSE 'OTROS'
        END as 'PRODUCTO',

	FI.DESCRIPCION AS 'SUB PRODUCTO'

FROM prestamo AS p

INNER JOIN socio AS s             ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto AS sc     ON sc.codsocio = s.codsocio
LEFT JOIN planilla AS pla         ON p.codplanilla = pla.codplanilla
INNER JOIN grupocab AS pro        ON pro.codgrupocab = p.codgrupocab
INNER JOIN distrito AS d          ON d.coddistrito = sc.coddistrito
INNER JOIN provincia AS pv        ON pv.codprovincia = d.codprovincia
INNER JOIN departamento AS dp     ON dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet AS tm  ON tm.codtabladet = p.CodEstado
LEFT JOIN grupocab AS gpo         ON gpo.codgrupocab = pla.codgrupocab
LEFT JOIN tablaMaestraDet AS tm2  ON tm2.codtabladet = s.codestadocivil
LEFT JOIN tablaMaestraDet AS tm3  ON tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
INNER JOIN pais                   ON pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI         ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN TipoCredito AS TC       ON tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
INNER JOIN TablaMaestraDet AS tm4 ON s.codestado = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

LEFT JOIN SolicitudCredito AS SOLICITUD ON P.CodSolicitudCredito = SOLICITUD.CodSolicitudCredito
LEFT JOIN Usuario AS USUARIO            ON SOLICITUD.CodUsuarioSegAprob = USUARIO.CodUsuario

-----------------------------------------------------
	LEFT JOIN TipoCambioSBS AS TCSBS
	on (year(p.fechadesembolso) = tcsbs.Anno) and (month(p.fechadesembolso) = tcsbs.MES)

-----------------------------------------------------
--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20020101'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio     > 0
AND p.montosolicitado > 0
AND p.codestado <> 563 -- que no sea crédito anulado


'''

df_fincore = pd.read_sql_query(query, conn)

df_fincore = df_fincore.drop_duplicates(subset = 'pagare_fincore')

#%%
avales1 = avales1.merge(df_fincore,
                        left_on = 'Fincore',
                        right_on = 'pagare_fincore',
                        how = 'left')

avales1 = avales1.dropna(subset = ['pagare_fincore'])

avales1 = avales1[['Fincore', 'PRODUCTO', 'SUB PRODUCTO', 'Aval']]

avales2 = avales1.drop_duplicates(subset = ['Fincore', 'PRODUCTO', 'SUB PRODUCTO', 'Aval'])

#%%
avales2['Enumeracion'] = avales2.groupby('Fincore').cumcount() + 1

avales2['CO DEUDOR'] = 'CO DEUDOR ' + avales2['Enumeracion'].astype(str)

#%%

# Pivotear los datos
result = avales2.pivot(index=['Fincore', 'PRODUCTO', 'SUB PRODUCTO'], 
                       columns='Enumeracion', 
                       values='Aval')

# Renombrar las columnas para que reflejen "CO DEUDOR"
result.columns = [f'CO DEUDOR {col}' for col in result.columns]

# Resetear el índice para volver a tener un DataFrame plano
result = result.reset_index()
result = result.drop_duplicates(subset = ['Fincore'])

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\experian rossonero\\avales procesamiento para brenda')

result.to_excel('Avales.xlsx',
                index = False )
