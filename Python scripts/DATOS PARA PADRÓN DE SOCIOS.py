# -*- coding: utf-8 -*-
"""
Created on Tue May 14 10:59:58 2024

@author: Joseph Montoya
"""
# =============================================================================
# DATOS EXTRAS PARA REPORTE 
# =============================================================================
import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS
fecha_corte = '20240430' # formato para sql server

#%% LECTURA PADRÓN DE SOCIOS
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\PADRÓN DE SOCIOS\\2024 ABRIL')

#%%
padron = pd.read_excel('Rpt_PadronSocios Abril-24 Ampliado - incl inhabiles.xlsx',
                       skiprows = 1,
                       dtype = {'CodSoc'                  : str,
                                'Celular1'                : str,
                                'NO ENCONT EN RPT APORTE' : str
                                })

#%% LECTURA ANEXO06 DEL SQL
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
SELECT
	FechaCorte1,
	Nro_Fincore, 
	ApellidosyNombresRazonSocial2,
    CodigoSocio7,
    NumerodeDocumento10,
	MontodeDesembolso22,
	FechadeDesembolso21,
	Saldodecolocacionescreditosdirectos24,
	CapitalVencido29,
	CapitalenCobranzaJudicial30,
	SaldosdeCreditosCastigados38,
	ProvisionesConstituidas37,
	ProvisionesRequeridas36,
	originador, administrador,
	PLANILLA, NUEVA_PLANILLA,
	TipodeProducto43,
	CASE
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LD'
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeProducto43 IN (20,21,22,23,24,25,29) THEN 'MICRO EMPRESA'
		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIA'
		END AS 'PRODUCTO TXT'
FROM
	anexos_riesgos3..anx06
WHERE 
	FechaCorte1 = '{fecha_corte}'

'''
anexo_06 = pd.read_sql_query(query, conn)
del conn

#%% COLUMNA ESTADO

padron['CodSoc'] = padron['CodSoc'].str.strip()
anexo_06['CodigoSocio7'] = anexo_06['CodigoSocio7'].str.strip()
codigos_anexo_06 = set(anexo_06['CodigoSocio7'])

def estado(padron):
    if padron['CodSoc'] in codigos_anexo_06:
        return 'ACTIVO'
    else:
        return 'INACTIVO'
padron['ESTADO'] = padron.apply(estado, axis = 1)

#%% LECTURA DE SQL SERVER

datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
select 	
	s.codigosocio as 'CodSoc',
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	s.fechanacimiento,
	DATEDIFF(year, s.fechanacimiento, '20240331') AS Edad,
	tm2.descripcion as 'est_civil',
	C.INGRESOBRUTO,
	B.DESCRIPCION AS 'GradoInstrucción'    
	--,	*
from Socio as S
	LEFT JOIN tablaMaestraDet AS tm2 ON tm2.codtabladet = s.codestadocivil
	LEFT JOIN PLANILLASOCIO AS C     ON s.CODSOCIO = C.CODSOCIO
	LEFT JOIN tablaMaestraDet AS B   ON s.CODINSTRUCCION = B.CODTABLADET
'''

datos_para_padron = pd.read_sql_query(query, conn)
# datos_para_padron['INGRESOBRUTO'] = datos_para_padron['INGRESOBRUTO'].fillna(0)
datos_para_padron = datos_para_padron.sort_values(by        = 'INGRESOBRUTO',
                                                  ascending = False)
datos_para_padron.drop_duplicates(subset  = 'CodSoc',
                                  keep    = 'first', 
                                  inplace = True)

#%% MERGE DE LOS DATOS
padron2 = padron.merge(datos_para_padron[['CodSoc', 'Edad', 'est_civil', 'INGRESOBRUTO', 'GradoInstrucción']],
                       on  = 'CodSoc',
                       how = 'left')

