# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 10:46:51 2023

@author: sanmiguel38
"""

###############################################################################
##          CRUCE DE BAJAS DE KONECTA
###############################################################################

import pandas as pd
import os
import numpy as np

#%%

'AQUI SE PONE LA FECHA QUE UNO QUIERE QUE APAREZCA EN EL NOMBRE DEL ARCHIVO'
FECHATXT = '24-07-2023'

'ubicación de trabajo'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 JULIO\\24 07 2023')

#%%
################################
#  DATA ENVIADA POR COBRANZA
################################

bajas = pd.read_excel('Bajas al 21.07.xlsx',
                    dtype=({'Documento': object}))

bajas['Documento'] = bajas['Documento'].str.strip()

uwu = bajas[pd.isna(bajas['Documento'])]
print(uwu)
bajas['Documento original'] =   bajas['Documento']
bajas['Documento'] = bajas['Documento'].str.zfill(14)
print(uwu)
del uwu

#%%
######################################################
#   REPORTE DE CRÉDITOS VIGENTES, ENVIADO POR CESAR
######################################################
vigentes = pd.read_excel("creditos vigentes SM al 24-07-23 - para bajas Konecta corte 12_40am.xlsx", #aqui cambiar el nombre y/o ubicación del archivo
                      dtype={'Doc_Identidad': object,
                             'codigosocio': object,
                             'pagare_fincore': object,
                             'fechadesembolso': object
                             })

#La función "str.strip()" se utiliza para quitar los espacios en blanco en el principio y al final de cada valor en la columna "Doc_Identidad"
vigentes["Doc_Identidad"] = vigentes["Doc_Identidad"].str.strip()
#%%
#parsenado las fechas
formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d', 
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

#%%
'por si acaso, nos quedamos solo con los que tienen estado = pendiente'

vigentes["Estado"] = vigentes["Estado"].str.strip() #quitamos espacios
vigentes["Estado"] = vigentes["Estado"].str.upper() #mayúsculas

vigentes = vigentes[vigentes["Estado"] == 'PENDIENTE']

#%%
'agregamos 14 ceros al reporte enviado POR CESAR'
vigentes["Doc_Identidad"] = vigentes["Doc_Identidad"].astype(str)
vigentes["DOC_IDENTIDAD_ceros"] = vigentes["Doc_Identidad"].str.zfill(14)

#%%
'nos quedamos solo con las columnas necesarias'

vigentes2 = vigentes[["DOC_IDENTIDAD_ceros", "Socio", "fechadesembolso", "pagare_fincore", "CuotaFija", "Planilla"]]
vigentes2 = vigentes2.rename(columns={"Doc_Identidad": "DOC_IDENTIDAD",
                                      "Socio": "SOCIO",
                                      "fechadesembolso": "FECHA_DESEMBOLSO",
                                      "pagare_fincore": "PAGARE_FINCORE",
                                      "CuotaFija": "CUOTA MENSUAL",
                                      "Planilla": "EMPRESA/PLANILLA"})

bajas2 = bajas[['Documento', 'Documento original']]
#%%
'inner join usando '
df_resultado = vigentes2.merge(bajas2, 
                         left_on=["DOC_IDENTIDAD_ceros"], 
                         right_on=['Documento']
                         ,how='inner')

#%%
'''creamos el archivo final'''

df_resultado['SALDO A DESCONTAR'] = np.nan
df_resultado['# CUOTAS'] = np.nan

final = df_resultado[['Documento original','SOCIO', 'FECHA_DESEMBOLSO', 'SALDO A DESCONTAR', '# CUOTAS',"CUOTA MENSUAL", 'PAGARE_FINCORE', "EMPRESA/PLANILLA"]]

final = final.rename(columns={'Documento original': 'Documento'})

#%%

NOMBRE = 'BAJAS '+ FECHATXT +'.xlsx'
try:

    os.remove(NOMBRE)
except FileNotFoundError:
    pass

final.to_excel(NOMBRE, index=False,
               sheet_name=FECHATXT)







