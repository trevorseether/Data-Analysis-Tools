# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 09:56:31 2023

@author: sanmiguel38
"""

import pandas as pd
import os
from datetime import datetime
import numpy as np

'AQUÍ SE PONE EL DIRECTORIO DE LOS ARCHIVOS CON LOS QUE VAMOS A TRABAJAR'
DIRECTORIO = "C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 JUNIO\\16 junio 2023"
os.chdir(DIRECTORIO)

'AQUI SE PONE LA FECHA QUE UNO QUIERE QUE APAREZCA EN EL NOMBRE DEL ARCHIVO'
FECHATXT = '16-06-2023'
#%%
'función poderosa para convertir texto de fechas a fechas datetime'
def parse_date(date_str):
    try:
        # Intentar parsear como fecha con formato DD/MM/YYYY HH:MM:SS
        return datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        try:
            # Si falla, intentar parsear como fecha con formato DD/MM/YYYY
            return datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            try:
                # Si falla, intentar parsear como fecha con formato DD-MM-YYYY HH:MM:SS
                return datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S')
            except ValueError:
                try:
                    # Si falla, intentar parsear como fecha con formato DD-MM-YYYY HH:MM:SS
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return date_str

#%%    
'importación de los excels'

columna_de_dni = 'Documento' #por si cambian el nombre donde está el dni
#esto se hace al reporte que mandan de cobranzas
'''al momento de importar el archivo de bajas, debemos crear una columna auxiliar con la fórmula
=texto(documento;"00000000000000"), que complete con ceros para tener 14 dígitos,
a este ponle el nombre de Documento, y la antigua el nombre Documentoque no funciona'''

bajas = pd.read_excel("2DO INFORME BAJAS GRUPO KONECTA.xlsm"
                      , #aqui cambiar el nombre y/o ubicación del archivo
                      dtype={columna_de_dni: object})  


bajas[columna_de_dni] = bajas[columna_de_dni].str.strip()


#%%
columna_de_dni = 'Documento'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 JUNIO')
ruta = 'C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 JUNIO'
ruta2 = ruta + '\\'
owo = pd.read_excel(ruta2 + '2DO INFORME BAJAS GRUPO KONECTA.xlsm',
                    dtype=({'Documento': object}))

owo['Documento'] = owo['Documento'].str.strip()

uwu = owo[pd.isna(owo['Documento'])]
print(uwu)
owo['Documento'] = owo['Documento'].str.zfill(14)
print(uwu)

bajas = owo.copy()

#%%
######################################################
#   REPORTE DE CRÉDITOS VIGENTES, ENVIADO POR CESAR
######################################################
vigentes = pd.read_excel("creditos vigentes SM al 16-06-23 - para bajas Konecta corte 9_30am.xlsx", #aqui cambiar el nombre y/o ubicación del archivo
                      dtype={'Doc_Identidad': object,
                             'codigosocio': object,
                             'pagare_fincore': object
                             },
                      parse_dates=['fechadesembolso']
                                   ,
                         date_parser=parse_date)


#La función "str.strip()" se utiliza para quitar los espacios en blanco en el principio y al final de cada valor en la columna "Doc_Identidad"
vigentes["Doc_Identidad"] = vigentes["Doc_Identidad"].str.strip()

#%%
'por si acaso, nos quedamos solo con los que tienen estado = pendiente'

vigentes["Estado"] = vigentes["Estado"].str.strip()

vigentes2 = vigentes.copy() #este es un checkpoint del dataframe, por si acaso, se malogra algo, para no empezar desde el principio
vigentes = vigentes[vigentes["Estado"] == 'PENDIENTE']

#%%
'nos quedamos solo con las columnas necesarias'

vigentes2 = vigentes[["Doc_Identidad", "Socio", "fechadesembolso", "pagare_fincore", "CuotaFija", "Planilla"]]
vigentes2 = vigentes2.rename(columns={"Doc_Identidad": "DOC_IDENTIDAD",
                                      "Socio": "SOCIO",
                                      "fechadesembolso": "FECHA_DESEMBOLSO",
                                      "pagare_fincore": "PAGARE_FINCORE",
                                      "CuotaFija": "CUOTA MENSUAL",
                                      "Planilla": "EMPRESA/PLANILLA"})

bajas2 = bajas[[columna_de_dni, 'Documento original']] #hay que revisar este dataframe a ver si están todos los dnis
#%%

'agregamos 14 ceros para un mejor match'

vigentes2["DOC_IDENTIDAD"] = vigentes2["DOC_IDENTIDAD"].astype(str)
vigentes2["DOC_IDENTIDAD_ceros"] = vigentes2["DOC_IDENTIDAD"].str.zfill(14)


#%%

'inner join usando '
df_resultado = vigentes2.merge(bajas2, 
                         left_on=["DOC_IDENTIDAD_ceros"], 
                         right_on=[columna_de_dni]
                         ,how='inner')

#%%
'''creamos el archivo final'''

df_resultado['SALDO A DESCONTAR'] = np.nan
df_resultado['# CUOTAS'] = np.nan

final = df_resultado[['DOC_IDENTIDAD','SOCIO', 'FECHA_DESEMBOLSO', 'SALDO A DESCONTAR', '# CUOTAS',"CUOTA MENSUAL", 'PAGARE_FINCORE', "EMPRESA/PLANILLA"]]

#%%

NOMBRE = 'BAJAS '+ FECHATXT +'.xlsx'
try:

    os.remove(DIRECTORIO + '\\'+NOMBRE)
except FileNotFoundError:
    pass

final.to_excel(NOMBRE, index=False,
               sheet_name=FECHATXT)

#############################################################
#%%###########################################################
###      𝒐𝒑𝒄𝒊𝒐𝒏𝒂𝒍, 𝒔𝒊 𝒏𝒐𝒔 𝒑𝒂𝒔𝒂 𝒍𝒐𝒔 𝒅𝒂𝒕𝒐𝒔 𝑱𝒉𝒐𝒏    ###############
##############################################################

import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 JUNIO\\05 JUNIO 2023')

FECHATXT = '05-06-2023'

bajas_konecta = pd.read_excel('1ER INFORME BAJAS KONECTA  JUNIO 2023.xlsm')
creditos_vigentes_jhon = pd.read_excel('reporte_josep_20230605_1026.xlsx',
                                       dtype=({"Doc. Identidad": str}))

#%%
'agregamos 14 ceros al DOCUMENTO DEL REPORTE QUE ENVÍA COBRANZAS'
#para contar el nro de filas antes de procesar
filas_nulas1 = bajas_konecta[bajas_konecta["Documento"].isnull()].shape[0]
bajas_konecta["Documento"] = bajas_konecta["Documento"].astype(str)
filas_nulas2 = bajas_konecta[bajas_konecta["Documento"].isnull()].shape[0]
print(f'al principio habías {filas_nulas1} filas nulas y ahora hay {filas_nulas2}')

bajas_konecta["Documento"] = bajas_konecta["Documento"].str.zfill(14)
if bajas_konecta[bajas_konecta["Documento"].isnull()].shape[0] == 0:
    print('no se ha eliminado nada')
else:
    print('revisar')

#%%
'agregamos 14 ceros al DOCUMENTO DEL REPORTE DE VIGENTES'
creditos_vigentes_jhon['doc para después del merge'] = creditos_vigentes_jhon["Doc. Identidad"]
filas_nulas1 = creditos_vigentes_jhon[(creditos_vigentes_jhon["Doc. Identidad"].isnull()) &
                                      (creditos_vigentes_jhon["Razon Social"].isnull())].shape[0]
#creditos_sin_documento = creditos_vigentes_jhon[creditos_vigentes_jhon["Doc. Identidad"].isnull()]
creditos_vigentes_jhon["Doc. Identidad"] = creditos_vigentes_jhon["Doc. Identidad"].astype(str)
filas_nulas2 = creditos_vigentes_jhon[creditos_vigentes_jhon["Doc. Identidad"].isnull()].shape[0]
print(f'al principio habías {filas_nulas1} filas nulas y ahora hay {filas_nulas2}')

creditos_vigentes_jhon["Doc. Identidad"] = creditos_vigentes_jhon["Doc. Identidad"].str.zfill(14)
if creditos_vigentes_jhon[creditos_vigentes_jhon["Doc. Identidad"].isnull()].shape[0] == 0:
    print('no se ha eliminado nada')
else:
    print('revisar')
    
#%%
'añadiendo 8 ceros al nro de fincore del reporte de vigentes (enviado por Jhon)'
filas_nulas1 = creditos_vigentes_jhon[(creditos_vigentes_jhon["# Fincore"].isnull())].shape[0]
#creditos_sin_documento = creditos_vigentes_jhon[creditos_vigentes_jhon["# Fincore"].isnull()]
creditos_vigentes_jhon["# Fincore"] = creditos_vigentes_jhon["# Fincore"].astype(str)
filas_nulas2 = creditos_vigentes_jhon[creditos_vigentes_jhon["# Fincore"].isnull()].shape[0]
print(f'al principio habías {filas_nulas1} filas nulas y ahora hay {filas_nulas2}')

creditos_vigentes_jhon["# Fincore"] = creditos_vigentes_jhon["# Fincore"].str.zfill(8) #añadiendo ceros
if creditos_vigentes_jhon[creditos_vigentes_jhon["# Fincore"].isnull()].shape[0] == 0:
    print('no se ha eliminado nada')
else:
    print('revisar')

#%%
'juntando nombres y apellidos del reporte de Jhon'
creditos_vigentes_jhon['apellidos y nombres'] = creditos_vigentes_jhon['Ape. Paterno'] + ' ' +\
                                                creditos_vigentes_jhon['Ape. Materno'] + ' ' +\
                                                creditos_vigentes_jhon['Socio']
                                                
creditos_vigentes_jhon['# CUOTAS'] = '' #COLUMNA VACÍA
creditos_vigentes_jhon['SALDO A DESCONTAR'] = ''
#%%
'nos quedamos solo con las columnas necesarias de este último dataframe'
casi_final = creditos_vigentes_jhon[['Doc. Identidad', 'apellidos y nombres', 
                                     'Fecha Desembolso','SALDO A DESCONTAR',
                                     '# CUOTAS','Cuota',
                                     '# Fincore','Empresa',
                                     'doc para después del merge']]

nuevos_nombres = {'Doc. Identidad':      'DOC_IDENTIDAD', 
                  'apellidos y nombres': 'SOCIO',
                  'Fecha Desembolso':    'FECHA_DESEMBOLSO',
                  'Cuota':               'CUOTA MENSUAL',
                  '# Fincore':           'PAGARE_FINCORE',
                  'Empresa':             'EMPRESA/PLANILLA'}

casi_final = casi_final.rename(columns=nuevos_nombres)

#%%
#merge para quedarnos solo con los vigentes
bajas = bajas_konecta[["Documento", 
                       'Sociedad']] #esto de sociedad puede que lo necesite algún día
df_resultado = casi_final.merge(bajas, 
                                left_on=['DOC_IDENTIDAD'], 
                                right_on=["Documento"]
                                ,how='inner')
df_resultado['DOC_IDENTIDAD'] = df_resultado['doc para después del merge']
#%%
'nos quedamos con las columnas necesarias'

df_final = df_resultado[['DOC_IDENTIDAD',
                         'SOCIO',
                         'FECHA_DESEMBOLSO',
                         'SALDO A DESCONTAR',
                         '# CUOTAS',
                         'CUOTA MENSUAL',
                         'PAGARE_FINCORE',
                         'EMPRESA/PLANILLA']]

#%%
#exportación a excel
NOMBRE = 'BAJAS '+ FECHATXT +'.xlsx'
try:

    os.remove(NOMBRE)
except FileNotFoundError:
    pass

final.to_excel(NOMBRE, index=False,
               sheet_name=FECHATXT)


