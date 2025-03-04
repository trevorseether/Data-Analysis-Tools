# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 09:04:46 2024

@author: Joseph Montoya
"""
# =============================================================================
#                            DESEMBOLSOS DIARIOS
# =============================================================================

import pandas as pd
from   datetime import datetime #, timedelta
from   datetime import date
import pyodbc
import os

import warnings
warnings.filterwarnings('ignore')

#%%
corte_actual      = '20241231' #FUNCIONARÁ DESDE '20240229' EN ADELANTE

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\DIANA LORENA\\montos desembolsados diarios')

tabla             = '[DESEMBOLSOS_DIARIOS].[dbo].[2024_12]'
tabla_acumulada   = '[DESEMBOLSOS_DIARIOS].[dbo].[2024_12_acum]'

CARGA_SQL_SERVER  = True #True o False

crear_excel       = False #True o False

incluir_hoy       = False #True o False

#%%
# Crear una lista de fechas para el año 2024
fechas_2024 = pd.date_range(start = '2024-01-01', end = '2024-12-31')

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
            #'26-07-2024',
            '28-07-2024',
            '29-07-2024',
            '06-08-2024',
            '30-08-2024',
            '08-10-2024',
            '01-11-2024',
            #'06-12-2024',
            '08-12-2024',
            '09-12-2024',
            #'23-12-2024',
            '24-12-2024',
            '25-12-2024',
            #'30-12-2024',
            #'31-12-2024'
            ]

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
fechas_2023 = pd.date_range(start = '2023-01-01', end = '2023-12-31')

# Crear un DataFrame con las fechas
df_anterior = pd.DataFrame({'Fecha': fechas_2023})

# Agregar una columna que indique el día de la semana
df_anterior['Dia de la semana'] = df_anterior['Fecha'].dt.day_name()

#%%
# Lista de feriados
feriados_2023 = ['01-01-2023',
                 '01-04-2023',
                 '06-04-2023',
                 '07-04-2023',
                 '08-04-2023',
                 #'01-05-2023', # extrañamente, han colocado créditos en esta fecha a pesar de ser feriado
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
    elif fecha.weekday() == 6:  # 6 es Domingo
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

#%% Fecha de hoy para incluir o no el día de hoy

if incluir_hoy == True:
    fecha_hoy_sql = '20501231' # fecha arbitrariamente lejana
else:
    fecha_hoy_sql = str(date.today())
    fecha_hoy_sql = fecha_hoy_sql[0:4] + fecha_hoy_sql[5:7] + fecha_hoy_sql[8:10]

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
        WHEN 1 THEN 'lunes '
        WHEN 2 THEN 'martes '
        WHEN 3 THEN 'miércoles '
        WHEN 4 THEN 'jueves '
        WHEN 5 THEN 'viernes '
        WHEN 6 THEN 'sábado '
        WHEN 7 THEN 'domingo '
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
--------------------------------------<<<<<<<<<<<<<<<<<<<<	
	p.flagrefinanciado,
	CASE
		WHEN (P.CodEstado<>563) and (flagRefinanciado=1 or (p.CodSolicitudCredito =0)) THEN 'REFINANCIADO'
		ELSE 'normal'
		END AS 'REFINANCIAMIENTO_txt',
--------------------------------------<<<<<<<<<<<<<<<<<<<<	
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
		OR PRO.DESCRIPCION LIKE '%MARIBEL%PUCH%'
        
		OR PRO.DESCRIPCION LIKE '%CHRISTIAN LLERENA%'
		OR PRO.DESCRIPCION LIKE '%JORGE%ARAGON%'
		OR PRO.DESCRIPCION LIKE '%ESTHER%RAMIREZ%'
		OR PRO.DESCRIPCION LIKE '%ESTHER%RODRIGUE%'
		OR PRO.DESCRIPCION LIKE '%MARIA%CRISTINA%MARTINEZ%'
		OR PRO.DESCRIPCION LIKE '%HAROLD%RAMO%'
		OR PRO.DESCRIPCION LIKE '%RILDO%URRUTIA%'
		OR PRO.DESCRIPCION LIKE '%MARISOL%CHOQUE%HUARICA%'
		OR PRO.DESCRIPCION LIKE '%LILIANA%CHILO%REA%'
		OR PRO.DESCRIPCION LIKE '%DONNY%CHAVE%'
		OR PRO.DESCRIPCION LIKE '%ADMIN%AREQUIP%' ) 
            THEN 'AREQUIPA'
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
			OR PRO.DESCRIPCION LIKE '%ANTHON%OSORIO%'
			OR PRO.DESCRIPCION LIKE '%YULAISE%MORE%' 
			OR PRO.DESCRIPCION LIKE '%MIGUEL%TELLO%'
			OR PRO.DESCRIPCION LIKE '%MARTIN%VILCA%'
			OR PRO.DESCRIPCION LIKE '%GRICERI%NU%BA%'
			OR PRO.DESCRIPCION LIKE '%ANA%GUERRA%SOL%'
			OR PRO.DESCRIPCION LIKE '%GIANELLA%GIOVA%'
			OR PRO.DESCRIPCION LIKE '%GINO%PALOMINO%'
			OR PRO.DESCRIPCION LIKE '%JENN%PACHE%'
			OR PRO.DESCRIPCION LIKE '%JESUS%ERVER%'
			OR PRO.DESCRIPCION LIKE '%JENNYFER%PACHER%'
			OR PRO.DESCRIPCION LIKE '%ROXANA%BENITE%MENE%'
			OR PRO.DESCRIPCION LIKE '%HUGO%MARCHAN%'
			OR PRO.DESCRIPCION LIKE '%WILLIAM%FRANK%FLORE%SUA%'
			OR PRO.DESCRIPCION LIKE '%ADMIN%S%ANITA%' ) 
        THEN 'SANTA ANITA'
				WHEN 
		      (PRO.DESCRIPCION LIKE '%JESSICA%PISCOYA%'
    		OR PRO.DESCRIPCION LIKE '%JOSE%SANCHE%'
    		OR PRO.DESCRIPCION LIKE '%MILTON%JUARE%'
    		OR PRO.DESCRIPCION LIKE '%PAULO%SARE%'
    		OR PRO.DESCRIPCION LIKE '%ROY%NARVAE%'
			or PRO.DESCRIPCION like '%ENRIQUE%DELFIN%'
			or PRO.DESCRIPCION LIKE '%JES%PISCOYA%'
			or PRO.DESCRIPCION LIKE '%YELIT%ORTI%DIA%'
			or PRO.DESCRIPCION LIKE '%HELLEN%VALERA%SOLI%'
			or PRO.DESCRIPCION LIKE '%ENRIQUE%DELFIN%'
			OR PRO.DESCRIPCION LIKE '%ADMIN%TRUJILLO%'
			OR PRO.DESCRIPCION LIKE '%FELIX%MARTI%GARCIA%RODRIGUEZ%' ) 
        THEN 'TRUJILLO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%CESAR%MERA%'
    		OR PRO.DESCRIPCION LIKE '%WILLIAMS%TRAUCO%'
            OR PRO.DESCRIPCION LIKE '%ALEXANDER%GARCIA%' 
			OR PRO.DESCRIPCION LIKE '%WILLIAMS%TRAUCO%' 
			OR PRO.DESCRIPCION LIKE '%DENNIS%TERRONES%'
			OR PRO.DESCRIPCION LIKE '%NADINE%SELMIRA%'
			OR PRO.DESCRIPCION LIKE '%CESAR%MERA%CASA%'
			OR PRO.DESCRIPCION LIKE '%ADMIN%TARAPOTO%'		) 
        THEN 'TARAPOTO'
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
		WHEN FI.CODIGO IN (30,31,33) THEN 'LD'
		WHEN FI.CODIGO IN (21,22,23,24,25,27,28,29) THEN 'MICROEMPRESA'
		WHEN FI.CODIGO IN (26) THEN 'EMPRENDEMUJER'
		WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑAEMPRESA'
		WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANAEMPRESA'
		WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIO'
	ELSE 'INVESTIGAR CASO'
	END AS 'PRODUCTO43',
	
    FI.DESCRIPCION AS 'FINALIDAD',

	CASE
		WHEN (p.flagrefinanciado = 1 or P.CodSolicitudCredito = 0) THEN 'REFINANCIADO'
		ELSE 'NO REFINANCIADO'
		END AS 'ETIQUETA REFINANCIADO'

FROM prestamo as p

INNER JOIN  socio              AS s    ON s.codsocio      = p.codsocio
LEFT JOIN   sociocontacto      AS sc   ON sc.codsocio     = s.codsocio
LEFT JOIN   planilla           AS pla  ON p.codplanilla   = pla.codplanilla
INNER JOIN  grupocab           AS pro  ON pro.codgrupocab = p.codgrupocab
INNER JOIN  distrito           AS d    ON d.coddistrito   = sc.coddistrito
INNER JOIN  provincia          AS pv   ON pv.codprovincia = d.codprovincia
INNER JOIN  departamento       AS dp   ON dp.coddepartamento = pv.coddepartamento
INNER JOIN  tablaMaestraDet    AS tm   ON tm.codtabladet  = p.CodEstado
LEFT JOIN   grupocab           AS gpo  ON gpo.codgrupocab = pla.codgrupocab
LEFT JOIN   tablaMaestraDet    AS tm2  ON tm2.codtabladet = s.codestadocivil
LEFT JOIN   tablaMaestraDet    AS tm3  ON tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet   AS tm3  On tm3.codtabladet = s.codcategoria
INNER JOIN  pais                       ON pais.codpais    = s.codpais
LEFT JOIN   FINALIDAD          AS FI   ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN   TipoCredito        AS TC   ON tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN  usuario            AS u    ON p.CodUsuario    = u.CodUsuario
INNER JOIN  TablaMaestraDet    AS tm4  ON s.codestado     = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota      AS pcu  ON p.CodPrestamo   = pcu.CodPrestamo

WHERE
 
    (EOMONTH(CONVERT(VARCHAR(10),p.fechadesembolso,112))    = @FECHA_MES
    OR EOMONTH(CONVERT(VARCHAR(10),p.fechadesembolso,112))  = @fechaAnterior
    OR EOMONTH(CONVERT(VARCHAR(10),p.fechadesembolso,112))  = @fecha12MESES)
    
    AND CONVERT(VARCHAR(10),p.fechadesembolso,112) < {fecha_hoy_sql}

AND s.codigosocio>0
AND p.codestado <> 563


---------------------------- crédito desembolsado en un día no laboral
--and p.fechadesembolso <> '20231105'
----------------------------

ORDER BY p.fechadesembolso desc, Socio ASC

'''

df_fincore = pd.read_sql_query(query, conn)

df_fincore['fechadesembolso'] = df_fincore['fechadesembolso'].dt.date
df_fincore['fechadesembolso'] = pd.to_datetime(df_fincore['fechadesembolso'])

###############################################################################
# AJUSTE DE FECHA DE DESEMBOLSO PARA CASOS ULTRA EXCEPCIONALES
# este crédito se desembolsó un domingo (es refinanciado)
df_fincore.loc[(df_fincore['pagare_fincore'] == '00116680'),
                'fechadesembolso'] = pd.Timestamp('2023-11-06')
###############################################################################

# normalización de fechas
df_fincore['fechadesembolso'] = df_fincore['fechadesembolso'].dt.normalize()


# df_fincore = df_fincore[df_fincore['ETIQUETA REFINANCIADO'] == 'NO REFINANCIADO']

#%% MERGE CON EL NRO DE DÍA LABORAL

union = df_fincore.merge(dias_laborales[dias_laborales['Numero de dia laboral'] != 0], # union solo con los días laborales
                         left_on  = 'fechadesembolso',
                         right_on = 'Fecha',
                         how      = 'left')
del union['Fecha']

print('Debe salir cero:')
print(union[pd.isna(union['Numero de dia laboral'])].shape[0])
if union[pd.isna(union['Numero de dia laboral'])].shape[0] > 0:
    revisar_fecha_desembolso = union[pd.isna(union['Numero de dia laboral'])]
    print('Si no sale cero, es porque se ha desembolsado en una fecha que no es laboral')
    print(revisar_fecha_desembolso['fechadesembolso'].unique())

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
               'Numero de dia laboral',
               'ETIQUETA REFINANCIADO']]

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

    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f" IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla} ")    
    cursor.execute(f" SELECT top 100 * INTO {tabla} FROM DESEMBOLSOS_DIARIOS.DBO.[2024_01] ")    
    cursor.execute(f" DELETE FROM {tabla}")
    
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
              [ETIQUETA REFINANCIADO])
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
        row['ETIQUETA REFINANCIADO']
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

# for i in range(0,(union['Numero de dia laboral'].unique().max())):
#     para_filtrar = union.copy()
#     para_filtrar = para_filtrar[para_filtrar['Numero de dia laboral'] <= i+1]
#     para_filtrar['dia acumulado'] = i+1
#     acum = pd.concat([acum,para_filtrar], ignore_index = True)

try:
    for i in range(0,(union['Numero de dia laboral'].unique().max())):
        para_filtrar = union.copy()
        para_filtrar = para_filtrar[para_filtrar['Numero de dia laboral'] <= i+1]
        para_filtrar['dia acumulado'] = i+1
        acum = pd.concat([acum,para_filtrar], ignore_index=True)

except TypeError:
    print('Posiblemente hay desembolso en fecha asignada como feriado')
    print('investigar el siguiente dataframe: "df_investigar"')
    df_investigar = union[pd.isna(union['Numero de dia laboral'])]

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

    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f" if OBJECT_ID('{tabla_acumulada}') IS NOT NULL DROP TABLE {tabla_acumulada} ")    
    cursor.execute(f" SELECT top 100 * INTO {tabla_acumulada} FROM DESEMBOLSOS_DIARIOS.DBO.[2024_01_acum] ")    
    cursor.execute(f" DELETE FROM {tabla_acumulada}")   
    
    for index, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {tabla_acumulada}
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
              [dia acumulado],
              [ETIQUETA REFINANCIADO])
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        row['dia acumulado'],
        row['ETIQUETA REFINANCIADO']
        )

    cnxn.commit()
    cursor.close()
    
    print(f'Se cargaron los datos a SQL SERVER {tabla_acumulada}')
    
else:
    print('No se ha cargado a SQL SERVER')

#%% AÑADIENDO A LAS TABLAS DE DATOS CONCATENADOS
if CARGA_SQL_SERVER == True:
    
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    df = union.copy()


    cursor.execute(f" DELETE FROM [DESEMBOLSOS_DIARIOS].[dbo].[DESEMBOLSOS] WHERE FechaCorte = '{corte_actual}'")    
    cursor.execute(f" INSERT INTO [DESEMBOLSOS_DIARIOS].[dbo].[DESEMBOLSOS] SELECT * FROM {tabla}")   



    cursor.execute(f" DELETE FROM [DESEMBOLSOS_DIARIOS].[dbo].[DESEMBOLSOS_acum] WHERE FechaCorte = '{corte_actual}'")    
    cursor.execute(f" INSERT INTO [DESEMBOLSOS_DIARIOS].[dbo].[DESEMBOLSOS_acum] SELECT * FROM {tabla_acumulada}")   

    cnxn.commit()
    cursor.close()

    print('Se insertaron los datos en las tablas principales')
else:
    print('No se ha cargado a SQL SERVER')

#%% CONECCIÓN A SQL PARA MONTO NETO
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT
	s.codigosocio,
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	p.fechadesembolso,
	p.montosolicitado as 'Otorgado',
	DESCUENTO.valor as 'retención',
	--p.montosolicitado - DESCUENTO.valor as 'MONTO NETO',
    DESCUENTO.retencion as 'tipo reten'

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

LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'
--AND s.codigosocio>0
ORDER BY RIGHT(CONCAT('0000000',p.numero),8)

'''

df_monto_neto = pd.read_sql_query(query, conn)
# df_monto_neto.drop_duplicates(subset = 'pagare_fincore', inplace = True)

df_monto_neto['retención'] = df_monto_neto['retención'].fillna(0)

lista_fincore = list(df_monto_neto['pagare_fincore'])

#%%
fincores = df_monto_neto[['codigosocio',
                          'Socio',
                          'Doc_Identidad',
                          'pagare_fincore',
                          'fechadesembolso',
                          'Otorgado',
                          ]]

fincores.drop_duplicates(subset = 'pagare_fincore', inplace = True)

# codigo que no sirve de nada pero lo reuso de otro script y lo adapto xd
estan = fincores[fincores['pagare_fincore'].isin(lista_fincore)]

#%% PARA COMPARAR:
# filtrando la retención total
df_retencion_total = df_monto_neto[df_monto_neto['tipo reten'] == 'TOTAL RETENCIÓN']
df_retencion_total = df_retencion_total.rename(columns = {'retención' : 'retención por total'})

# por agrupamiento
df_reten_agrup = df_monto_neto[df_monto_neto['tipo reten'] != 'TOTAL RETENCIÓN']
reten = df_reten_agrup.pivot_table(values  = 'retención',
                                   index   = 'pagare_fincore',
                                   aggfunc = 'sum').reset_index()
reten = reten.rename(columns = {'retención' : 'retención por agrupamiento'})

#%% MERGE
union_2 = estan.merge(df_retencion_total[['pagare_fincore', 'retención por total']],
                    on  = 'pagare_fincore',
                    how = 'left')
union_2 = union_2.merge(reten,
                    on  = 'pagare_fincore',
                    how = 'left')#%%

union_2 = union_2.fillna(0)
union_2['MONTO NETO'] = union_2['Otorgado'] - union_2['retención por total']
union_2['MONTO NETO'] = union_2['MONTO NETO'].round(2)
union_2.drop_duplicates(subset = 'pagare_fincore', inplace = True)

#%%
if CARGA_SQL_SERVER == True:
    # Esta es la tabla que estará en SQL SERVER
    tabla =  '[DESEMBOLSOS_DIARIOS].[dbo].[MONTO_NETO_2]'
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    df = union_2[['Socio', 'pagare_fincore', 'MONTO NETO']].copy()
    df = df.fillna(0)
    
    # AQUÍ SE DEBE APLICAR UN PROCESO DE LIMPIEZA DE LA TABLA PORQUE NO ACEPTA CELDAS CON VALORES NULOS
    # EJEMPLO df = df.fillna(0)
    
    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")    

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
            sql_type = 'INT'
        elif dtype == 'int32':
            sql_type = 'INT'
        elif dtype == 'float64':
            sql_type = 'FLOAT'
        elif dtype == 'object':
            sql_type = 'NVARCHAR(255)'  # Ajusta el tamaño según tus necesidades
        elif dtype == '<M8[ns]':
            sql_type = 'DATETIME'  # Ajusta el tamaño según tus necesidades

        create_table_query += f"[{column_name}] {sql_type}, "
        
    create_table_query = create_table_query.rstrip(', ') + ")"  # Elimina la última coma y espacio

    # Ejecutar la sentencia CREATE TABLE
    cursor.execute(create_table_query)
    
    # CREACIÓN DE LA QUERY DE INSERT INTO
    # Crear la lista de nombres de columnas con corchetes
    column_names = [f"[{col}]" for col in df.columns]
    # Crear la lista de placeholders para los valores
    value_placeholders = ', '.join(['?' for _ in df.columns])
    # Crear la consulta de inserción con los nombres de columna y placeholders de valores
    insert_query = f"INSERT INTO {tabla} ({', '.join(column_names)}) VALUES ({value_placeholders})"

    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')

else:
    print('No se ha cargado a SQL SERVER')

#%% ALERTA PARA CESAR
inicio_mes = pd.Timestamp(corte_actual[0:6] + '01')

alerta = union.merge(union_2[['Socio', 'pagare_fincore', 'MONTO NETO']],
                     on  = 'pagare_fincore',
                     how = 'left')

alerta = alerta[alerta['fechadesembolso'] >= inicio_mes]
alerta = alerta[alerta['MONTO NETO'] < 0]

if alerta[['MONTO NETO', 'pagare_fincore']].shape[0] > 0:
    print('MONTO NETO NEGATIVO, investigar')
else:
    print('ok')

