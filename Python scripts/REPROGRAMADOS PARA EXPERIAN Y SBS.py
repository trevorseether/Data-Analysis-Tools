# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 09:07:46 2023

@author: Joseph Montoya
"""
###############################################################################
#### REPROGRAMADOS PARA LA SBS 
###############################################################################

#%% PRIMER REPORTE PARA EXPERIAN
#%% importación de módulos
import pandas as pd
import os

#%% INSUMOS
# Anexo 06 de reprogramados ###################################################
anx06_repro = 'Rpt_DeudoresSBS Créditos Reprogramados ENERO 2024 no incluye castigados.xlsx'
###############################################################################

# Directorio de trabajo #######################################################
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\2024 enero\\productos'
###############################################################################

# mes y año ###################################################################
mes = 'enero'
año = 2024
###############################################################################
#%% IMPORTACIÓN DE ARCHIVOS

os.chdir(directorio)
tabla1 = pd.read_excel(anx06_repro,
                       skiprows = 2,
                       dtype = {'Número de Documento 10/' : str,
                                'Código Socio 7/'         : str})

#eliminación de filas vacías si es que las hay
tabla1.dropna(subset = ['Apellidos y Nombres / Razón Social 2/',
                        'Fecha de Nacimiento 3/',
                        'Número de Documento 10/',
                        'Domicilio 12/',
                        'Numero de Crédito 18/'], inplace = True, how = 'all')

df = pd.DataFrame()  #CREANDO INSTANCIA DATA FRAME

df['CODIGO SOCIO']      = tabla1['Código Socio 7/']
df['TIPO DOCUMENTO']    = tabla1['Tipo de Documento 9/']
df['NUMERO DOCUMENTO']  = tabla1["Número de Documento 10/"]
df['TIPO DE CREDITO']   = tabla1["Tipo de Crédito 19/"]
df['DEUDA DIRECTA']     = tabla1["Saldo de colocaciones (créditos directos) 24/"]
df['TIPO DE REPROGRAMACION']  = tabla1["TIPO_REPRO"]
df['DEUDA REPROGRAMADA']      = tabla1["Saldo de colocaciones (créditos directos) 24/"]

df['TIPO DE CREDITO'] = df['TIPO DE CREDITO'].astype(int)
df['TIPO DE CREDITO'] = df['TIPO DE CREDITO'].map({9  : '09', #REEMPLAZANDO LOS VALORES POR STRINGS CON CEROS
                                                   8  : '08',
                                                   10 : '10',
                                                   11 : '11',
                                                   12 : '12',
                                                   13 : '13'},
                                                 na_action = None) #EN CASO DE NULO NO HACER NADA

df['CODIGO SOCIO']      = df['CODIGO SOCIO'].str.strip()
df['NUMERO DOCUMENTO']  = df['NUMERO DOCUMENTO'].str.strip()

#%% NOMBRE
X = mes
Y = año
resultado = (str(X.lower().capitalize()) + " " + "Reprogramados - " +str(Y)) #métodos string para crear el nombre del archivo
nombre = str(resultado)+".xlsx"

#%% EXCEL

try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

df.to_excel(nombre, 
            index = False,
            startrow = 1,
            startcol = 1,
            sheet_name=str(X.lower().capitalize() + "-"+str(Y)))


#%% REPROGRAMADOS PARA LA SBS
#una vez que Experian nos devuelva la calificación de los socios
'''
## ###    #####   #####    #####     # ####           ######
#######  #######  #######  ######   #######           #######
     ##  ##   ##       ##      ##   ##                    ###
######   ##   ##  ######       ##   #######             ####
 #       #######  ##   ##      ##    #                ####
##       ##   ##  ##   ##      ##   #######           #######
##       ##   ##  ##   ##      ##    ######           #######
'''

#%% importación de módulos
import pandas as pd
import os

#%% INSUMOS

# Directorio de trabajo #######################################################
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\REPROGRAMADOS para SBS\\2023 diciembre'
###############################################################################

# Anexo 06 de reprogramados ###################################################
anx06_repro = 'Rpt_DeudoresSBS Créditos Reprogramados DICIEMBRE 2023 no incluye castigados.xlsx'
###############################################################################

# CALIFICACIÓN ENVIADA POR EXPERIAN ###########################################
calificacion = '20523941047_70369063_PE202400019_COOPAC_SAN_MIGUEL_SEGMENTACION_RIESGO_SALIDA.xlsx'
###############################################################################

#%%
# mes y año ###################################################################
mes = 'diciembre'
año = 2023
###############################################################################

#%% PROCESAMIENTO
os.chdir(directorio)

#lectura del anexo06 de reprogramados
tabla1 = pd.read_excel(anx06_repro,
                       #sheet_name = "Hoja1",
                       skiprows = 2,
                       dtype = {'Número de Documento 10/' : str,
                                'Código Socio 7/'         : str,
                                'Nro Prestamo \nFincore'  : str
                               },
                       parse_dates=["FEC_ULT_REPROG"])

#eliminación de filas vacías si es que las hay
tabla1.dropna(subset=['Apellidos y Nombres / Razón Social 2/',
                      'Fecha de Nacimiento 3/',
                      'Número de Documento 10/',
                      'Domicilio 12/',
                      'Numero de Crédito 18/'], inplace = True, 
                                                how = 'all')


#lectura del segundo archivo
tabla2 = pd.read_excel(calificacion,
                        sheet_name = "A. SALIDA BATCH",
                        skiprows   = 6,
                        dtype      = {'NUMERO DOCUMENTO': str}
                       )

df = pd.DataFrame()  #CREANDO INSTANCIA DATA FRAME
df['1/CCL/Código Interno del socio']          = tabla1["Código Socio 7/"] #ESTÁ SACANDO INFOR DE UN DATAFRAME PARA INSERTARLO EN OTRO
df['2/CSOCIO/Código Interno del socio']       = tabla1["Código Socio 7/"]
df['3/TID/Tipo de documento']                 = tabla1["Tipo de Documento 9/"]
df['4/NID/Número de Documento']               = tabla1["Número de Documento 10/"]
df['4/NID/Número de Documento']               = df['4/NID/Número de Documento'].str.strip()

df['5/NCL/Nombre del deudor']                 = tabla1["Apellidos y Nombres / Razón Social 2/"]
df['06/CCR/Número de código de la operación'] = tabla1['Nro Prestamo \nFincore']
df['7/SKCR/Saldo capital de la deuda']        = tabla1["Saldo de colocaciones (créditos directos) 24/"]
df['8/TCR/Tipo de crédito según reporte crediticio de deudores'] = tabla1["Tipo de Crédito 19/"]
df['9/MDREPRP/ Modalidad de reprogramación']  = tabla1['9/MDREPRP/ Modalidad de reprogramación'] # = tabla1["TIPO_REPRO"]
########################
df['10/SEGRIESGO/ Segmentación de Riesgos']   = 'modificar' #tabla2["RIESGO_FINAL"] #INFO QUE VIENE DE LA TABLA DE EQUIFAX
########################
df['11/SIN/Ingresos devengados']              = tabla1['Rendimiento\nDevengado 40/']
df['12/FREP/ Fecha en que se realizó la reprogramación'] = tabla1["FEC_ULT_REPROG"]
df['13/CLADEU/ Clasificación del deudor']     = tabla1["Clasificación del Deudor con Alineamiento 15/"]
df['14/REP_EME']                              = tabla1["Saldo de colocaciones (créditos directos) 24/"]

df['8/TCR/Tipo de crédito según reporte crediticio de deudores'] = df['8/TCR/Tipo de crédito según reporte crediticio de deudores'].map({9:'09', #REEMPLAZANDO LOS VALORES POR STRINGS CON CEROS
                                                   8  : '08',
                                                   10 : '10',
                                                   11 : '11',
                                                   12 : '12',
                                                   13 : '13'},
                                                  na_action = None) #EN CASO DE NULO NO HACER NADA

'''
df['9/MDREPRP/ Modalidad de reprogramación'] = df['9/MDREPRP/ Modalidad de reprogramación'].map(
                                                  {"TIPO 1": '1', #REEMPLAZANDO LOS VALORES POR STRINGS CON CEROS
                                                   "TIPO 2": '2',
                                                   "TIPO 3": '1'},
                                                  na_action=None) #EN CASO DE NULO NO HACER NADA
'''

df = df.merge(tabla2[['NUMERO DOCUMENTO','NIVEL DE RIESGO']],
                         left_on  = ["4/NID/Número de Documento"],
                         right_on = ['NUMERO DOCUMENTO'],
                         how      = 'left')
df.drop(['NUMERO DOCUMENTO'], 
        axis = 1, 
        inplace = True)

df['10/SEGRIESGO/ Segmentación de Riesgos'] = df['NIVEL DE RIESGO']

df.drop(['NIVEL DE RIESGO'], 
        axis = 1, 
        inplace = True)


df['10/SEGRIESGO/ Segmentación de Riesgos'] = df['10/SEGRIESGO/ Segmentación de Riesgos'].map({"BAJO"  : '1',
                                                                                               "MEDIO" : '2',
                                                                                               "ALTO"  : '3',
                                                                                               'SIN INFORMACION': '2'}, 
                                                                                              na_action = None)

formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM',
            '%Y/%m/%d %H:%M:%S PM',
            '%Y/%m/%d %H:%M:%S AM']

# Función de análisis de fechas
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
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

df['12/FREP/ Fecha en que se realizó la reprogramación'] = df['12/FREP/ Fecha en que se realizó la reprogramación'].apply(parse_dates)

mesesito = str(mes)
añito = str(año)
X = "COOPAC SAN MIGUEL REPROGRAMADOS - " + mesesito.upper() + " " + añito

nombre = str(X) + ".xlsx"

#%% EXCEL
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

df.to_excel(nombre,
            index = False,
            startrow = 0,
            startcol = 0,
            sheet_name=str(mesesito.upper() + " " + str(añito)))

