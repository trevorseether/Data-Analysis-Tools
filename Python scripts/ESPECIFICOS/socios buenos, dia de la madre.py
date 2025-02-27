# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:41:37 2024

@author: sanmiguel38
"""

# =============================================================================
# SOCIOS SIN MOROSIDAD PARA EL SORTEO
# =============================================================================
import pandas as pd
import pyodbc
import os

#%%
fecha_corte = '20250131'
fecha_hoy   = '20250207' # para especificar hasta qué fecha incluir desembolsos(desembolsos nuevos que no están en el ANX06)

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\socios buenos para sorteo\\15 mayo 2024')

usar_sql     = True # True o False, si le das False, es obligatorio definir un excel de anexo06

#%%
if usar_sql == True:
    conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

    query = f'''
    SELECT
    	ApellidosyNombresRazonSocial2 AS 'NOMBRES Y APELLIDOS',
    	NumerodeDocumento10           AS 'DOCUMENTO',
    	CodigoSocio7                  AS 'CÓDIGO SOCIO',
    	Nro_Fincore                   AS 'NRO FINCORE',
    	FechadeDesembolso21           AS 'FECHA DESEMBOLSO',
    	MontodeDesembolso22           AS 'DESEMBOLSO',

    	CASE
    		WHEN TipodeProducto43 IN (34,35,36,37,38,39)          THEN 'DXP'
    		WHEN TipodeProducto43 IN (30,31,32,33)                THEN 'LIBRE DISPONIBILIDAD'
    		WHEN TipodeProducto43 IN (15,16,17,18,19)             THEN 'PEQUEÑA EMPRESA'
    		WHEN TipodeProducto43 IN (21,22,23,24,25,26,27,28,29) THEN 'MICRO EMPRESA'
    		WHEN TipodeProducto43 IN (95,96,97,98,99)             THEN 'MEDIANA EMPRESA'
    		WHEN TipodeProducto43 IN (41,45)                      THEN 'HIPOTECARIO'
    			END AS 'PRODUCTO',
    	CASE
    		WHEN Fecha_castigo IS NOT NULL        THEN 'CASTIGADO'
    		WHEN Refinanciado IN ('REFINANCIADO') THEN 'REFINANCIADO'
    		WHEN Reprogramados = 1                THEN 'REPROGRAMADO'
    		 END AS 'ESTADO',
             
             DiasdeMora33
    
    FROM anexos_riesgos3..ANX06
    WHERE FechaCorte1 = '{fecha_corte}'
    --AND DiasdeMora33 = 0

    ORDER BY ApellidosyNombresRazonSocial2
    
    '''

    anx06 = pd.read_sql_query(query, conn)

#%% FILTRACION
malos = anx06[(anx06['DiasdeMora33'] > 0) |
              (~pd.isna(anx06['ESTADO']))]

buenos = anx06[~anx06['CÓDIGO SOCIO'].isin(malos['CÓDIGO SOCIO'])]

#%% desembolsados este mes
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT

	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	p.fechaCancelacion

FROM prestamo as p

INNER JOIN socio as s on s.codsocio = p.codsocio
where CONVERT(VARCHAR(10),p.fechadesembolso,112) > '20100101' 
and s.codigosocio>0  
and p.codestado = 342
order by p.fechadesembolso desc

'''

df_cancelados = pd.read_sql_query(query, conn)

#%% CRÉDITOS DESEMBOLSADOS DURANTE EL PRESENTE MES

fecha_inicio = fecha_hoy[0:6] + '01'

query = f'''
SELECT
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'NOMBRES Y APELLIDOS',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'DOCUMENTO',
	s.codigosocio                                         AS 'CÓDIGO SOCIO', 
	RIGHT(CONCAT('0000000',p.numero),8)                   AS 'NRO FINCORE',
	p.fechadesembolso                                     AS 'FECHA DESEMBOLSO', 
	p.montosolicitado                                     AS 'DESEMBOLSO', 
	CASE
		WHEN FI.CODIGO IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN FI.CODIGO IN (30,31,32,33) THEN 'LIBRE DISPONIBILIDAD'
		WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
		WHEN FI.CODIGO IN (21,22,23,24,25,26,27,28,29) THEN 'MICRO EMPRESA'
		WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
		WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIO'
			END AS 'PRODUCTO'
            
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

--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' AND  '{fecha_hoy}'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio     > 0
AND p.montosolicitado > 0
AND p.codestado = 341
'''
df_desembolsados = pd.read_sql_query(query, 
                                     conn,
                                     dtype = {'DOCUMENTO'    : str,
                                              'CÓDIGO SOCIO' : str,
                                              'NRO FINCORE'  : str})

#%% CONCATENACIÓN DEL ANEXO06 CON LOS DESEMBOLSADOS
del buenos['DiasdeMora33']
del buenos['ESTADO']
df_vertical = pd.concat([buenos, 
                         df_desembolsados], ignore_index = True)

#%% ELIMINAMOS LOS CANCELADOS
df_vertical = df_vertical[~df_vertical['NRO FINCORE'].isin(df_cancelados['pagare_fincore'])]

df_vertical.sort_values(by = ['FECHA DESEMBOLSO', 'NOMBRES Y APELLIDOS'], ascending = [True, True], inplace = True)

#%%
query = '''
SELECT
    RIGHT(CONCAT('0000000',p.numero),8) AS 'NRO FINCORE',
	--s.codigosocio                       AS 'CÓDIGO SOCIO', 
	sc.celular1                         AS 'CELULAR', 
	sc.Email                            AS 'CORREO'

FROM prestamo AS p

INNER JOIN socio AS s             ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto AS sc     ON sc.codsocio = s.codsocio

LEFT JOIN SolicitudCredito AS SOLICITUD ON P.CodSolicitudCredito = SOLICITUD.CodSolicitudCredito
LEFT JOIN Usuario AS USUARIO            ON SOLICITUD.CodUsuarioSegAprob = USUARIO.CodUsuario


'''
datos_socios = pd.read_sql_query(query, 
                                 conn,
                                 dtype = {'NRO FINCORE' : str,
                                          'CELULAR'     : str})

datos_socios['CELULAR'] = datos_socios['CELULAR'].str.strip()

# Función para eliminar '.0' exactamente al final de una cadena
def remove_exact_suffix(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

# Aplicar la función a la columna 'telefono'
datos_socios['CELULAR'] = datos_socios['CELULAR'].apply(lambda x: remove_exact_suffix(x, '.0'))

#%% MERGE CON LOS DATOS
df_final = df_vertical.merge(datos_socios,
                             on  = 'NRO FINCORE',
                             how = 'left')

def cel_51(celular):
    if len(celular) < 9:
        return 0
    if (celular[0] == '9') and (len(celular) == 9):
        return '+51' + celular
    elif celular[:2] == '51':
        return '+' + celular
    else:
        return 0

df_final['CELULAR'] = df_final['CELULAR'].apply(cel_51)

#%%
df_final.to_excel('CAMPAÑA DE DÍA DE LA MADRE.xlsx',
                  index = False)
