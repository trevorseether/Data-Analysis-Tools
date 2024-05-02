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
fecha_corte = '20240331'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\socios con vigentes')

#%% LECTURA DE LAS CREDENCIALES
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%% CREACIÓN DE LA CONECCIÓN A SQL

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#%% QUERY, créditos vigentes
query = '''
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
	s.fechanacimiento, 
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
	s.FechaNacimiento, 
	s.fechaInscripcion, 
	u.IdUsuario as 'User_Desemb', 
	tm4.descripcion as 'EstadoSocio'
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

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'
AND s.codigosocio>0  

AND p.codestado = 341 --SIGNFICA QUE EL CRÉDITO SE ENCUENTRE EN SITUACIÓN VIGENTE

order by socio asc, p.fechadesembolso desc

'''

vigentes = pd.read_sql_query(query, 
                             conn, 
                             dtype = {'Doc_Identidad'  : object,
                                      'codigosocio'    : object,
                                      'pagare_fincore' : object,
                                      'fechadesembolso': object,
                                      'Celular'        : str
                                      })
del conn
vigentes.drop_duplicates(subset = 'pagare_fincore', inplace = True)
vigentes['Celular'] = vigentes['Celular'].str.strip()

#%%
col_necesarias = vigentes[['Socio',
                           'Doc_Identidad',
                           #'pagare_fincore',
                           #'fechadesembolso',
                           #'Otorgado',
                           #'moneda',
                           'Celular',
                           'Email']]

col_necesarias.drop_duplicates(subset = 'Doc_Identidad', inplace = True)

def cel_51(celular):
    if (celular[0] == '9') and (len(celular) == 9):
        return '+51' + celular
    elif celular[:2] == '51':
        return '+' + celular
    else:
        return 0

col_necesarias['Celular1'] = col_necesarias['Celular'].apply(cel_51)


#%% ANEXO 06
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
SELECT 
	ApellidosyNombresRazonSocial2 AS 'APELLIDOS NOMBRES / RAZÓN SOCIAL',
    FechadeNacimiento3 as 'FECHA NAC',
	NumerodeDocumento10 AS 'DOCUMENTO', 
	TipodeDocumento9 AS 'TIPO DOC',
	CASE
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LIBRE DISPONIBILIDAD'
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeProducto43 IN (21,22,23,24,25,26,27,28,29) THEN 'MICRO EMPRESA'
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
base_completada = anexo_06.merge(col_necesarias[['Doc_Identidad',
                                                 'Celular1',
                                                 'Email']],
                                 left_on  = 'DOCUMENTO',
                                 right_on = 'Doc_Identidad',
                                 how      = 'inner')

#%% excel
base_completada.to_excel(f'base vigentes {fecha_corte}.xlsx',
                         index = False)

