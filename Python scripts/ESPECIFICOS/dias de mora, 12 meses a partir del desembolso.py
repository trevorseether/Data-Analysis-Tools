# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:00:07 2024

@author: sanmiguel38
"""

# =============================================================================
# dias de atraso según los meses
# =============================================================================

import pandas as pd
import pyodbc
import os
import warnings
warnings.filterwarnings('ignore')

#%%
# fecha_corte = '2024-03-31'

'Directorio de trabajo:'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\dias de atraso, 12 meses a partir del desembolso')

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = '''
SELECT  
	FechaCorte1,
	FechadeDesembolso21,
	EOMONTH(FechadeDesembolso21) as 'ULT DÍA DESEMBOLSO',
	DATEDIFF(MONTH, EOMONTH(FechadeDesembolso21), FechaCorte1) as 'MESES DIFERENCIA',
	ApellidosyNombresRazonSocial2,
	NumerodeDocumento10,
	TipodeDocumento9,
	Nro_Fincore,
	DiasdeMora33,
	TipodeProducto43,
		CASE
			WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
			WHEN TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29) THEN 'MYPE'
			END AS 'PRODUCTO TXT'
FROM anexos_riesgos3..ANX06
WHERE FechadeDesembolso21 BETWEEN '20220301' AND '20230331'
AND TipodeProducto43 in (34,35,36,37,38,39,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29)
and DATEDIFF(MONTH, EOMONTH(FechadeDesembolso21), FechaCorte1) <= 12
ORDER BY FechaCorte1, ApellidosyNombresRazonSocial2
'''
base = pd.read_sql_query(query, 
                         conn,
                         parse_dates=['ULT DÍA DESEMBOLSO'])
base['Nro_Fincore'] = base['Nro_Fincore'].str.strip() #########################
del conn

#%%
# corte_actual = base[base['FechaCorte1'] == pd.Timestamp(fecha_corte)]
# corte_actual.rename(columns = {"DiasdeMora33" : "Dias de mora actual"}, 
#                     inplace = True)

# owo = corte_actual.copy()

#%% DESEMBOLSADOS (todos incluso los cancelados)
# datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

# server      = datos['DATOS'][0]
# username    = datos['DATOS'][2]
# password    = datos['DATOS'][3]

# conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
# conn = pyodbc.connect(conn_str)

# query = '''
# SELECT

# 	s.codigosocio, 
# 	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
# 	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
        
# 	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
# 	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
# 	p.fechadesembolso, 
# 	p.montosolicitado as 'Otorgado',
# 	p.fechaCancelacion, 
# 	tc.Descripcion as 'TipoCredito', 
# 	FI.CODIGO AS 'COD_FINALIDAD', 
# 	FI.DESCRIPCION AS 'FINALIDAD'

# 	-- ,
# 	-- DESCUENTO.valor as 'retención',
# 	-- p.montosolicitado - DESCUENTO.valor as 'MONTO NETO'

# -- pcu.FechaVencimiento as Fecha1raCuota, pcu.NumeroCuota, pcu.SaldoInicial,
# FROM prestamo AS p

# INNER JOIN socio AS s             ON s.codsocio = p.codsocio
# LEFT JOIN sociocontacto AS sc     ON sc.codsocio = s.codsocio
# LEFT JOIN planilla AS pla         ON p.codplanilla = pla.codplanilla
# INNER JOIN grupocab AS pro        ON pro.codgrupocab = p.codgrupocab
# INNER JOIN distrito AS d          ON d.coddistrito = sc.coddistrito
# INNER JOIN provincia AS pv        ON pv.codprovincia = d.codprovincia
# INNER JOIN departamento AS dp     ON dp.coddepartamento = pv.coddepartamento
# INNER JOIN tablaMaestraDet AS tm  ON tm.codtabladet = p.CodEstado
# LEFT JOIN grupocab AS gpo         ON gpo.codgrupocab = pla.codgrupocab
# LEFT JOIN tablaMaestraDet AS tm2  ON tm2.codtabladet = s.codestadocivil
# LEFT JOIN tablaMaestraDet AS tm3  ON tm3.codtabladet = p.CodSituacion
# --INNER JOIN tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
# INNER JOIN pais                   ON pais.codpais = s.codpais
# LEFT JOIN FINALIDAD AS FI         ON FI.CODFINALIDAD = P.CODFINALIDAD
# LEFT JOIN TipoCredito AS TC       ON tc.CodTipoCredito = p.CodTipoCredito
# INNER JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
# INNER JOIN TablaMaestraDet AS tm4 ON s.codestado = tm4.CodTablaDet
# --LEFT JOIN PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

# LEFT JOIN SolicitudCredito AS SOLICITUD ON P.CodSolicitudCredito = SOLICITUD.CodSolicitudCredito
# LEFT JOIN Usuario AS USUARIO            ON SOLICITUD.CodUsuarioSegAprob = USUARIO.CodUsuario

# --LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito
# --LEFT JOIN PAIS AS PAIS ON S.CodPais = PAIS.CODPAIS

# WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) between '20220301' and '20230331'

# --AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

# --AND s.codigosocio>0

# --and p.codestado = 342
# --AND FI.CODIGO IN (15,16,17,18,19,20,21,22,23,24,25,29)

# -- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
# -- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
# -- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
# -- AND p.codcategoria=351
# ORDER BY iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) ASC, p.fechadesembolso DESC
# '''

# df_fincore = pd.read_sql_query(query, conn)

# df_fincore.drop_duplicates(subset  = 'pagare_fincore', 
#                            inplace = True)

# del conn

# owo = df_fincore.copy()

# owo.rename(columns = {'pagare_fincore' : 'Nro_Fincore'}, 
#                     inplace = True)

#%% DESEMBOLSADOS
owo = base[base['FechaCorte1'] == base['ULT DÍA DESEMBOLSO']]

#%% merges
for i in range(1,13):
    # print(i)
    owo = owo.merge(base[base['MESES DIFERENCIA'] == i][['Nro_Fincore', "DiasdeMora33"]],
                             on  = 'Nro_Fincore',
                             how = 'left')

owo.columns = ['FechaCorte1',         'FechadeDesembolso21',    'ULT DÍA DESEMBOLSO',
               'MESES DIFERENCIA',    'ApellidosyNombresRazonSocial2',
               'NumerodeDocumento10', 'TipodeDocumento9',       'Nro_Fincore',
               'DiasdeMora33',        'TipodeProducto43',       'PRODUCTO TXT',
               'Días de atraso 1er mes', 
               'Días de atraso 2do mes',
               'Días de atraso 3er mes',
               'Días de atraso 4to mes',
               'Días de atraso 5to mes',
               'Días de atraso 6to mes',
               'Días de atraso 7mo mes',
               'Días de atraso 8vo mes',
               'Días de atraso 9no mes',
               'Días de atraso 10mo mes',
               'Días de atraso 11vo mes',
               'Días de atraso 12vo mes']

owo.drop_duplicates(subset  = 'Nro_Fincore', 
                    inplace = True)

#%% ESTRUCTURA EXPERIAN
df_experian_12_meses = pd.DataFrame()
df_experian_12_meses['Fecha_Evaluacion( fecha desembolso )'] = owo['FechadeDesembolso21']
df_experian_12_meses['Tipo de documento']       = owo['TipodeDocumento9']
df_experian_12_meses['Número de documento']     = owo['NumerodeDocumento10']
df_experian_12_meses['Tipo de crédito']         = owo['PRODUCTO TXT']
df_experian_12_meses['Dictamen']                = None
df_experian_12_meses['Días de atraso 1er mes']  = owo['Días de atraso 1er mes']
df_experian_12_meses['Días de atraso 2do mes']  = owo['Días de atraso 2do mes']
df_experian_12_meses['Días de atraso 3er mes']  = owo['Días de atraso 3er mes']
df_experian_12_meses['Días de atraso 4to mes']  = owo['Días de atraso 4to mes']
df_experian_12_meses['Días de atraso 5to mes']  = owo['Días de atraso 5to mes']
df_experian_12_meses['Días de atraso 6to mes']  = owo['Días de atraso 6to mes']
df_experian_12_meses['Días de atraso 7mo mes']  = owo['Días de atraso 7mo mes']
df_experian_12_meses['Días de atraso 8vo mes']  = owo['Días de atraso 8vo mes']
df_experian_12_meses['Días de atraso 9no mes']  = owo['Días de atraso 9no mes']
df_experian_12_meses['Días de atraso 10mo mes'] = owo['Días de atraso 10mo mes']
df_experian_12_meses['Días de atraso 11vo mes'] = owo['Días de atraso 11vo mes']
df_experian_12_meses['Días de atraso 12vo mes'] = owo['Días de atraso 12vo mes']

para_filla_na_0 = ['Días de atraso 1er mes', 
                   'Días de atraso 2do mes',
                   'Días de atraso 3er mes',
                   'Días de atraso 4to mes',
                   'Días de atraso 5to mes',
                   'Días de atraso 6to mes',
                   'Días de atraso 7mo mes',
                   'Días de atraso 8vo mes',
                   'Días de atraso 9no mes',
                   'Días de atraso 10mo mes',
                   'Días de atraso 11vo mes',
                   'Días de atraso 12vo mes']
for i in para_filla_na_0:
    df_experian_12_meses[i] = df_experian_12_meses[i].fillna(0)
    
#%% A EXCEL
df_experian_12_meses.to_excel('dias de atraso.xlsx',
                              index = False)

# owo.to_excel('dias de atraso.xlsx',
#              index = False)
