# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 09:19:43 2024

@author: sanmiguel38
"""
# =============================================================================
#                            VISITA DOMICILIARIA
# =============================================================================

import pandas as pd
import os
import pyodbc
#%%
ubi         = 'C:\\Users\\sanmiguel38\\Desktop\\VERIFICACIÓN DOMICILIARIA\\05 junio'
nombre      = 'RELACIÓN MYPE - JUNIO 2024.xlsx'
skip_filas  = 2
fecha_corte = '20240531'
menor_a     = 10000

#%%

os.chdir(ubi)
desembolsados = pd.read_excel(io = nombre, 
                              # sheet_name = ,
                              skiprows = skip_filas,
                              dtype = {'N°\nPréstamo' : str,
                                       'N° DNI'       : str})

desembolsados['N°\nPréstamo'] = desembolsados['N°\nPréstamo'].str.strip()
desembolsados['N° DNI']       = desembolsados['N° DNI'].str.strip()

#%% filtrado
#desembolsados = desembolsados[desembolsados['Monto'] <= menor_a]

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = f'''
DECLARE @CORTE AS DATETIME      = '{fecha_corte}' 
DECLARE @INICIO_MES AS DATETIME = DATEFROMPARTS(YEAR(@CORTE), MONTH(@CORTE), 1);
--------------------------------------------------------------------------------
SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	p.montosolicitado as 'Otorgado', 
	p.TEM, 
	p.NroPlazos, 
	p.CuotaFija,
	p.fechaCancelacion, 
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado,
	CONCAT(sc.nombrevia,' Nro ', sc.numerovia,' ', sc.nombrezona) as 'direcc_socio',
	d.nombre as 'distrito', 
	pv.nombre as 'provincia', 
	dp.nombre as 'departamento',
	sc.ReferenciaDomicilio,
	TIPO_CASA.Descripcion

FROM socio                 AS s
LEFT JOIN prestamo         AS p   ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto    AS sc  ON sc.codsocio = s.codsocio
LEFT JOIN planilla         AS pla ON p.codplanilla = pla.codplanilla
INNER JOIN grupocab        AS pro ON pro.codgrupocab = p.codgrupocab
INNER JOIN distrito        AS d   ON d.coddistrito = sc.coddistrito
INNER JOIN provincia       AS pv  ON pv.codprovincia = d.codprovincia
INNER JOIN departamento    AS dp  ON dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet AS tm  ON tm.codtabladet = p.CodEstado

LEFT JOIN TablaMaestraDet AS TIPO_CASA  ON SC.CodTipoDomicilio = TIPO_CASA.CodTablaDet

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN @INICIO_MES AND @CORTE

AND TIPO_CASA.CodTablaCab = 4

'''

df_fincore = pd.read_sql_query(query, conn)
del conn

df_fincore.drop_duplicates( subset = 'codigosocio', inplace = True)

#%% MERGE LEFT JOIN
col_desembolsados = desembolsados[['Socio',
                                   'N° DNI']]

col_desembolsados = col_desembolsados.merge(df_fincore,
                                            left_on  = 'N° DNI',
                                            right_on = 'Doc_Identidad',
                                            how      = 'left')

#%%
col_desembolsados.to_excel('visita domiciliaria.xlsx',
                           index = False)