#%% LECTURA DE CRÉDITOS OTORGADOS
query = '''
SELECT
	s.codigosocio as 'CodSoc', 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	p.montosolicitado as 'Otorgado',
    FI.CODIGO AS 'COD_FINALIDAD',
	CASE
		WHEN FI.CODIGO IN (34,35,36,37,38,39)			THEN 'DXP'
		WHEN FI.CODIGO IN (30,31,32,33)					THEN 'LIBRE DISPONIBILIDAD'
		WHEN FI.CODIGO IN (41,45)						THEN 'HIPOTECARIO'
		WHEN FI.CODIGO IN (15,16,17,18,19)				THEN 'PEQUEÑA EMPRESA'
		WHEN FI.CODIGO IN (21,22,23,24,25,26,27,28,29)  THEN 'MICRO EMPRESA'
		WHEN FI.CODIGO IN (95,96,97,98,99)				THEN 'MEDIANA EMPRESA'
		ELSE 'INVESTIGAR'
		
		END AS 'PRODUCTO_TXT',
	FI.DESCRIPCION

FROM prestamo AS p

    INNER JOIN socio AS S ON s.codsocio = p.codsocio
    LEFT JOIN FINALIDAD AS FI ON FI.CODFINALIDAD = P.CODFINALIDAD
WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) between '20010101' and '20240331'

	AND s.codigosocio > 0
	AND p.montosolicitado > 0

ORDER BY socio ASC, p.fechadesembolso DESC

'''

total_creditos = pd.read_sql_query(query, conn)
total_creditos.drop_duplicates(subset  = 'pagare_fincore',
                               keep    = 'first', 
                               inplace = True)

#%% LOS GROUPS
num_cred = total_creditos.pivot_table(values  = 'pagare_fincore',
                                      index   = 'CodSoc',
                                      aggfunc = 'count').reset_index()
num_cred.rename(columns = {'pagare_fincore':'número de créditos'}, inplace = True)

promedio_otorgado = total_creditos.pivot_table(values  = 'Otorgado',
                                               index   = 'CodSoc',
                                               aggfunc = 'mean').reset_index()
promedio_otorgado.rename(columns = {'Otorgado':'Promedio otorgado'}, inplace = True)
promedio_otorgado['Promedio otorgado'] = promedio_otorgado['Promedio otorgado'].round(2)

#%% MERGE FINAL
padron3 = padron2.merge(num_cred,
                        on  = 'CodSoc',
                        how = 'left')

padron3 = padron3.merge(promedio_otorgado,
                        on  = 'CodSoc',
                        how = 'left')

#%% COLUMNAS NECESARIAS
padron_final = padron3[['CodSoc',
                        'ESTADO',
                        'Edad', 
                        'est_civil',
                        'INGRESOBRUTO',
                        'número de créditos',
                        'Promedio otorgado',
                        'GradoInstrucción', 
                        ]]

padron_final.columns = ['CodSoc', 
                        'ESTADO',
                        'EDAD', 
                        'ESTADO CIVIL',
                        'INGRESO BRUTO', 
                        'NÚMERO DE CRÉDITOS',
                        'MONTO OTORGADO PROMEDIO',
                        'GRADO DE INSTRUCCIÓN']

padron_final.to_excel('datos_para_padron.xlsx',
                       index = False)

#%%
# import matplotlib.pyplot as plt

# # Suponiendo que df es tu DataFrame y 'columna' es el nombre de la columna numérica
# plt.hist(padron3['número de créditos'], bins=50, color='skyblue', edgecolor='black')
# plt.xlabel('Valores')
# plt.ylabel('Frecuencia')
# plt.title('Distribución de la columna')
# plt.show()

#%% 
archivo_original = padron3[['CodSoc', 'Apellidos y Nombres', 'Aporte Inicial', 'Aporte\nCobranza',
       'Aporte \nExtraOrd.', 'Reduccion', 'Aporte\nFinal', 'Ultima\nOperacion',
       'Ultima\nOperacion Aportes', 'Fecha Inscripcion TSocio', 'Ocupacion',
       'Tipo Persona TXT', 'Tipo Documento TXT', 'Nro Doc Identidad Unificado',
       'Direccion Completa', 'Distrito', 'Departamento', 'Provincia', 'Ubigeo',
       'Actividad Economica', 'Sexo', 'Nacionalidad TXT',
       'Fecha Primer Prestamo', 'Email', 'Celular1', 'Telefono Fijo1',
       'Condicion', 'Fecha Ultimo Desembolso', 'Fecha Bloqueo', 
       
       'ESTADO','Edad','est_civil','INGRESOBRUTO','número de créditos','Promedio otorgado','GradoInstrucción'
]]

# merge con el crédito
archivo_original = archivo_original.merge(total_creditos[['CodSoc', 'pagare_fincore', 'Otorgado', 'PRODUCTO_TXT']],
                                          on  = 'CodSoc',
                                          how = 'left')

archivo_original.to_excel('padrón de créditos.xlsx',
                          index = False)

