# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 10:46:51 2023

@author: Joseph Montoya Muñoz
"""
'''
###############################################################################
##          CRUCE DE BAJAS DE KONECTA
###############################################################################
'''
#%% IMPORTACIÓN DE MÓDULOS

import pandas as pd
import os
import pyodbc
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

from colorama import Back # , Style, init, Fore

#%% DIRECTORIO DE TRABAJO, fecha actual

'AQUI SE PONE LA FECHA DE HOY' ################################################
FECHATXT = '2025-03-12'  # FORMATO AÑO-MES-DÍA
###############################################################################

'directorio de trabajo' #######################################################
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2025\\marzo\\12 03'
###############################################################################

'NOMBRE DEL ARCHIVO DE BAJAS ENVIADO' #########################################
nombre_archivo = '2DO INFORME 03_25 GRUPO KONECT.xlsx'
###############################################################################

'filas a skipear' ######################
filas_skip = 12                       ##
########################################

'COLUMNA DEL DOCUMENTO IDENTIDAD' #############
COL_DOC_IDENTIDAD = 'Documento' #'DNI' # 'Documento'
###############################################

'COLUMNA DE LA FECHA DE BAJA' #################
COL_FECHA_BAJA = 'BAJA SAP' #'BAJA SAP'  #'Fecha egreso'
###############################################

'HOJA DE EXCEL' ###############################
nombre_sheet = 'Final'
###############################################

'Creación de excels'###########################
crear_excel = True # True o False
###############################################

#%% IMPORTANDO EL INFORME DE BAJAS

os.chdir(directorio)

bajas = pd.read_excel(nombre_archivo,
                      skiprows = filas_skip,
                      dtype    = ({COL_DOC_IDENTIDAD: object}),
                      sheet_name = nombre_sheet)

bajas[COL_DOC_IDENTIDAD] = bajas[COL_DOC_IDENTIDAD].astype(str)
bajas[COL_DOC_IDENTIDAD] = bajas[COL_DOC_IDENTIDAD].str.strip()
formato_para_lista_negra = bajas.copy() 

doc_nulos = bajas[pd.isna(bajas[COL_DOC_IDENTIDAD])]
print('Documentos que se hayan convertido en Null:')
print(doc_nulos.shape[0])

bajas['Documento original'] = bajas[COL_DOC_IDENTIDAD]
bajas[COL_DOC_IDENTIDAD] = bajas[COL_DOC_IDENTIDAD].str.zfill(14)
print('Documentos que se hayan convertido en Null:')

if doc_nulos.shape[0] > 0:
    print(doc_nulos)
    print(Back.RED + 'investigar qué ha pasado')
else:
    print(doc_nulos.shape[0])
    del doc_nulos
    print(Back.GREEN + 'todo bien')

#%% LECTURA DE LAS CREDENCIALES
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%% CREACIÓN DE LA CONECCIÓN A SQL

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#%% QUERY, créditos vigentes

def convertir_fecha(fecha_str):
    try:
        # Parsea la fecha de entrada en formato 'dd-mm-yyyy'
        fecha = datetime.strptime(fecha_str, '%d-%m-%Y')
        # Formatea la fecha en el formato 'yyyymmdd'
        fecha_formateada = fecha.strftime('%Y%m%d')
        return fecha_formateada
    except ValueError:
        return "Formato de fecha incorrecto. Debe ser 'dd-mm-yyyy'."

fecha_formateada = convertir_fecha(FECHATXT)

###############################################################################
fecha_hoy = fecha_formateada ######### AQUÍ VA LA FECHA DE HOY
###############################################################################

# ACTUALMENTE LA QUERY TRAE TODOS LOS CRÉDITOS VIGENTES, SIN IMPORTAR LA FECHA
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
	sc.celular1, 
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

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112)  >= '20110101' 
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

#%% PARSEO DE FECHAS

formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', 
            '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM']  # Lista de formatos a analizar
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format = formato)
        except ValueError:
            pass
    return pd.NaT

vigentes['fechadesembolso'] = vigentes['fechadesembolso'].apply( parse_dates )

#%% FILTRAMOS ESTADO = PENDIENTE
'por si acaso, nos quedamos solo con los que tienen estado = pendiente'

vigentes["Estado"] = vigentes["Estado"].str.strip() # quitamos espacios
vigentes["Estado"] = vigentes["Estado"].str.upper() # mayúsculas

vigentes = vigentes[vigentes["Estado"] == 'PENDIENTE']

#%% 14 ceros para merge
'agregamos 14 ceros al reporte EXTRAIDO CON SQL'
vigentes["Doc_Identidad"]       = vigentes["Doc_Identidad"].astype(str)
vigentes["DOC_IDENTIDAD_ceros"] = vigentes["Doc_Identidad"].str.zfill(14)

#%%SELECCIÓN DE COLUMNAS
'nos quedamos solo con las columnas necesarias'

vigentes2 = vigentes[["DOC_IDENTIDAD_ceros", 
                      "Socio", 
                      "fechadesembolso", 
                      "pagare_fincore", 
                      "CuotaFija", 
                      "Planilla"]]

vigentes2 = vigentes2.rename(columns = {"Doc_Identidad"   : "DOC_IDENTIDAD",
                                        "Socio"           : "SOCIO",
                                        "fechadesembolso" : "FECHA_DESEMBOLSO",
                                        "pagare_fincore"  : "PAGARE_FINCORE",
                                        "CuotaFija"       : "CUOTA MENSUAL",
                                        "Planilla"        : "EMPRESA/PLANILLA"})

bajas2 = bajas[[COL_DOC_IDENTIDAD, 'Documento original']]

#%% INNER JOIN
'inner join usando '
df_resultado = vigentes2.merge(bajas2, 
                               left_on  = ["DOC_IDENTIDAD_ceros"], 
                               right_on = [COL_DOC_IDENTIDAD],
                               how      = 'inner')

#%% DATAFRAME FINAL
'''creamos el archivo final'''
#df_resultado['SALDO A DESCONTAR'] = np.nan
#df_resultado['# CUOTAS'] = np.nan

final = df_resultado[['Documento original',
                      'SOCIO', 
                      'FECHA_DESEMBOLSO', 
                      #'SALDO A DESCONTAR', 
                      #'# CUOTAS',
                      'CUOTA MENSUAL',
                      'PAGARE_FINCORE', 
                      'EMPRESA/PLANILLA']]

final = final.rename(columns = {'Documento original' : COL_DOC_IDENTIDAD})

# POR SI ACASO, ELIMINAMOS DUPLICADOS
final.drop_duplicates(subset = 'PAGARE_FINCORE', inplace = True)

#%% 
# =============================================================================
#  PARTE 2 VERIFICACIÓN SI EL SOCIO TIENE UN CRÉDITO SOLICITADO
# =============================================================================
conn = pyodbc.connect(conn_str)

query = '''

SELECT
    
    iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad', 
    iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
    S.CodigoSocio,
    B.MontoSolicitado,
    B.CuotaFija,
    B.FechaSolicitud
    --,*

FROM SOCIO AS S

LEFT JOIN SolicitudCredito as b 
ON S.CodSocio = b.CodSocio

WHERE b.CodEstado in (48,280,330,331,336)

-- 48  TRANSITO

-- 280 APROBADO

-- 330 EVALUACION

-- 331 DEVUELTO ANALISTA

-- 336 DEVUELTO SUPERVISOR

'''

pendientes = pd.read_sql_query(query, 
                               conn, 
                               dtype = {'Doc_Identidad' : object,
                                        'CodigoSocio'   : object
                                        })

#%% 14 ceros para merge
'agregamos 14 ceros al reporte EXTRAIDO CON SQL'
pendientes["Doc_Identidad"]       = pendientes["Doc_Identidad"].astype(str)
pendientes["DOC_IDENTIDAD_ceros"] = pendientes["Doc_Identidad"].str.zfill(14)

# Cruzamos con bajas2
nos_quieren_estafar = pendientes[pendientes["DOC_IDENTIDAD_ceros"].isin(list(bajas2[COL_DOC_IDENTIDAD]))]
del nos_quieren_estafar["DOC_IDENTIDAD_ceros"]
del nos_quieren_estafar['CodigoSocio']

nos_quieren_estafar['Estado'] = 'Crédito Solicitado'

#%% CREACIÓN DE EXCEL
if crear_excel == True:
    NOMBRE = 'BAJAS ' + FECHATXT + '.xlsx'
    
    # Eliminar el archivo si ya existe
    try:
        os.remove(NOMBRE)
    except FileNotFoundError:
        pass
    
    # Crear un objeto ExcelWriter para manejar la escritura de DataFrames en el archivo
    with pd.ExcelWriter(NOMBRE, engine='xlsxwriter') as writer:
        # Escribir el primer DataFrame en el archivo
        final.to_excel(writer,
                       index = False,
                       sheet_name = FECHATXT)
    
        # Verificar si hay datos que podrían indicar intento de estafa y escribirlos debajo del primer DataFrame
        # si hay estos casos, incluir en el correo a Manuel Montoya y a Cesar Diaz
        if nos_quieren_estafar.shape[0] > 0:
            nos_quieren_estafar.to_excel(writer,
                                         sheet_name = FECHATXT,
                                         startrow = final.shape[0] + 2,  # Offset para no sobrescribir el primer DataFrame
                                         startcol = 0,
                                         index = False)  # Aquí puedes elegir si quieres o no los índices

    # No es necesario llamar a writer.save() o writer.close() ya que el bloque 'with' maneja eso automáticamente
else:
    pass

#%% FORMATO PARA LISTA NEGRA DEL FINCORE
df = formato_para_lista_negra.copy()

def tipo_doc(df):
    if len(df[COL_DOC_IDENTIDAD]) == 8:
        return 'DNI'
    if len(df[COL_DOC_IDENTIDAD]) == 9:
        return 'CARNET EXT.'
    else:
        return 'otros'

df['tipo doc'] = df.apply(tipo_doc, axis = 1)

if df[df['tipo doc'] == 'otros'].shape[0] > 0:
    print('documento de identidad investigar')
    
#%%
def parse_dates(date_str):
    '''
    Parameters
    ----------
    date_str : Es el formato que va a analizar dentro de la columna del DataFrame.

    Returns
    -------
    Si el date_str tiene una estructura compatible con los formatos preestablecidos
    para su iteración, la convertirá en un DateTime

    '''
    #formatos en los cuales se tratará de convertir a DateTime
    formatos = ['%d/%m/%Y %H:%M:%S',   
                '%d/%m/%Y',            
                '%Y%m%d', '%Y-%m-%d',  
                '%Y-%m-%d %H:%M:%S',   
                '%Y/%m/%d %H:%M:%S',   
                '%Y-%m-%d %H:%M:%S PM',
                '%Y-%m-%d %H:%M:%S AM',
                '%Y/%m/%d %H:%M:%S PM',
                '%Y/%m/%d %H:%M:%S AM']

    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format = formato)
        except ValueError:
            pass
    return pd.NaT

df['fechas'] = df[COL_FECHA_BAJA].apply(parse_dates)
if df[pd.isna(df['fechas'])].shape[0] > 0:
    print('investigar fechas sin formato')
    
#%%
if 'Sociedad' not in df.columns:
    # Si no existe, crearla con valores vacíos
    df['Sociedad'] = ''

df['Sociedad'].fillna('', inplace = True)
df['fecha'] = df['fechas'].dt.strftime('%Y-%m-%d')

fecha_datetime = datetime.strptime(FECHATXT, '%Y-%m-%d')
fecha_nuevo_formato = fecha_datetime.strftime('%Y-%m-%d')
def observacion(df):
    
    if df['Sociedad'] != '':
        observacion_txt = f'POR CESE DE PLANILLA SEGÚN BASE KONECTA, REMITIDA EL {fecha_nuevo_formato}. TRABAJADOR PERTENECIA A ' \
        + str(df['Sociedad']) +\
        ' CON FECHA DE BAJA ' + str(df['fecha'])
        return observacion_txt
    
    elif df['Sociedad'] == '':
        observacion_txt2 = f'POR CESE DE PLANILLA SEGÚN BASE KONECTA, REMITIDA EL {fecha_nuevo_formato}.' +\
        ' CON FECHA DE BAJA ' + str(df['fecha'])
        return observacion_txt2
    
df['observacion'] = df.apply(observacion, axis = 1)

#%% DataFrame para Fincore
df_para_carga = pd.DataFrame()

df_para_carga['TipoLista']    = None
df_para_carga['TipoDocto']    = df['tipo doc'].copy()
df_para_carga['NroDocumento'] = df[COL_DOC_IDENTIDAD].copy()
df_para_carga['Nombres']      = None
df_para_carga['ApePaterno']   = df['Empleado'].copy()
df_para_carga['ApeMaterno']   = None
df_para_carga['Cargo']        = None
df_para_carga['Entidad']      = None
df_para_carga['FechaInicio']  = df['fecha'].copy()
df_para_carga['FechaFin']     = None
df_para_carga['TipoNoticia']  = None
df_para_carga['Observacion']  = df['observacion'].copy()

df_para_carga['FechaInicio']  = df_para_carga['FechaInicio'].apply(parse_dates)

#%% EXCEL
if crear_excel == True:
    df_para_carga.to_excel(f'Bajas Konecta, para lista negra {fecha_nuevo_formato}.xlsx',
                           index = False)
else:
    pass
