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
FECHATXT = '14-02-2024'  # FORMATO DÍA-MES-AÑO
###############################################################################

'directorio de trabajo' #######################################################
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2024\\febrero\\14 02'
###############################################################################

'NOMBRE DEL ARCHIVO DE BAJAS ENVIADO' #########################################
nombre_archivo = '4to INFORME 02_24 GRUPO KONECTA (B).xlsx'
###############################################################################

'filas a skipear' ######################
filas_skip = 0                        ##
########################################

#%% IMPORTANDO EL INFORME DE BAJAS

os.chdir(directorio)

bajas = pd.read_excel(nombre_archivo,
                      skiprows = filas_skip,
                      dtype    = ({'Documento': object}))

bajas['Documento'] = bajas['Documento'].astype(str)
bajas['Documento'] = bajas['Documento'].str.strip()

doc_nulos = bajas[pd.isna(bajas['Documento'])]
print('Documentos que se hayan convertido en Null:')
print(doc_nulos.shape[0])
bajas['Documento original'] = bajas['Documento']
bajas['Documento'] = bajas['Documento'].str.zfill(14)
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

inner join socio as s on s.codsocio = p.codsocio
LEFT join sociocontacto as sc on sc.codsocio = s.codsocio
left join planilla as pla on p.codplanilla = pla.codplanilla
inner join grupocab as pro on pro.codgrupocab = p.codgrupocab
inner join distrito as d on d.coddistrito = sc.coddistrito
inner join provincia as pv on pv.codprovincia = d.codprovincia
inner join departamento as dp on dp.coddepartamento = pv.coddepartamento
inner join tablaMaestraDet as tm on tm.codtabladet = p.CodEstado
left join grupocab as gpo on gpo.codgrupocab = pla.codgrupocab
left join tablaMaestraDet as tm2 on tm2.codtabladet = s.codestadocivil
left join tablaMaestraDet as tm3 on tm3.codtabladet = p.CodSituacion
--inner join tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
inner join pais on pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI ON FI.CODFINALIDAD = P.CODFINALIDAD
left join TipoCredito as TC on tc.CodTipoCredito = p.CodTipoCredito
inner join usuario as u on p.CodUsuario = u.CodUsuario
inner join TablaMaestraDet as tm4 on s.codestado = tm4.CodTablaDet
--left join PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

where CONVERT(VARCHAR(10),p.fechadesembolso,112) 
BETWEEN '20110101' AND '{fecha_hoy}' and s.codigosocio>0  and p.codestado = 341 -- and (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
--where year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 -- and pro.Descripcion like '%WILLIAMS TRAUCO%' --  and p.codcategoria=351
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
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

vigentes['fechadesembolso'] = vigentes['fechadesembolso'].apply(parse_dates)

#%% FILTRAMOS ESTADO = PENDIENTE
'por si acaso, nos quedamos solo con los que tienen estado = pendiente'

vigentes["Estado"] = vigentes["Estado"].str.strip() #quitamos espacios
vigentes["Estado"] = vigentes["Estado"].str.upper() #mayúsculas

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

bajas2 = bajas[['Documento', 'Documento original']]

#%% INNER JOIN
'inner join usando '
df_resultado = vigentes2.merge(bajas2, 
                               left_on  = ["DOC_IDENTIDAD_ceros"], 
                               right_on = ['Documento'],
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
                      "CUOTA MENSUAL",
                      'PAGARE_FINCORE', 
                      "EMPRESA/PLANILLA"]]

final = final.rename(columns = {'Documento original' : 'Documento'})

# POR SI ACASO, ELIMINAMOS DUPLICADOS
final.drop_duplicates(subset = 'PAGARE_FINCORE', inplace = True)

#%% CREACIÓN DE EXCEL

NOMBRE = 'BAJAS '+ FECHATXT + '.xlsx'

try:
    os.remove(NOMBRE)
except FileNotFoundError:
    pass

final.to_excel(NOMBRE, 
               index = False,
               sheet_name = FECHATXT)


