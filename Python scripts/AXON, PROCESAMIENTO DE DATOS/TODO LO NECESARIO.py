# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:19:19 2024

@author: sanmiguel38
"""

# =============================================================================
# datos para netbank
# =============================================================================
import pandas as pd
import os

#%%
sub_carpeta  = '2 - Creditos'

os.chdir('R:\\REPORTES DE GESTIÓN\DESARROLLO\\Implementacion NetBank\\Datos para Migracion\\Migracion 06Nov24' + '\\' + sub_carpeta)

excel        = '02_Prestamos-completo (interés negativo corregido).xlsx'
sheet_nombre = 'prppg (2)' #  "prppg"     "prppg (2)"
filas_skip   = 19
crear_csv    = True

activar_limpieza    = False
activar_strip       = False
eliminar_duplicados = True

#%%
base = pd.read_excel(excel,
                     sheet_name = sheet_nombre,
                     skiprows   = filas_skip,
                     dtype      = str)

#%% strip eliminación de espacios
columnas_strip = ['socio', 'DireccionDNI']

if activar_strip == True:
    for i in columnas_strip:
        base[i] = base[i].str.strip()

#%%
if activar_limpieza == True:
    columnas_limpiar = ['socio', 'DireccionDNI']
    
    total_reemplazos = 0
    def contar_reemplazos(df, columna, char_a_reemplazar):
        global total_reemplazos
        # Calcular longitud antes del reemplazo
        longitud_antes = df[columna].str.len().sum()
        # Reemplazar el carácter
        df[columna] = df[columna].str.replace(char_a_reemplazar, '', regex=False)
        # Calcular longitud después del reemplazo
        longitud_despues = df[columna].str.len().sum()
        # Contar cuántos reemplazos se hicieron
        reemplazos = longitud_antes - longitud_despues
        total_reemplazos += reemplazos
        print(f"Reemplazos de '{char_a_reemplazar}': {reemplazos}")
    
    for i in columnas_limpiar:
        base[i] = base[i].str.strip()
        contar_reemplazos( base, i, '?')
        contar_reemplazos( base, i, '¿')
        contar_reemplazos( base, i, '|')
        contar_reemplazos( base, i, '*')
        contar_reemplazos( base, i, ';')
        contar_reemplazos( base, i, '!')
        contar_reemplazos( base, i, '=')
        contar_reemplazos( base, i, '*')
    
#%% validación de duplicados
columna = 'indice que debe ser único'

base[columna] = base['NroPrestamo'] + '-' + base['numerocuota']

columna_que_no_debe_duplicarse = columna

# número de orden del archivo original
base['orden original'] = range(1, len(base) + 1)

#%%
df_duplicados = base[base.duplicated(subset = columna_que_no_debe_duplicarse, 
                                     keep   = False)]

if eliminar_duplicados == True:
    if df_duplicados.shape[0] == 0:
        print('sin duplicados')
    else:
        print('existen duplicados')
        # base = base.drop_duplicates(subset = columna_que_no_debe_duplicarse, 
        #                             keep   = 'first')

#%%
# kashio = base.copy()
# kashio['EMAIL'] = kashio['gbemamail'].copy()

# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.PE'  , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.COM' , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCON'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAI.COM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GGMIAL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GNMAIL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMA.IL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL..COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL'         , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HMAIL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMIL.COM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMEIL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@OUTOOK.ES'     , '@OUTLOOK.ES')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.C'     , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAILCOM'    , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAI.COM'    , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.CO'  , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.COMOM' , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.COMOM.PE' , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMJM'   , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMOM'   , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAOL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAIL.COM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMC.OM' , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPM'   , '@GMAIL.COM')

# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAL.COM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIIL.COM'  , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAL.COM'    , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPM'   , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMIAL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCOM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAI.COM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAL.COM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CCOM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL .COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILO.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCOM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COPM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMAIL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')    
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMCALLE CESAR VALEJO 420 INT' , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CM'      , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILC.OM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMIAL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GNAIL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GAMAIL.COM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COJM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAOL.COM'     , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.'    , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.CM'  , '@GMAIL.COM')

# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@OUTLOOCK.COM' , '@OUTLOOK.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIOL.COM' , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@OUTLOC.COM'   , '@OUTLOOK.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMCM'  , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPE'  , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM*9'  , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMPE'  , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM614' , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HTOMAIL.COM'  , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HPTMAIL.COM'  , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GHOTMAIL.COM' , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMAIL.COMO' , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HTMAIL.COM'   , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTAMIL.COM'  , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOTMIAL.COM'  , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HTMAIL.COM'   , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@HOSMAIL.COM'  , '@HOTMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@.COM'         , '@GMAIL.COM')
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COML'   , '@GMAIL.COM')


# # usando regular expresions
# kashio['EMAIL'] = kashio['EMAIL'].str.replace(r'@GMAIL$', '@GMAIL.COM', 
#                                               regex = True)
# kashio['EMAIL'] = kashio['EMAIL'].str.replace(r'@HOTMAIL$', '@HOTMAIL.COM', 
#                                               regex = True)


# kashio.loc[kashio['EMAIL'] == 'CARLOSCASTILLOFUENTES12@'  , 'EMAIL'] = 'CARLOSCASTILLOFUENTES12@GMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'DENIS_POBLETE@GHOTMAIL.COM', 'EMAIL'] = 'DENIS_POBLETE@HOTMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'RAQUELALINA@GNAIL.COM'     , 'EMAIL'] = 'RAQUELALINA@GMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'RRENGIFOCORAL@HOTMAIL..COM', 'EMAIL'] = 'RRENGIFOCORAL@HOTMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'TATO.12.TLV@GMAOL.COM'     , 'EMAIL'] = 'TATO.12.TLV@GMAIL.COM'
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM\n.COM', '@GMAIL.COM')    

# kashio.loc[kashio['EMAIL'] == 'BRAULIO.18@@HOTMAIL.COM'          , 'EMAIL'] = 'BRAULIO.18@HOTMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'GISELAISABELLEONATOCHE@GMAIL.'    , 'EMAIL'] = 'GISELAISABELLEONATOCHE@GMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'RAQUELALINA@GNAIL.COMALDAIRPOLOPASTOR@GMAIL.COM9614' , 'EMAIL'] = 'ALDAIRPOLOPASTOR@GMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'HERRERA2019ROMULO@OUTLOOK.COM-'   , 'EMAIL'] = 'HERRERA2019ROMULO@OUTLOOK.COM'
# kashio.loc[kashio['EMAIL'] == 'CESARSOLISBARRETO@GM,AIL.COM'     , 'EMAIL'] = 'CESARSOLISBARRETO@GMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'LISSET_SS@HOTM,AIL.COM', 'EMAIL'] = 'LISSET_SS@HOTMAIL.COM'
# kashio['EMAIL'] = kashio['EMAIL'].str.replace('@KONECTA_GROUP.COM'    , '@KONECTA-GROUP.COM')    

# kashio.loc[kashio['EMAIL'] == 'MARJORIE.LIBRAVITVIL1994@GMAIL', 'EMAIL'] = 'MARJORIE.LIBRAVITVIL1994@GMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'CIBER_APOL@HOTMAIL'            , 'EMAIL'] = 'CIBER_APOL@HOTMAIL.COM'
# kashio.loc[kashio['EMAIL'] == 'JSU8095@GMAIL.COM*9'           , 'EMAIL'] = 'JSU8095@GMAIL.COM'

# ###############################################################################
# kashio['EMAIL ANTERIOR'] = kashio['EMAIL'] #si reactivamos la celda anterior, esto habría que eliminarlo o comentarlo

# def correccion(row):
#     palabras_a_buscar = [ 'GMAILCON', '\\', '/', 'FMAIL.COM', 
#                           'GAMIL.COM', 'GEMAIL.COM', 'GMAIL.COM.COM',
#                           'HOTMAIL.COM/MECHIBL_2000@HOTMAIL.COM', 
#                           'GMAI.COM', 'GMIAL.COM', 'GNMAIL.COM', 
#                           '@MAIL.COM', 'Ñ', ' ', '  ', '   ', 
#                           'GMAIL.COMN', 'GMNAIL.COM', 'Á', 'É', 'Í', 'Ó', 'Ú',
#                           '@GIMAIL.COM', '@GMAIL.CONM', '@GMA.IL.COM', '?' , ','  ]
    
#     if any(palabra in row['EMAIL ANTERIOR'] for palabra in palabras_a_buscar):
#         return 'REGULARIZARCORREO@GMAIL.COM'
#     else:
#         return row['EMAIL ANTERIOR']
    
# kashio['EMAIL ANTERIOR'] = kashio.apply(correccion, axis = 1)

# kashio['EMAIL'] = kashio['EMAIL ANTERIOR']





# kashio['gbemamail'] = kashio['EMAIL'].copy()
# del kashio['EMAIL']
# del kashio['EMAIL ANTERIOR']

#%% filtrado de cuotas
# =============================================================================
# COMENTAR TODO ESTO SI SE VA A PROCESAR OTRAS HOJAS
# =============================================================================
base['numerocuota int'] = base['numerocuota'].astype(int)

###############################################################################
formatos = [ '%d-%m-%Y',
             '%d/%m/%Y' ] # Lista de formatos a analizar

def parse_date(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(   arg = date_str, 
                                  format = formato,)
        except ValueError:
            pass
    return pd.NaT

base['fecha timestamp'] = base['FechaVencimiento'].apply(parse_date)
###############################################################################


base['capital'] = base['capital'].astype(float)
base['interes'] = base['interes'].astype(float)

# creditos que nacen con cero, es correcto
base = base.sort_values(by=['NroPrestamo', 'fecha timestamp'], 
                        ascending=[True, True])

# Convertir la columna 'FechaVencimiento' a datetime
base['FechaVencimiento'] = base['fecha timestamp']
# base['FechaVencimiento'] = pd.to_datetime(base['FechaVencimiento'])

# Función para identificar la primera cuota
def marcar_primera_cuota(grupo):
    grupo = grupo.sort_values(by='fecha timestamp')
    grupo['Etiqueta'] = 'sin etiqueta'  # Etiqueta predeterminada
    if grupo.iloc[0]['numerocuota int'] == 0:  # Revisar si la primera cuota es 0
        grupo.iloc[0, grupo.columns.get_loc('Etiqueta')] = 'nacimiento cuota cero'
    return grupo

# Aplicar la función a cada grupo de 'NroPrestamo'
base = base.groupby('NroPrestamo', group_keys = False).apply(marcar_primera_cuota)

def mantener_cuota_cero(base):
    if (base['Etiqueta'] == 'nacimiento cuota cero') and (base['interes'] > 0):
        return '(mantener) cuota cero original con capital'
    if (base['numerocuota int'] == 0) and (base['capital'] > 0):
        return '(mantener) amortización de capital'
    if (base['numerocuota int'] == 0) and (base['capital'] == 0):
        return '(eliminar) cap cero'
    else:
        return ''
base['mantener ceros'] = base.apply(mantener_cuota_cero, axis =1 )

# =============================================================================
# hasta aquí, siguen todas las cuotas
# =============================================================================
nro_finco = '00089730'
verificar = base[base['NroPrestamo'] == nro_finco]

#%%
base = base.sort_values(by=['orden original'], 
                        ascending=[True])

conteo_lista = base.pivot_table(values  = 'NroPrestamo',
                                index   = columna,
                                aggfunc = 'count').reset_index()

conteo_cuotas_duplicadas = conteo_lista[conteo_lista['NroPrestamo'] > 1]
conteo_cuotas_duplicadas.columns = [columna, 'conteo']

# def marcar_duplicados(base):
#     if base['indice que debe ser único'] in lista_dups:
#         return 'cuota duplicada'
#     else:
#         return ''
# base['duplicidad cuota'] = base.apply(marcar_duplicados, axis = 1)
'reemplazando el bloque anterior por un merge'

base2 = base.merge(conteo_cuotas_duplicadas,
                   on = columna,
                   how = 'left')

def dups(base2):
    if base2['conteo'] >= 2:
        return 'duplicado'
    else:
        return ''
base2['duplicidad cuota'] = base2.apply(dups, axis = 1)

#%%
base2 = base2.sort_values(by=['NroPrestamo', 'fecha timestamp', 'orden original'], 
                          ascending=[True, True, True])

# duplicados, para eliminar y mostrar solo la ultima cuota, (más reciente en el tiempo)
base2['estado'] = base.duplicated(subset=['NroPrestamo', 'numerocuota int'], keep='last').map(
                    {True: 'eliminar', False: 'mantener'})

#%% finalmente, eliminar duplicados
def eliminacion_final(base2):
    
    if (base2['mantener ceros'] == '(eliminar) cap cero'):
        return 'eliminar'
    if (base2['estado'] == 'eliminar') and (base2['mantener ceros'] == ''):
        return 'eliminar'
    else:
        return 'mantener'

base2['eliminar cuota'] = base2.apply(eliminacion_final, axis = 1)

nro_finco = '00089730'
verificar = base[base['NroPrestamo'] == nro_finco]


#%%
base3 = base2[base2['eliminar cuota'] == 'mantener'].copy()

base3 = base3[['NroPrestamo', 'FechaVencimiento', 'numerocuota', 'capital', 'interes',
               'CargosGenerales', 'CargosSeguro', 'Aporte', 'TotalCargo', 'TotalPago',
               'Ahorros', 'Pagado']]

# =============================================================================
# HASTA ACÁ
# =============================================================================
#%% crear csv

base3 = base
nombre_carpeta = excel.split(".")[0]

# Ruta completa de la carpeta
ruta_carpeta = os.path.join(os.getcwd(), nombre_carpeta)

# Verifica si la carpeta ya existe
# if not os.path.exists(ruta_carpeta):
#     os.makedirs(ruta_carpeta)
#     print(f"Carpeta '{nombre_carpeta}' creada exitosamente.")
# else:
#     print(f"La carpeta '{nombre_carpeta}' ya existe.")

# if crear_csv == True:
#     print('creando csv')
#     # df1[columnas].to_csv(sheet_nombre + '.csv',  #código para el procesamiento de las cuotas
#     base3.to_csv(nombre_carpeta + '\\' + sheet_nombre + '.csv', 
#                  index    =  False,
#                  encoding =  'utf-8-sig', #'utf-8',
#                  header   =  False,
#                  sep      =  ';')
#     print('csv creado')


