# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 15:00:55 2023

@author: Joseph Montoya
"""
# ============================================================================= #
#                                                                               #
#              PROCESAMIENTO DEL REPORTE DIARIO DE KASHIO                       #
#                                                                               #
# ============================================================================= #

#%% MÓDULOS
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

import calendar
import datetime
from colorama import Back # , Style, init, Fore

#%% UBICACIÓN DE LOS ARCHIVOS #################################################
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2024 10\\24 10')
###############################################################################

#%% NOMBRE ARCHIVO PRINCIPAL
'NOMBRE DEL ARCHIVO DE HOY' ###################################################
ARCHIVO_HOY = 'DATA_CLIENTES_COOP.SANMIGUEL_20241024.xlsx'
###############################################################################

#%% CREAR ARCHIVO DE VERIFICACIÓN DE CORREOS ##################################
crear_archivo         = False #True o False
###############################################################################

'REPORTE DE MENSAJERÍA PREVENTIVA' ############################################
mensajeria_preventiva = False #True o False
###############################################################################

'filtrar solo mype' ###########################################################
solo_pyme             = False #True o False
###############################################################################

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%% lectura del archivo
kashio = pd.read_excel(ARCHIVO_HOY,
                       dtype = { 'ID CLIENTE'       : str,
                                 'TELEFONO'         : str,
                                 'NUMERO DOCUMENTO' : str }
                       )

kashio['ID CLIENTE'] = kashio['ID CLIENTE'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.upper()

columnas = list(kashio.columns)

#%%  lectura y merge con el del día anterior (obsoleto)
'''
#LEYENDO EL DEL DÍA ANTERIOR
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\21 agosto 2023'
nombre = 'DATA_CLIENTES_COOP.SANMIGUEL_20230821.xlsx'

kashio_anterior = pd.read_excel(ubi + '\\' + nombre,
                                dtype={'ID CLIENTE': str,
                                       'TELEFONO': str,
                                       'NUMERO DOCUMENTO': str})

kashio_anterior['ID CLIENTE'] = kashio_anterior['ID CLIENTE'].str.strip()
kashio_anterior['EMAIL'] = kashio_anterior['EMAIL'].str.strip()
kashio_anterior['EMAIL'] = kashio_anterior['EMAIL'].str.upper()

kashio_anterior['EMAIL ANTERIOR'] = kashio_anterior['EMAIL']
kashio_anterior['ID ANTERIOR'] = kashio_anterior['ID CLIENTE']
kashio_anterior = kashio_anterior[['ID ANTERIOR', 'EMAIL ANTERIOR']]

#%% unimos con el del día anterior
kashio = kashio.merge(kashio_anterior, 
                      left_on=['ID CLIENTE'],
                      right_on=['ID ANTERIOR'],
                      how='left')

def limpieza(kashio): #si no hay 'email del día anterior' se coloca el del día actual
    if pd.isna(kashio['EMAIL ANTERIOR']):
        return kashio['EMAIL']
    else:
        return kashio['EMAIL ANTERIOR']
    
kashio['EMAIL ANTERIOR'] = kashio.apply(limpieza, axis=1)

kashio['EMAIL ANTERIOR'] = kashio['EMAIL ANTERIOR'].str.strip()
'''
#%% LIMPIEZA DE DATOS:
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.PE'  , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.COM' , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCON'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAI.COM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GGMIAL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GNMAIL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMA.IL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL..COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL'         , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HMAIL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMIL.COM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMEIL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@OUTOOK.ES'     , '@OUTLOOK.ES')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.C'     , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAILCOM'    , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAI.COM'    , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.CO'  , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.COMOM' , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.COMOM.PE' , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMJM'   , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMOM'   , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAOL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAIL.COM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMC.OM' , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPM'   , '@GMAIL.COM')

kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAL.COM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIIL.COM'  , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAL.COM'    , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPM'   , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMIAL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCOM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAI.COM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAL.COM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CCOM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL .COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILO.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCOM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COPM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMAIL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMCALLE CESAR VALEJO 420 INT' , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CM'      , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILC.OM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMIAL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GNAIL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMAIL.COM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COJM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAOL.COM'     , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.'    , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.CM'  , '@GMAIL.COM')

kashio['EMAIL'] = kashio['EMAIL'].str.replace('@OUTLOOCK.COM' , '@OUTLOOK.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIOL.COM' , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@OUTLOC.COM'   , '@OUTLOOK.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMCM'  , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPE'  , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM*9'  , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPE'  , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM614' , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HTOMAIL.COM'  , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HPTMAIL.COM'  , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GHOTMAIL.COM' , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.COMO' , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HTMAIL.COM'   , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTAMIL.COM'  , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMIAL.COM'  , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HTMAIL.COM'   , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOSMAIL.COM'  , '@HOTMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@.COM'         , '@GMAIL.COM')
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COML'   , '@GMAIL.COM')


# usando regular expresions
kashio['EMAIL'] = kashio['EMAIL'].str.replace(r'@GMAIL$', '@GMAIL.COM', 
                                              regex = True)
kashio['EMAIL'] = kashio['EMAIL'].str.replace(r'@HOTMAIL$', '@HOTMAIL.COM', 
                                              regex = True)


kashio.loc[kashio['EMAIL'] == 'CARLOSCASTILLOFUENTES12@'  , 'EMAIL'] = 'CARLOSCASTILLOFUENTES12@GMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'DENIS_POBLETE@GHOTMAIL.COM', 'EMAIL'] = 'DENIS_POBLETE@HOTMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'RAQUELALINA@GNAIL.COM'     , 'EMAIL'] = 'RAQUELALINA@GMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'RRENGIFOCORAL@HOTMAIL..COM', 'EMAIL'] = 'RRENGIFOCORAL@HOTMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'TATO.12.TLV@GMAOL.COM'     , 'EMAIL'] = 'TATO.12.TLV@GMAIL.COM'
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM\n.COM', '@GMAIL.COM')    

kashio.loc[kashio['EMAIL'] == 'BRAULIO.18@@HOTMAIL.COM'          , 'EMAIL'] = 'BRAULIO.18@HOTMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'GISELAISABELLEONATOCHE@GMAIL.'    , 'EMAIL'] = 'GISELAISABELLEONATOCHE@GMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'RAQUELALINA@GNAIL.COMALDAIRPOLOPASTOR@GMAIL.COM9614' , 'EMAIL'] = 'ALDAIRPOLOPASTOR@GMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'HERRERA2019ROMULO@OUTLOOK.COM-'   , 'EMAIL'] = 'HERRERA2019ROMULO@OUTLOOK.COM'
kashio.loc[kashio['EMAIL'] == 'CESARSOLISBARRETO@GM,AIL.COM'     , 'EMAIL'] = 'CESARSOLISBARRETO@GMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'LISSET_SS@HOTM,AIL.COM', 'EMAIL'] = 'LISSET_SS@HOTMAIL.COM'
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@KONECTA_GROUP.COM'    , '@KONECTA-GROUP.COM')    

kashio.loc[kashio['EMAIL'] == 'MARJORIE.LIBRAVITVIL1994@GMAIL', 'EMAIL'] = 'MARJORIE.LIBRAVITVIL1994@GMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'CIBER_APOL@HOTMAIL'            , 'EMAIL'] = 'CIBER_APOL@HOTMAIL.COM'
kashio.loc[kashio['EMAIL'] == 'JSU8095@GMAIL.COM*9'           , 'EMAIL'] = 'JSU8095@GMAIL.COM'

###############################################################################
kashio['EMAIL ANTERIOR'] = kashio['EMAIL'] #si reactivamos la celda anterior, esto habría que eliminarlo o comentarlo

def correccion(row):
    palabras_a_buscar = [ 'GMAILCON', '\\', '/', 'FMAIL.COM', 
                          'GAMIL.COM', 'GEMAIL.COM', 'GMAIL.COM.COM',
                          'HOTMAIL.COM/MECHIBL_2000@HOTMAIL.COM', 
                          'GMAI.COM', 'GMIAL.COM', 'GNMAIL.COM', 
                          '@MAIL.COM', 'Ñ', ' ', '  ', '   ', 
                          'GMAIL.COMN', 'GMNAIL.COM', 'Á', 'É', 'Í', 'Ó', 'Ú',
                          '@GIMAIL.COM', '@GMAIL.CONM', '@GMA.IL.COM', '?' , ','  ]
    
    if any(palabra in row['EMAIL ANTERIOR'] for palabra in palabras_a_buscar):
        return 'REGULARIZARCORREO@GMAIL.COM'
    else:
        return row['EMAIL ANTERIOR']
    
kashio['EMAIL ANTERIOR'] = kashio.apply(correccion, axis = 1)

kashio['EMAIL'] = kashio['EMAIL ANTERIOR']

kashio = kashio[columnas] #nos quedamos solo con las columnas necesarias

#%% columna verificadora de correos
kashio['dominio'] = kashio['EMAIL'].str.split('@', expand = True)[1]

kashio['dominio'] = kashio['dominio'].fillna('REGULARIZARCORREO@GMAIL.COM')
kashio.loc[kashio['dominio'] == ''  , 'dominio'] = 'REGULARIZARCORREO@GMAIL.COM'

def regularizar_correo(kashio):
    if ('REGULARIZARCORREO@GMAIL.COM' in kashio['dominio']):
        return 'REGULARIZARCORREO@GMAIL.COM'
    else:
        return kashio['EMAIL']
kashio['EMAIL'] = kashio.apply(regularizar_correo, axis = 1)    

#%% REPORTE DE CLIENTES CORREGIDO PARA CHEQUEAR LOS CORREOS
if crear_archivo == True:

    nombre = "Correo corregido " + str(ARCHIVO_HOY[29:37]) + ".xlsx"
    try:
        ruta = nombre
        os.remove(ruta)
    except FileNotFoundError:
        pass

    kashio.to_excel(nombre, index = False)

else:
    pass

#%% Ponemos los correos corregidos en el otro reporte (el más grande)

# AUTOMATICAMENTE LEERÁ EL SEGUNDO ARCHIVO
kashio_ampliado = pd.read_excel('DATA_RECIBOS_COOP.SANMIGUEL_' + str(ARCHIVO_HOY[29:37]) + '.xlsx',
                                dtype = {'ID CLIENTE (*)'   : str,
                                         'REFERENCIA'       : str,
                                         'ID ORDEN DE PAGO' : str}
                                )

kashio_ampliado = kashio_ampliado.rename(columns = {"NOMBRE" : "NOMBRE_1"})

#%% AJUSTE DE TEXTO PARA DXP LIQUIDADOS
mask_liquidados = kashio_ampliado['Unnamed: 10'] == 'LIQUIDADOS' #si en el fincore le cambian el nombre a esta columna, pues va a fallar esta línea

kashio_ampliado.loc[mask_liquidados, 
                    'DESCRIPCION'] = kashio_ampliado.loc[mask_liquidados, 
                                                         'DESCRIPCION'].str.replace('PRESTAMO DESCUENTO POR PLANILLA', 
                                                                                    'PRESTAMO DXP LIQUIDADOS')
                                                                                    
#%%
# kashio_sin_pyme = kashio_ampliado[kashio_ampliado['Unnamed: 10'] != 'PYME']
# kashio_sin_pyme.to_excel('RECIBOS COOP SAN MIGUEL ' + str(ARCHIVO_HOY[29:37]) + ' no incluye PYME.xlsx',
#                          index = False)

#%% FILTRACIÓN DE PYMES
if solo_pyme == True:
    try:
        kashio_ampliado = kashio_ampliado[kashio_ampliado['Unnamed: 10'] == 'PYME'] ##########
        if kashio_ampliado['Unnamed: 10'].unique() == ['PYME']:
            print('Correctamente Filtrado')
        else:
            print('Mal filtado')
            
    except KeyError:
        columna_filtro = kashio_ampliado.columns[10]
        kashio_ampliado = kashio_ampliado[kashio_ampliado[columna_filtro] == 'PYME'] ##########   
        if kashio_ampliado[columna_filtro].unique() == ['PYME']:
            print('Correctamente Filtrado')
        else:
            print('Mal filtado')
    
    except KeyError as e:
        print("Error:", e)
else:
    pass

#%% 
valor1 = kashio_ampliado.shape[0]
print(kashio_ampliado.shape[0])

kashio_ampliado = kashio_ampliado.merge(kashio, 
                                        left_on  = ['ID CLIENTE (*)'],
                                        right_on = ['ID CLIENTE'],
                                        how      = 'left')
valor2 = kashio_ampliado.shape[0]
print(kashio_ampliado.shape[0])
if valor1 != valor2:
    print('Si sale diferente hay que investigar, posiblemente hay créditos duplicados')
    print('')
else:
    print('Todo bien, no hay créditos duplicados')

#%% ARCHIVO FINAL PARA CONVERTIR A CSV

kashio_para_csv = kashio_ampliado[['ID CLIENTE', 
                                   'DOCUMENTO', 
                                   'NUMERO DOCUMENTO', 
                                   'NOMBRE', 
                                   'EMAIL',
                                   'TELEFONO', 
                                   'ESTADO', 
                                   'ID ORDEN DE PAGO', 
                                   'REFERENCIA', 
                                   'NOMBRE_1',
                                   'DESCRIPCION', 
                                   'MONEDA', 
                                   'MONTO', 
                                   'VENCIMIENTO', 
                                   'EXPIRACION']]

kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Á', 'A')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('É', 'E')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Í', 'I')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Ó', 'O')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Ú', 'U')

kashio_para_csv['DOCUMENTO'] = 'OTHER'

kashio_para_csv['MONTO'] = kashio_para_csv['MONTO'].round(2)

kashio_para_csv['EXPIRACION'] = '31/12/2050'  #fecha arbitrariamente lejana (actualmente se está poniendo un str)
                                #pd.Timestamp('2050-12-31') si es que necesitaramos que esté en formato DateTime

#%% VERIFICADOR DE FECHAS DE VENCIMIENTO
# Por lo menos debemos tener hasta fechas del fin de mes actual
kashio_para_csv['VENCIMIENTO parseado'] = pd.to_datetime(kashio_para_csv['VENCIMIENTO'])

# Obtén la fecha actual
# obtenemos la fecha del nombre del archivo que estamos trabajando
fecha_actual = datetime.date(int(str(ARCHIVO_HOY[29:33])), # año
                             int(str(ARCHIVO_HOY[33:35])), # mes
                             int(str(ARCHIVO_HOY[35:37]))) # día

# fecha_actual = datetime.date.today() # este método busca la fecha de hoy en el sistema

# Obtiene el último día del mes
ultimo_dia_del_mes = datetime.date(fecha_actual.year, 
                                   fecha_actual.month, 
                                   calendar.monthrange(fecha_actual.year, 
                                                       fecha_actual.month)[1])

# Verifica si estás en diciembre
if fecha_actual.month == 12:
    # Si es diciembre, configura el mes al próximo año y el día al último día de enero
    ultimo_dia_del_siguiente_mes = datetime.date(fecha_actual.year + 1, 1, 31)
else:
    # Si no es diciembre, calcula el último día del mes siguiente
    ultimo_dia_del_siguiente_mes = datetime.date(fecha_actual.year, 
                                                 fecha_actual.month + 1, 
                                                 calendar.monthrange(fecha_actual.year, 
                                                                     fecha_actual.month + 1)[1])
# Comparación de fechas
if pd.Timestamp(ultimo_dia_del_mes).day - pd.Timestamp(fecha_actual).day > 4:
    if pd.Timestamp(ultimo_dia_del_mes) in list(kashio_para_csv['VENCIMIENTO parseado']):
        print(Back.GREEN + 'Fechas bien puestas')
    else:
        print(Back.RED + '🚨🚨 Las fechas están mal 🚨🚨, cambiar la segunda en el fincore al último día del mes')
elif pd.Timestamp(ultimo_dia_del_siguiente_mes) in list(kashio_para_csv['VENCIMIENTO parseado']):
    print(Back.GREEN + 'Fechas bien puestas')
else:
    print(Back.RED + '🚨🚨 Las fechas están mal 🚨🚨, cambiar la segunda en el fincore al último día del mes')
    
# Columna ya no necesaria
kashio_para_csv.drop('VENCIMIENTO parseado', 
                     axis    = 1, 
                     inplace = True)

#%% EXPORTAR A CSV 
# kashio_para_csv.to_excel('GeneracionData ' + str(ARCHIVO_HOY[29:37]) + '.xlsx', 
#                        index    = False,
#                        encoding = 'utf-8-sig')

kashio_para_csv.to_csv('GeneracionData ' + str(ARCHIVO_HOY[29:37]) + '.csv', 
                       index    = False,
                       encoding = 'utf-8-sig')
# En esta línea de código, se utiliza la codificación 'utf-8-sig'. 
# Esta codificación es similar a UTF-8, pero agrega un carácter de marca 
# de orden de bytes (BOM) al principio del archivo CSV. El BOM es un 
# indicador que algunos programas y sistemas utilizan para reconocer 
# que el archivo está codificado en UTF-8. Esta opción es útil cuando 
# necesitas garantizar que el archivo CSV se interprete correctamente 
# en programas que requieren un BOM, como Microsoft Excel.

#%% EXPORTAR A EXCEL SI ES QUE ES NECESARIO CREAR EL REPORTE MENSUAL

if mensajeria_preventiva == True:
    kashio_para_csv.to_excel('insumo cobranzas en caso de necesitar el reporte.xlsx',
                             index = False)
else:
    pass

