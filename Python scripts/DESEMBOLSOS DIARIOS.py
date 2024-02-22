# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 09:04:46 2024

@author: Joseph Montoya
"""
# =============================================================================
#                            DESEMBOLSOS DIARIOS
# =============================================================================

import pandas as pd
from datetime import datetime #, timedelta
import pyodbc
import os
#%%
corte_actual      = '20240229'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\DIANA LORENA\\montos desembolsados diarios')

tabla             = '[DESEMBOLSOS_DIARIOS].[dbo].[2024_02]'
tabla_acumulada   = '[DESEMBOLSOS_DIARIOS].[dbo].[2024_02_acum]'

CARGA_SQL_SERVER  = False #True o False

crear_excel       = False #True o False

#%%
# Crear una lista de fechas para el año 2024
fechas_2024 = pd.date_range(start='2024-01-01', end = '2024-12-31')

# Crear un DataFrame con las fechas
df = pd.DataFrame({'Fecha': fechas_2024})

# Agregar una columna que indique el día de la semana
df['Dia de la semana'] = df['Fecha'].dt.day_name()

#%%
# Lista de feriados
feriados = ['01-01-2024',
            '28-03-2024',
            '29-03-2024',
            '01-05-2024',
            '07-06-2024',
            '29-06-2024',
            '23-07-2024',
            '26-07-2024',
            '28-07-2024',
            '29-07-2024',
            '06-08-2024',
            '30-08-2024',
            '07-10-2024',
            '08-10-2024',
            '01-11-2024',
            '06-12-2024',
            '08-12-2024',
            '09-12-2024',
            '23-12-2024',
            '24-12-2024',
            '25-12-2024',
            '30-12-2024',
            '31-12-2024']

# Convertir fechas de feriados a formato datetime
feriados = [datetime.strptime(fecha, '%d-%m-%Y') for fecha in feriados]

# Función para etiquetar días no laborales
def dia_no_laboral(fecha):
    if fecha in feriados:
        return 'no laboral'
    elif fecha.weekday() == 6:  # Domingo
        return 'no laboral'
    else:
        return 'laboral'

# Aplicar función a DataFrame
df['dia no laboral'] = df['Fecha'].apply(dia_no_laboral)

#%% Año 2023
# Crear una lista de fechas para el año 2024
fechas_2023 = pd.date_range(start='2023-01-01', end = '2023-12-31')

# Crear un DataFrame con las fechas
df_anterior = pd.DataFrame({'Fecha': fechas_2023})

# Agregar una columna que indique el día de la semana
df_anterior['Dia de la semana'] = df_anterior['Fecha'].dt.day_name()

#%%
# Lista de feriados
feriados_2023 = ['01-01-2023',
                 '06-04-2023',
                 '07-04-2023',
                 '01-05-2023',
                 '29-06-2023',
                 '28-07-2023',
                 '29-07-2023',
                 '06-08-2023',
                 '30-08-2023',
                 '08-10-2023',
                 '01-11-2023',
                 '08-12-2023',
                 '09-12-2023',
                 '25-12-2023' ]

# Convertir fechas de feriados a formato datetime
feriados_2023 = [datetime.strptime(fecha, '%d-%m-%Y') for fecha in feriados_2023]

# Función para etiquetar días no laborales
def dia_no_laboral(fecha):
    if fecha in feriados_2023:
        return 'no laboral'
    elif fecha.weekday() == 6:  # Domingo
        return 'no laboral'
    else:
        return 'laboral'

# Aplicar función a DataFrame
df_anterior['dia no laboral'] = df_anterior['Fecha'].apply(dia_no_laboral)

#%% enumeración de días laborales (año actual)
# Obtener el año y el mes de cada fecha
df['Año'] = df['Fecha'].dt.year
df['Mes'] = df['Fecha'].dt.month

# Crear una columna para enumerar los días laborales por mes
df['Numero de dia laboral'] = 0

# Enumerar los días laborales por mes
for year_month, group in df.groupby(['Año', 'Mes']):
    laboral_count = 0
    for idx, row in group.iterrows():
        if row['dia no laboral'] == 'laboral':
            laboral_count += 1
            df.at[idx, 'Numero de dia laboral'] = laboral_count

#%% enumeración de días laborales (año anterior)
# Obtener el año y el mes de cada fecha
df_anterior['Año'] = df_anterior['Fecha'].dt.year
df_anterior['Mes'] = df_anterior['Fecha'].dt.month

# Crear una columna para enumerar los días laborales por mes
df_anterior['Numero de dia laboral'] = 0

# Enumerar los días laborales por mes
for year_month, group in df_anterior.groupby(['Año', 'Mes']):
    laboral_count = 0
    for idx, row in group.iterrows():
        if row['dia no laboral'] == 'laboral':
            laboral_count += 1
            df_anterior.at[idx, 'Numero de dia laboral'] = laboral_count

#%% Numeración concatenada

dias_laborales = pd.concat([df,df_anterior], ignore_index = True)

#%% 
# =============================================================================
#                             DESEMBOLSOS DIARIOS
# =============================================================================

#%% usuario SQL fincore
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%%

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

query = f'''
-- p.codcategoria = 351 -> nuevo
-- p.codcategoria = 352 -> ampliacion
-- p.codestado = 563 -> anulado
-- p.codestado = 341 -> pendiente
-- p.codestado = 342 -> cancelado
-- tc.CODTIPOCREDITO -> ( 3=Cons.Ordinario / 1=Med.Empresa / 2=MicroEmp. / 9=Peq.Empresa)
DECLARE @FECHA_MES AS DATETIME = '{corte_actual}'

DECLARE @fechaAnterior AS DATETIME;
SET @fechaAnterior = EOMONTH(DATEADD(MONTH, -1, EOMONTH(CONVERT(DATETIME, @FECHA_MES, 112))));

DECLARE @fecha12MESES AS DATETIME;
SET @fecha12MESES = EOMONTH(DATEADD(MONTH, -12, EOMONTH(CONVERT(DATETIME, @FECHA_MES, 112))));

SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad', 
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso,
	DAY(p.fechadesembolso) AS 'Día del mes',
	DATENAME(dw, p.fechadesembolso) AS dia_semana,
	
	CASE DATEPART(WEEKDAY, p.fechadesembolso)
        WHEN 1 THEN 'domingo '
        WHEN 2 THEN 'lunes '
        WHEN 3 THEN 'martes '
        WHEN 4 THEN 'miércoles '
        WHEN 5 THEN 'jueves '
        WHEN 6 THEN 'viernes '
        WHEN 7 THEN 'sábado '
    END +
    CAST((DATEPART(DAY, p.fechadesembolso) - 1) / 7 + 1 AS VARCHAR) AS dia_numero,	
	
	CASE	
		WHEN (MONTH(p.fechadesembolso) = MONTH(@FECHA_MES)		
		AND   YEAR(p.fechadesembolso) =	YEAR(@FECHA_MES)) THEN 'MES ACTUAL'
		WHEN MONTH(p.fechadesembolso) = MONTH(@fechaAnterior)	THEN 'MES ANTERIOR'
		WHEN MONTH(p.fechadesembolso) = MONTH(@fecha12MESES)    THEN 'MES hace un año'
	ELSE 'INVESTIGAR'
	END AS 'MES COMPARACIÓN',
	p.montosolicitado as 'Otorgado', 
	p.TEM, 
	p.NroPlazos, 
	tm.descripcion as 'Estado',
	p.fechaCancelacion, 
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado, 
	pro.descripcion as 'Funcionario',
	CASE
		WHEN pro.descripcion LIKE '%PROSEVA%' THEN pro.descripcion
				WHEN 
		(PRO.DESCRIPCION LIKE '%ADOLFO%HUAMAN%'
		OR PRO.DESCRIPCION LIKE '%CESAR%MEDINA%'
		OR PRO.DESCRIPCION LIKE '%DAYANA%CHIRA%'
		OR PRO.DESCRIPCION LIKE '%ESTHER%RAMIR%'
		OR PRO.DESCRIPCION LIKE '%JESSICA%SOLOR%'
		OR PRO.DESCRIPCION LIKE '%JESICA%SOLOR%'
		OR PRO.DESCRIPCION LIKE '%JORGE%ARAG%'
		OR PRO.DESCRIPCION LIKE '%MARIBEL%PUCH%') THEN 'AREQUIPA'
				WHEN
		(PRO.DESCRIPCION LIKE '%ALEJANDRO%HUAMAN%'
		OR PRO.DESCRIPCION LIKE '%ANA%GUERR%'
		OR PRO.DESCRIPCION LIKE '%ANT%OSORIO%'
		OR PRO.DESCRIPCION LIKE '%EDUAR%TITO%'
		OR PRO.DESCRIPCION LIKE '%ELBER%ALVA%'
		OR PRO.DESCRIPCION LIKE '%FIGARI%VEG%'
		OR PRO.DESCRIPCION LIKE '%GINO%PALO%'
		OR PRO.DESCRIPCION LIKE '%GRICERIO%NU%'
		OR PRO.DESCRIPCION LIKE '%JEAN%BRAV%'
		OR PRO.DESCRIPCION LIKE '%JIMN%MENDO%'
		OR PRO.DESCRIPCION LIKE '%KELLY%HUAM%'
		OR PRO.DESCRIPCION LIKE '%MAR%MARTINE%'
		OR PRO.DESCRIPCION LIKE '%MARTIN%VILCA%'
		OR PRO.DESCRIPCION LIKE '%PAMELA%GARC%'
		OR PRO.DESCRIPCION LIKE '%SUSAN%ROJAS%'
		OR PRO.DESCRIPCION LIKE '%VICTOR%FARFA%'
		OR PRO.DESCRIPCION LIKE '%YESENIA%POTENC%'
		--OR PRO.DESCRIPCION LIKE '%YULAISE%MOREANO%'
		OR PRO.DESCRIPCION LIKE '%GERENCIA%'
		OR PRO.DESCRIPCION LIKE '%LUIS%BUSTAMAN%'
		OR PRO.DESCRIPCION LIKE '%JONAT%ESTRADA%'
		OR PRO.DESCRIPCION LIKE '%GRUPO%'
		OR PRO.DESCRIPCION LIKE '%DAVID%BORJ%'
		OR PRO.DESCRIPCION LIKE '%VICTOR%VARGA%'
		OR PRO.DESCRIPCION LIKE '%BORIS%CAMARGO%'
		) THEN 'LIMA'
				WHEN
		(PRO.DESCRIPCION LIKE '%YULAISE%MOREANO%'
		OR PRO.DESCRIPCION LIKE '%JESUS%CERVERA%'
		OR PRO.DESCRIPCION LIKE '%EDISON%FLORES%'
		) THEN 'SANTA ANITA'
				WHEN 
		(PRO.DESCRIPCION LIKE '%JESSICA%PISCOYA%'
		OR PRO.DESCRIPCION LIKE '%JOSE%SANCHE%'
		OR PRO.DESCRIPCION LIKE '%MILTON%JUARE%'
		OR PRO.DESCRIPCION LIKE '%PAULO%SARE%'
		OR PRO.DESCRIPCION LIKE '%ROY%NARVAE%'
		) THEN 'TRUJILLO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%CESAR%MERA%'
		OR PRO.DESCRIPCION LIKE '%WILLIAMS%TRAUCO%'
		) THEN 'TARAPOTO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%JHONY%SALDA%'
		) THEN 'RESTO DE CARTERA PROVINCIA'
	WHEN  FI.CODIGO IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29) THEN 'INVESTIGAR'
	ELSE 'NO ES MYPE'
		END AS 'ZONAS mype',

	d.nombre as 'distrito', 
	pv.nombre as 'provincia', 
	dp.nombre as 'departamento', 
	iif(s.codigosocio>28790,'SOC.NVO', 'SOC.ANT') AS 'tipo_soc',
	tm3.Descripcion as 'Situacion', 
	p.fechaventacartera, 
	tc.Descripcion as 'TipoCredito', 
	FI.CODIGO AS 'COD_FINALIDAD',
    
	CASE
		WHEN FI.CODIGO IN (34,35,36,37,38,39) THEN 'DXP'
        WHEN FI.CODIGO IN (32) THEN 'MULTIOFICIOS'
		WHEN FI.CODIGO IN (30,31,32,33) THEN 'LD'
		WHEN FI.CODIGO IN (21,22,23,24,25,27,28,29) THEN 'MICROEMPRESA'
		WHEN FI.CODIGO IN (26) THEN 'EMPRENDEMUJER'
		WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑAEMPRESA'
		WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANAEMPRESA'
		WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIO'
	ELSE 'INVESTIGAR CASO'
	END AS 'PRODUCTO43',
	
    FI.DESCRIPCION AS 'FINALIDAD'
FROM prestamo as p

INNER JOIN socio             AS s    on s.codsocio = p.codsocio
LEFT JOIN sociocontacto      AS sc   on sc.codsocio = s.codsocio
LEFT JOIN planilla           AS pla  on p.codplanilla = pla.codplanilla
INNER JOIN grupocab          AS pro  on pro.codgrupocab = p.codgrupocab
INNER JOIN distrito          AS d    on d.coddistrito = sc.coddistrito
INNER JOIN provincia         AS pv   on pv.codprovincia = d.codprovincia
INNER JOIN departamento      AS dp   on dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet   AS tm   on tm.codtabladet = p.CodEstado
LEFT JOIN grupocab           AS gpo  on gpo.codgrupocab = pla.codgrupocab
LEFT JOIN tablaMaestraDet    AS tm2  on tm2.codtabladet = s.codestadocivil
LEFT JOIN tablaMaestraDet    AS tm3  on tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet AS tm3  On tm3.codtabladet = s.codcategoria
INNER JOIN pais on pais.codpais = s.codpais
LEFT JOIN FINALIDAD          AS FI   ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN TipoCredito        AS TC   on tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN usuario           AS u    on p.CodUsuario = u.CodUsuario
INNER JOIN TablaMaestraDet   AS tm4  on s.codestado = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota    AS pcu  on p.CodPrestamo = pcu.CodPrestamo

WHERE
 
    (EOMONTH(CONVERT(VARCHAR(10),p.fechadesembolso,112))    = @FECHA_MES
    OR EOMONTH(CONVERT(VARCHAR(10),p.fechadesembolso,112))  = @fechaAnterior
    OR EOMONTH(CONVERT(VARCHAR(10),p.fechadesembolso,112))  = @fecha12MESES)

AND s.codigosocio>0

ORDER BY p.fechadesembolso desc, Socio ASC

'''

df_fincore = pd.read_sql_query(query, conn)

df_fincore['fechadesembolso'] = df_fincore['fechadesembolso'].dt.date
df_fincore['fechadesembolso'] = pd.to_datetime(df_fincore['fechadesembolso'])

#%% MERGE CON EL NRO DE DÍA LABORAL

union = df_fincore.merge(dias_laborales[dias_laborales['Numero de dia laboral'] != 0], # union solo con los días laborales
                         left_on  = 'fechadesembolso',
                         right_on = 'Fecha',
                         how      = 'left')
del union['Fecha']

print('Debe salir cero:')
print(union[pd.isna(union['Numero de dia laboral'])].shape[0])
if union[pd.isna(union['Numero de dia laboral'])].shape[0] > 0:
    print('Si no sale cero, es porque se ha desembolsado en una fecha que no es laboral')

#%% EXCEL
union = union[['codigosocio', 
               'Socio', 
               'Doc_Identidad', 
               'pagare_fincore', 
               'moneda',
               'fechadesembolso', 
               #'Día del mes', 
               #'dia_semana', 
               #'dia_numero',
               'MES COMPARACIÓN', 
               'Otorgado', 
               'TEM', 
               #'NroPlazos', 
               #'Estado',
               #'fechaCancelacion', 
               'tipo_pre', 
               #'flagrefinanciado', 
               'Funcionario',
               'ZONAS mype', 
               #'distrito', 
               #'provincia', 
               #'departamento', 
               #'tipo_soc',
               #'Situacion', 
               #'fechaventacartera', 
               #'TipoCredito', 
               'COD_FINALIDAD',
               #'PRODUCTO43',
               #'FINALIDAD', 
               #'Dia de la semana', 
               #'dia no laboral', 
               #'Año',
               #'Mes',
               'Numero de dia laboral']]

union['FechaCorte'] = pd.to_datetime(corte_actual, format='%Y%m%d')

#%%
if crear_excel == True:
    union.to_excel('Desembolsos diarios.xlsx',
    index = False)
else:
    pass

#%% CARGA A SQL DE LOS DESEMBOLSOS DIARIOS
if CARGA_SQL_SERVER == True:
    
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    df = union.copy()

    # Limpiar la tabla antes de insertar nuevos datos
    cursor.execute(f"DELETE FROM {tabla}")
    
    for index, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {tabla}
            ( [codigosocio],       
              [Funcionario],
              [Socio],             
              [ZONAS mype],
              [Doc_Identidad],      
              [pagare_fincore],     
              [moneda],
              [fechadesembolso],
              [MES COMPARACIÓN],
              [COD_FINALIDAD],
              [Otorgado],           
              [TEM],                
              [tipo_pre],           
              [Numero de dia laboral],
              [FechaCorte])
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        row['codigosocio'],
        row['Funcionario'],
        row['Socio'],
        row['ZONAS mype'],
        row['Doc_Identidad'],
        row['pagare_fincore'],
        row['moneda'],
        row['fechadesembolso'],
        row['MES COMPARACIÓN'],
        row['COD_FINALIDAD'],
        row['Otorgado'],
        row['TEM'],
        row['tipo_pre'],
        row['Numero de dia laboral'],
        row['FechaCorte']
        )

    cnxn.commit()
    cursor.close()
    
    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    
else:
    print('No se ha cargado a SQL SERVER')

#%% DATOS ACUMULADOS
# ¿CREAR DATAFRAME ULTRA MASIVO? 🤔
acum = union.head(0)
acum['dia acumulado'] = 0

for i in range(0,(union['Numero de dia laboral'].unique().max())):
    para_filtrar = union.copy()
    para_filtrar = para_filtrar[para_filtrar['Numero de dia laboral'] <= i+1]
    para_filtrar['dia acumulado'] = i+1
    acum = pd.concat([acum,para_filtrar], ignore_index = True)

#%% a excel

if crear_excel ==  True:
    acum.to_excel('acumulado.xlsx',
                  index = False)
else:
    pass

#%% CARGA A SQL DE LOS DESEMBOLSOS ACUMULADOS
if CARGA_SQL_SERVER == True:
    
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    df = acum.copy()

    # Limpiar la tabla antes de insertar nuevos datos
    cursor.execute(f"DELETE FROM {tabla_acumulada}")
    
    for index, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {tabla}
            ( [codigosocio],       
              [Funcionario],
              [Socio],             
              [ZONAS mype],
              [Doc_Identidad],      
              [pagare_fincore],     
              [moneda],
              [fechadesembolso],
              [MES COMPARACIÓN],
              [COD_FINALIDAD],
              [Otorgado],           
              [TEM],                
              [tipo_pre],           
              [Numero de dia laboral],
              [FechaCorte],
              [dia acumulado])
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        row['codigosocio'],
        row['Funcionario'],
        row['Socio'],
        row['ZONAS mype'],
        row['Doc_Identidad'],
        row['pagare_fincore'],
        row['moneda'],
        row['fechadesembolso'],
        row['MES COMPARACIÓN'],
        row['COD_FINALIDAD'],
        row['Otorgado'],
        row['TEM'],
        row['tipo_pre'],
        row['Numero de dia laboral'],
        row['FechaCorte'],
        row['dia acumulado']
        )

    cnxn.commit()
    cursor.close()
    
    print(f'Se cargaron los datos a SQL SERVER {tabla_acumulada}')
    
else:
    print('No se ha cargado a SQL SERVER')

