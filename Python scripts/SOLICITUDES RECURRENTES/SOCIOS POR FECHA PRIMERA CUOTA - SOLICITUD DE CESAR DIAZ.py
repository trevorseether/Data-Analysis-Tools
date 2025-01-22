# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 10:32:05 2024

@author: sanmiguel38
"""

import pyodbc
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONTEO DE SOCIOS, REPORTE DE CESAR DÍAZ
# =============================================================================
#%%
fecha_final      = '20241231' # único parámetro para cambiar cada mes
CARGA_SQL_SERVER = True

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = f'''
SELECT
	s.codigosocio,
    eomonth(P.FechaPrimeraCuota) as 'MES PRIMERA CUOTA',
CASE
		WHEN ROW_NUMBER() OVER (PARTITION BY s.codigosocio, eomonth(P.FechaPrimeraCuota) ORDER BY s.codigosocio) = 1 THEN 1
		ELSE 0
		END AS 'CONTEO SOCIOS',

	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	p.montosolicitado as 'Otorgado', 
	P.FechaPrimeraCuota,
	--DESCUENTO.valor as 'retención',
	--p.montosolicitado - DESCUENTO.valor as 'MONTO NETO'
	FI.CODIGO AS 'COD_FINALIDAD',
	CASE
		WHEN FI.CODIGO IN (34,35,36,37,38,39)          THEN 'DXP'
		WHEN FI.CODIGO IN (30,31,32,33)                THEN 'LIBRE DISPONIBILIDAD'
		WHEN FI.CODIGO IN (15,16,17,18,19)             THEN 'PEQUEÑA EMPRESA'
		WHEN FI.CODIGO IN (21,22,23,24,25,26,27,28,29) THEN 'MICRO EMPRESA'
		WHEN FI.CODIGO IN (95,96,97,98,99)             THEN 'MEDIANA EMPRESA'
		WHEN FI.CODIGO IN (41,45)                      THEN 'HIPOTECARIO'
		ELSE 'INVESTIGAR'
		END AS 'TIPO DE PRODUCTO TXT'

-- pcu.FechaVencimiento as Fecha1raCuota, pcu.NumeroCuota, pcu.SaldoInicial,
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

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'

AND P.FechaPrimeraCuota BETWEEN '20230101' AND '{fecha_final}'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio>0
AND p.montosolicitado > 0

--and p.codestado = 342
--AND FI.CODIGO IN (15,16,17,18,19)

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY socio ASC, p.fechadesembolso DESC
'''

df_creds = pd.read_sql_query(query, conn)

df_creds['IDENTIFICADOR UNICO'] = df_creds['MES PRIMERA CUOTA'] + '-' + df_creds['codigosocio']

#%% socios
df_socios_total = df_creds[['IDENTIFICADOR UNICO','FechaPrimeraCuota']]
df_socios_total.drop_duplicates(subset  = 'IDENTIFICADOR UNICO',
                                inplace = True)

###############################################################################
df_socios_dxp = df_creds[df_creds['TIPO DE PRODUCTO TXT'] == 'DXP']
df_socios_dxp = df_socios_dxp[['IDENTIFICADOR UNICO','FechaPrimeraCuota']]
df_socios_dxp.drop_duplicates(subset  = 'IDENTIFICADOR UNICO',
                              inplace = True)

###############################################################################
df_socios_ld = df_creds[df_creds['TIPO DE PRODUCTO TXT'] == 'LIBRE DISPONIBILIDAD']
df_socios_ld = df_socios_ld[['IDENTIFICADOR UNICO','FechaPrimeraCuota']]
df_socios_ld.drop_duplicates(subset  = 'IDENTIFICADOR UNICO',
                             inplace = True)

###############################################################################
df_socios_peq = df_creds[df_creds['TIPO DE PRODUCTO TXT'] == 'PEQUEÑA EMPRESA']
df_socios_peq = df_socios_peq[['IDENTIFICADOR UNICO','FechaPrimeraCuota']]
df_socios_peq.drop_duplicates(subset  = 'IDENTIFICADOR UNICO',
                             inplace = True)

###############################################################################
df_socios_mic = df_creds[df_creds['TIPO DE PRODUCTO TXT'] == 'MICRO EMPRESA']
df_socios_mic = df_socios_mic[['IDENTIFICADOR UNICO','FechaPrimeraCuota']]
df_socios_mic.drop_duplicates(subset  = 'IDENTIFICADOR UNICO',
                             inplace = True)

#%%

# Define una lista con los dataframes y sus nombres de tabla correspondientes
tablas_y_dataframes = [
    ("EXCEPCIONES..TOTAL", df_socios_total),
    ("EXCEPCIONES..DXP"  , df_socios_dxp),
    ("EXCEPCIONES..LD"   , df_socios_ld),
    ("EXCEPCIONES..PEQ"  , df_socios_peq),
    ("EXCEPCIONES..MIC"  , df_socios_mic)
]

if CARGA_SQL_SERVER:
    # Establece la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    for tabla, df in tablas_y_dataframes:
        df = df.copy()
        
        # Limpieza de datos para evitar valores nulos
        df = df.fillna(0)  # O ajusta según sea necesario

        # Elimina la tabla si existe
        cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")    

        # Generar la sentencia CREATE TABLE dinámicamente
        create_table_query = f"CREATE TABLE {tabla} ("
        for column_name, dtype in df.dtypes.items():
            sql_type = ''
            if dtype == 'int64':
                sql_type = 'INT'
            elif dtype == 'float64':
                sql_type = 'FLOAT'
            elif dtype == 'object':
                sql_type = 'NVARCHAR(255)'  # Ajusta el tamaño según tus necesidades
            elif dtype == '<M8[ns]':
                sql_type = 'DATETIME'
            create_table_query += f"[{column_name}] {sql_type}, "
        create_table_query = create_table_query.rstrip(', ') + ")"  # Elimina la última coma y espacio
        
        # Ejecutar la creación de la tabla
        cursor.execute(create_table_query)

        # Crear la consulta de inserción
        column_names = [f"[{col}]" for col in df.columns]
        value_placeholders = ', '.join(['?' for _ in df.columns])
        insert_query = f"INSERT INTO {tabla} ({', '.join(column_names)}) VALUES ({value_placeholders})"

        # Insertar datos fila por fila
        for _, row in df.iterrows():
            cursor.execute(insert_query, tuple(row))
        
        print(f"Tabla {tabla} cargada correctamente.")
    
    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()
    print('Todos los dataframes se cargaron exitosamente en SQL Server.')
else:
    print('No se ha cargado a SQL SERVER.')

