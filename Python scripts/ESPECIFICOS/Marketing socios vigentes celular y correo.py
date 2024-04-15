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
fecha_hoy = '20241504'

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
query = f'''
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
FROM prestamo as p

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

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) 
BETWEEN '20110101' AND '{fecha_hoy}' 
AND s.codigosocio>0  

AND p.codestado = 341 --SIGNFICA QUE EL CRÉDITO SE ENCUENTRE EN SITUACIÓN VIGENTE

order by socio asc, p.fechadesembolso desc

'''

vigentes = pd.read_sql_query(query, 
                             conn, 
                             dtype = {'Doc_Identidad'  : object,
                                      'codigosocio'    : object,
                                      'pagare_fincore' : object,
                                      'fechadesembolso': object
                                      })
del conn
vigentes.drop_duplicates(subset = 'pagare_fincore', inplace = True)

#%%
col_necesarias = vigentes[['Socio',
                           'Doc_Identidad',
                           #'pagare_fincore',
                           #'fechadesembolso',
                           #'Otorgado',
                           #'moneda',
                           'celular1',
                           'Email']]

col_necesarias.drop_duplicates(subset = 'Doc_Identidad', inplace = True)

#%%
col_necesarias.to_excel('vigentes cel correo.xlsx',
                        index = False)

