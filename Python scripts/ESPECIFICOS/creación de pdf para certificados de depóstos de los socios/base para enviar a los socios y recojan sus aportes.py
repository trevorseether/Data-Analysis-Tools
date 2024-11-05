# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 09:39:26 2024

@author: sanmiguel38
"""

# pip install num2words

# =========================================================================== #
#  TABLA PARA DATOS PARA CORRESPONDIENDIA EN WORD (NOTIFICACIÓN DE APORTES)   #
# =========================================================================== #

from num2words import num2words
import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\envio de pdfs padron de socios y aportes\\AHORA SÍ')

nombre = 'Socios habiles a DIC-23 - para envio de certif aportes.xlsx'

#%% Función personalizada para convertir números a texto con el formato deseado
def numero_a_texto(num):
    # Separar la parte entera de la parte decimal
    entero, decimal = str(num).split('.')
    
    # Convertir la parte entera a palabras
    palabras = num2words(int(entero), lang='es')
    
    # Formatear la parte decimal
    decimal_formateado = f"con {int(decimal):02d}/100"
    
    # Combinar ambas partes
    resultado = f"{palabras} {decimal_formateado} soles"
    
    # Capitalizar la primera letra
    resultado = resultado[0].upper() + resultado[1:]
    
    return resultado

#%%
padron_socios = pd.read_excel(io       = nombre, 
                              skiprows = 1,
                              dtype    = {'CodSoc'             : str,
                                          'Tipo Persona TXT'   : str,
                                          'Aporte\nFinal a DIC.23' : float,
                                          'Aporte\nFinal'      : float,
                                          'Tipo Documento TXT' : str,
                                          'Nro Doc Identidad Unificado' : str,
                                          'Email'              : str,
                                          'Celular1'           : str,
                                          'ESTADO'             : str})

#%% 
#%%
padron_socios['CodSoc']                      = padron_socios['CodSoc'].str.strip()
padron_socios['Tipo Persona TXT']            = padron_socios['Tipo Persona TXT'].str.strip()
padron_socios['Tipo Documento TXT']          = padron_socios['Tipo Documento TXT'].str.strip()
padron_socios['Nro Doc Identidad Unificado'] = padron_socios['Nro Doc Identidad Unificado'].str.strip()
padron_socios['Email']                       = padron_socios['Email'].str.strip()
padron_socios['Apellidos y Nombres']         = padron_socios['Apellidos y Nombres'].str.strip()

#padron_socios['Celular1']                    = padron_socios['Celular1'].str.strip()

columna_aporte = 'Aporte\nFinal a DIC.23' #'Aporte\nFinal'

padron_socios[columna_aporte] = padron_socios[columna_aporte].round(2)
padron_socios[columna_aporte] = round(padron_socios[columna_aporte],2)

#%%
COLUMNAS = ['CodSoc',
            'Apellidos y Nombres',
            columna_aporte,
            'Tipo Persona TXT',
            'Tipo Documento TXT',
            'Nro Doc Identidad Unificado',
            'Nacionalidad TXT',
            'Email',
            'CASTIGADOS O VENDIDOS',
            #'Celular1'
            'estado mayo 2024',
            'vendidos 2024 (los que realmente no deben aparecer)'
            ]

#%%
base = padron_socios[COLUMNAS]

#%% Aplicar la función a la columna 'Monto'
# convertimos los números a texto
padron_socios[columna_aporte] = padron_socios[columna_aporte].apply(lambda x: f"{x:.2f}")

base['Monto_en_texto'] = base[columna_aporte].apply(numero_a_texto)

#%%
base = base[base['estado mayo 2024'] == 'INACTIVO']

base = base[~pd.isna(base['CASTIGADOS O VENDIDOS'])]
base = base[pd.isna(base['vendidos 2024 (los que realmente no deben aparecer)'])]

#%% FILTRADO
base = base[base['Tipo Persona TXT'] == '1']
base = base[~pd.isna(base['Email'])]
base = base[base['Email'].str.contains('@')]
base = base[base['Email']!= '@.']
base = base[base['Email']!= '.@COM']
base = base[base['Email']!= '@.COM']
base = base[base['Email']!= '@GMAIL.COM']

base['Email2'] = base['Email'].str.replace('@GMAIL.COM.PE'  , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.COM.COM' , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAILCON'      , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAI.COM'      , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GGMIAL.COM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GNMAIL.COM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
base['Email2'] = base['Email'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMA.IL.COM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL..COM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL'         , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@HMAIL.COM'     , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMIL.COM'      , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMEIL.COM'     , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@OUTOOK.ES'     , '@OUTLOOK.ES')    
base['Email2'] = base['Email'].str.replace('@HOTMAIL.C'     , '@HOTMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@HOTMAILCOM'    , '@HOTMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@HOTMAI.COM'    , '@HOTMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.COM.CO'  , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@HOTMAIL.COMOM' , '@HOTMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@HOTMAIL.COMOM.PE' , '@HOTMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.COMJM'   , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.COMOM'   , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIL.COMM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')    
base['Email2'] = base['Email'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')    

base.loc[base['Email2'] == 'CARLOSCASTILLOFUENTES12@',   'Email'] = 'CARLOSCASTILLOFUENTES12@GMAIL.COM'
base.loc[base['Email2'] == 'DENIS_POBLETE@GHOTMAIL.COM', 'Email'] = 'DENIS_POBLETE@HOTMAIL.COM'
base.loc[base['Email2'] == 'RAQUELALINA@GNAIL.COM',      'Email'] = 'RAQUELALINA@GMAIL.COM'
base.loc[base['Email2'] == 'RRENGIFOCORAL@HOTMAIL..COM', 'Email'] = 'RRENGIFOCORAL@HOTMAIL.COM'
base.loc[base['Email2'] == 'TATO.12.TLV@GMAOL.COM',      'Email'] = 'TATO.12.TLV@GMAIL.COM'

#%%
def tipo_doc_txt(base):
    if base['Tipo Documento TXT'] == '1':
        return 'DNI: '
    if base['Tipo Documento TXT'] == '2':
        return 'C/E: '
    if base['Tipo Documento TXT'] == '5':
        return 'DNI: '

base['TipoDocTXT'] = base.apply(tipo_doc_txt, axis = 1)

base['Columna documento'] = base['TipoDocTXT'] + base['Nro Doc Identidad Unificado']

#%%
base['Incremental'] = range(1, len(base) + 1)

base['Nombre pdf'] = base['CodSoc'] + '_' + base['Apellidos y Nombres']

#%% CREANDO ÍNDICE
# Definir la cantidad máxima de filas por archivo
# max_rows_per_file = 5000

# # Calcular el número total de archivos necesarios
# total_rows = base.shape[0]
# num_files = (total_rows // max_rows_per_file) + 1

# # Guardar cada parte en un archivo separado
# os.chdir('activos')
# for i in range(num_files):
#     start_row = i * max_rows_per_file
#     end_row = start_row + max_rows_per_file
#     subset_df = base.iloc[start_row:end_row]

#     # Guardar el DataFrame en un archivo Excel
#     file_name = f'output_part_{i+1}.xlsx'
#     subset_df.to_excel(file_name, index=False)

#     print(f'Guardado {file_name}')

base.to_excel('reingresantes inactivos.xlsx',
              index = False)

