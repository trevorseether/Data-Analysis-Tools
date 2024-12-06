# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:29:21 2024

@author: sanmiguel38
"""

# =============================================================================
# SOCIOS NO MOROSOS AL CORTE ESPECÍFICO
# =============================================================================

import os
import pandas as pd
import pyodbc

#%%
corte_anx_06 = '20241031'
usar_sql     = True # para usar Anexo 06

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\socios buenos para sorteo\\no morosis')

#%%
#%% LECTURA DE LAS CREDENCIALES
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%% CREACIÓN DE LA CONECCIÓN A SQL

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#%% QUERY, créditos vigentes

query = f'''
-- p.codcategoria = 351 -> nuevo
-- p.codcategoria = 352 -> ampliacion
-- p.codestado = 563 -> anulado
-- p.codestado = 341 -> pendiente
-- p.codestado = 342 -> cancelado
-- tc.CODTIPOCREDITO -> ( 3=Cons.Ordinario / 1=Med.Empresa / 2=MicroEmp. / 9=Peq.Empresa)

SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'DOCUMENTO',
	IIF(S.CodSexo = 4, 'FEMENINO',
		IIF(S.CodSexo = 3, 'MASCULINO','EMPRESA')) AS 'SEXO',
	s.fechanacimiento, 
	sc.celular1  as 'Celular',
	sc.Email,
    	CASE
    		WHEN FI.CODIGO IN (34,35,36,37,38,39) THEN 'DXP'
    		WHEN FI.CODIGO IN (30,31,33) THEN 'LIBRE DISPONIBILIDAD'
    		WHEN FI.CODIGO IN (32) THEN 'MULTI OFICIOS'
    		WHEN FI.CODIGO IN (26) THEN 'EMPRENDE MUJER'
    		WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
    		WHEN FI.CODIGO IN (21,22,23,24,25,27,28,29) THEN 'MICRO EMPRESA'
    		WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
    		WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIO'
    			END AS 'PRODUCTO',

	pro.descripcion as 'Funcionario',
	d.nombre   AS 'distrito', 
	pv.nombre  AS 'provincia', 
	dp.nombre  AS 'departamento',
		p.montosolicitado as 'Otorgado',
        p.fechadesembolso

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

WHERE 1 = 1

--CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20220101'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio     > 0
AND p.montosolicitado > 0
AND p.codestado = 341 -- que no sea crédito anulado
--and p.codestado = 342
and p.flagponderosa <> 1

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY p.montosolicitado desc

/*

SELECT a.CodUsuarioPriAprob, a.CodUsuarioSegAprob, b.IdUsuario FROM SolicitudCredito as a
	LEFT JOIN Usuario as b
	on a.CodUsuarioSegAprob = b.CodUsuario

select CodSolicitudCredito,* from prestamo

*/
'''

vigentes = pd.read_sql_query(query, 
                             conn,
                             dtype = {'Celular' : str})
del conn

solo_vigentes = pd.DataFrame()
solo_vigentes['codigosocio'] = vigentes['codigosocio']
solo_vigentes['vig'] = 'vig'
solo_vigentes = solo_vigentes.drop_duplicates(subset = 'codigosocio', keep='first')

#%%
formatos = [ '%d/%m/%Y %H:%M:%S',
             '%d/%m/%Y',
             '%Y%m%d',
             '%Y-%m-%d',
             '%Y-%m-%d %H:%M:%S',
             '%Y/%m/%d %H:%M:%S',
             '%Y-%m-%d %H:%M:%S PM',
             '%Y-%m-%d %H:%M:%S AM',
             '%Y/%m/%d %H:%M:%S PM',
             '%Y/%m/%d %H:%M:%S AM' ] # Lista de formatos a analizar

def parse_date(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(   arg = date_str, 
                                  format = formato,)
        except ValueError:
            pass
    return pd.NaT
vigentes['fechanacimiento'] = vigentes['fechanacimiento'].apply(parse_date)

#%%
def cel_51(celular):
    if (celular[0] == '9') and (len(celular) == 9):
        return '+51' + celular
    elif celular[:2] == '51':
        return '+' + celular
    else:
        return 0

vigentes['Celular1'] = vigentes['Celular'].apply(cel_51)

#%%
#%% ANEXO 06
if usar_sql == True:
    conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
    
    query = f'''
    SELECT
        CodigoSocio7 as 'codigosocio',
    	ApellidosyNombresRazonSocial2 AS 'APELLIDOS NOMBRES / RAZÓN SOCIAL',
        FechadeNacimiento3 as 'FECHA NAC',
    	NumerodeDocumento10 AS 'DOCUMENTO', 
    	--TipodeDocumento9 AS 'TIPO DOC',
    	CASE
    		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
    		WHEN TipodeProducto43 IN (30,31,33) THEN 'LIBRE DISPONIBILIDAD'
    		WHEN TipodeProducto43 IN (32) THEN 'MULTI OFICIOS'
    		WHEN TipodeProducto43 IN (26) THEN 'EMPRENDE MUJER'
    		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
    		WHEN TipodeProducto43 IN (21,22,23,24,25,27,28,29) THEN 'MICRO EMPRESA'
    		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
    		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIO'
    			END AS 'PRODUCTO',
    	DiasdeMora33 AS 'DÍAS DE MORA',
    	CASE
    		when Fecha_castigo is not null then 'CASTIGADO'
    		WHEN Refinanciado IN ('REFINANCIADO') THEN 'REFINANCIADO'
    		WHEN Reprogramados = 1 THEN 'REPROGRAMADO'
    		 END AS 'ESTADO'
    FROM anexos_riesgos3..ANX06
    WHERE FechaCorte1 = '{corte_anx_06}'
    ORDER BY ApellidosyNombresRazonSocial2

    '''
    anexo_06 = pd.read_sql_query(query, conn)

#%% mes faltante para el anexo 06
from datetime import datetime, timedelta

def obtener_siguiente_dia(fecha_str):
    # Convertir la cadena de fecha al formato datetime
    fecha = datetime.strptime(fecha_str, '%Y%m%d')
    # Sumar un día
    siguiente_dia = fecha + timedelta(days=1)
    return siguiente_dia

# Obtener el siguiente día
resultado = obtener_siguiente_dia(corte_anx_06)

dias_faltantes = vigentes[vigentes['fechadesembolso'] >= resultado]
dias_faltantes = dias_faltantes.drop_duplicates(subset = 'codigosocio', keep='first')

dias_faltantes = dias_faltantes[['codigosocio'     , 'Socio', 
                                 'fechanacimiento' , 'DOCUMENTO',
                                 'PRODUCTO', ]]
dias_faltantes['DÍAS DE MORA'] = 0
dias_faltantes['ESTADO'] = None

dias_faltantes = dias_faltantes.rename(columns = { 'Socio'           : 'APELLIDOS NOMBRES / RAZÓN SOCIAL',
                                                   'fechanacimiento' : 'FECHA NAC'})

df_concatenado = pd.concat([anexo_06, dias_faltantes.head(0)], ignore_index=True)

df_concatenado = df_concatenado.drop_duplicates(subset = 'codigosocio', keep='first')

#%%
vigentes_sin_dup = vigentes.drop_duplicates(subset = 'codigosocio', keep='first')
completado = df_concatenado.merge(vigentes_sin_dup[['DOCUMENTO',
                                            'Celular1',
                                            #'Funcionario',
                                            'Email',
                                            'distrito', 
                                            'provincia', 
                                            'departamento']],

                                 on     = 'DOCUMENTO',
                                 how    = 'inner')


completado = completado.drop_duplicates(subset = 'codigosocio', keep='first')

#%%
completado = completado.merge(solo_vigentes,
                              on = 'codigosocio',
                              how = 'inner')

completado = completado[completado['vig'] == 'vig']
del completado['vig']

#%%
morosos = completado[completado['DÍAS DE MORA'] != 0]
socios_morosos = list(set(list(morosos['codigosocio'])))

completado = completado[~completado['codigosocio'].isin(socios_morosos)]
completado = completado[pd.isna(completado['ESTADO'])]

del completado['DÍAS DE MORA']
del completado['ESTADO']

#%%
completado.to_excel(f'Socios no morosos {corte_anx_06}.xlsx',
                    index = False)
