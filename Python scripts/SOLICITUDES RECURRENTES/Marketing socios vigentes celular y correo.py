# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 10:55:52 2024

@author: sanmiguel38
"""

# =============================================================================
#  SOCIOS CON CRÉDITOS VIGENTES, TELÉFONO Y CORREO
# =============================================================================

import os
import pandas as pd
import pyodbc

#%%
fecha_corte = '20241031'
fecha_hoy   = '20241204' # para especificar hasta qué fecha incluir desembolsos(desembolsos nuevos que no están en el ANX06)

usar_sql     = True #False implica usar el excel, True implica obtener datos del sql
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\MARKETING\\socios con cred vigente')

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

fecha_inicio = fecha_hoy[0:6] + '01'

query = f'''
SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'APELLIDOS NOMBRES / RAZÓN SOCIAL',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'DOCUMENTO', 
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	p.montosolicitado as 'Otorgado', 
	p.TEM, 
	p.NroPlazos, 
	p.CuotaFija,  
	p.codestado, 
	tm.descripcion as 'Estado',
	p.fechaCancelacion, 
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado, 
	pro.descripcion as 'Funcionario', 
	pla.descripcion as 'Planilla', 
	gpo.descripcion as 'func_pla',
	CONCAT(sc.nombrevia,' Nro ', sc.numerovia,' ', sc.nombrezona) as 'direcc_socio', 
	d.nombre as 'distrito', 
	pv.nombre as 'provincia', 
	dp.nombre as 'departamento', 
	iif(s.codigosocio>28790,'SOC.NVO', 'SOC.ANT') AS 'tipo_soc',
	tm2.descripcion as 'est_civil', 
	pais.descripcion as 'pais', 
	s.fechanacimiento as 'FECHA NAC', 
	s.profesion, 
	sc.celular1 AS 'Celular', 
	SC.TelefonoFijo1, 
	sc.Email, 
	p.CodSituacion, 
	tm3.Descripcion as 'Situacion',
	p.fechaventacartera,
	iif(p.flagponderosa=1,'POND','SM') as 'origen',
	tc.CODTIPOCREDITO AS 'ClaseTipoCredito',
	tc.Descripcion as 'TipoCredito', 
	FI.CODIGO AS 'COD_FINALIDAD', 
	FI.DESCRIPCION AS 'FINALIDAD', 
	s.fechaInscripcion, 
	u.IdUsuario as 'User_Desemb', 
	tm4.descripcion as 'EstadoSocio',
    
    	CASE
    		WHEN FI.CODIGO IN (34,35,36,37,38,39) THEN 'DXP'
    		WHEN FI.CODIGO IN (30,31,33) THEN 'LIBRE DISPONIBILIDAD'
    		WHEN FI.CODIGO IN (32) THEN 'MULTI OFICIOS'
    		WHEN FI.CODIGO IN (26) THEN 'EMPRENDE MUJER'
    		WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
    		WHEN FI.CODIGO IN (21,22,23,24,25,27,28,29) THEN 'MICRO EMPRESA'
    		WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
    		WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIO'
    			END AS 'PRODUCTO'

    
-- pcu.FechaVencimiento as Fecha1raCuota, pcu.NumeroCuota, pcu.SaldoInicial,
FROM sanmiguel..prestamo as p

INNER JOIN socio as s               ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto as sc       ON sc.codsocio = s.codsocio
LEFT JOIN planilla as pla           ON p.codplanilla = pla.codplanilla
INNER JOIN grupocab as pro          ON pro.codgrupocab = p.codgrupocab
INNER JOIN distrito as d            ON d.coddistrito = sc.coddistrito
INNER JOIN provincia as pv          ON pv.codprovincia = d.codprovincia
INNER JOIN departamento as dp       ON dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet as tm    ON tm.codtabladet = p.CodEstado
LEFT JOIN grupocab as gpo           ON gpo.codgrupocab = pla.codgrupocab
LEFT JOIN tablaMaestraDet as tm2    ON tm2.codtabladet = s.codestadocivil
LEFT JOIN tablaMaestraDet as tm3    ON tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet as tm3 ON tm3.codtabladet = s.codcategoria
INNER JOIN pais                     ON pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI           ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN TipoCredito as TC         ON tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN usuario as u             ON p.CodUsuario = u.CodUsuario
INNER JOIN TablaMaestraDet as tm4   ON s.codestado = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota as pcu    ON p.CodPrestamo = pcu.CodPrestamo

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) <= '{fecha_hoy}'
AND s.codigosocio>0  
and p.montosolicitado > 0
AND p.codestado = 341 --SIGNFICA QUE EL CRÉDITO SE ENCUENTRE EN SITUACIÓN VIGENTE
and p.flagponderosa <> 1

order by 'APELLIDOS NOMBRES / RAZÓN SOCIAL' asc, p.fechadesembolso desc

'''

vigentes = pd.read_sql_query(query, 
                             conn, 
                             dtype = {'codigosocio'     : str,
                                      'DOCUMENTO'       : object,
                                      'pagare_fincore'  : object,
                                      'fechadesembolso' : object,
                                      'Celular'         : str
                                      })
del conn
vigentes.drop_duplicates(subset = 'pagare_fincore', inplace = True)
vigentes['Celular'] = vigentes['Celular'].str.strip()


# este parseador es perfecto y una de mis mejores creaciones de todos los tiempos
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
vigentes['FECHA NAC'] = vigentes['FECHA NAC'].apply(parse_date)

#%%
col_necesarias = vigentes[['codigosocio',
                           'APELLIDOS NOMBRES / RAZÓN SOCIAL',
                           'FECHA NAC',
                           #'DOCUMENTO',
                           'pagare_fincore',
                           'fechadesembolso',
                           #'Otorgado',
                           #'moneda',
                           'Funcionario',
                           'Celular',
                           'Email',
                           'distrito', 
                           'provincia', 
                           'departamento']]

# col_necesarias.drop_duplicates(subset = 'DOCUMENTO', inplace = True)

def cel_51(celular):
    if (celular[0] == '9') and (len(celular) == 9):
        return '+51' + celular
    elif celular[:2] == '51':
        return '+' + celular
    else:
        return 0

col_necesarias['Celular1'] = col_necesarias['Celular'].apply(cel_51)

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
    WHERE FechaCorte1 = '{fecha_corte}'
    ORDER BY ApellidosyNombresRazonSocial2

    '''
    anexo_06 = pd.read_sql_query(query, conn)
    
#%%
anexo_06_completado = anexo_06.merge(col_necesarias[['DOCUMENTO',
                                                 'Celular1',
                                                 'Funcionario',
                                                 'Email',
                                                 'distrito', 
                                                 'provincia', 
                                                 'departamento']],

                                 on     = 'DOCUMENTO',
                                 how    = 'inner')

#%% mes faltante para el anexo 06
from datetime import datetime, timedelta

def obtener_siguiente_dia(fecha_str):
    # Convertir la cadena de fecha al formato datetime
    fecha = datetime.strptime(fecha_str, '%Y%m%d')
    # Sumar un día
    siguiente_dia = fecha + timedelta(days=1)
    return siguiente_dia

# Obtener el siguiente día
resultado = obtener_siguiente_dia(fecha_corte)

dias_faltantes = vigentes[vigentes['fechadesembolso'] >= resultado]

dias_faltantes

['codigosocio', 'APELLIDOS NOMBRES / RAZÓN SOCIAL', 'FECHA NAC',
'PRODUCTO', 'DÍAS DE MORA', 'ESTADO',
       'Celular1', 'Funcionario', 'Email', 'distrito', 'provincia',
       'departamento'],

