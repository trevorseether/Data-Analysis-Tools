# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 18:00:56 2023

@author: sanmiguel38
"""

import pandas as pd

import os

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 AGOSTO\\fase 3')

df = pd.read_excel('Rpt_DeudoresSBS Anexo06 - AGOSTO 2023 PROCESADO 03 FINAL.xlsx',
                   skiprows=2,
                   dtype=({'Registro 1/'             : object, 
                          'Fecha de Nacimiento 3/'   : object,
                          'Código Socio 7/'          : object,
                          'Número de Documento 10/'  : object,
                          'Relación Laboral con la Cooperativa 13/'        :object, 
                          'Código de Agencia 16/'    : object,
                          'Moneda del crédito 17/'   : object, 
                          'Numero de Crédito 18/'    : object,
                          'Tipo de Crédito 19/'      : object,
                          'Sub Tipo de Crédito 20/'  : object,
                          'Fecha de Desembolso 21/'  : object,
                          'Cuenta Contable 25/'      : object,
                          'Tipo de Producto 43/'     : object,
                          'Fecha de Vencimiento Origuinal del Credito 48/' : object,
                          'Fecha de Vencimiento Actual del Crédito 49/'    : object,
                          'Nro Prestamo \nFincore'   : object,
                          'Refinanciado TXT'         : object}))

df.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                   'Fecha de Nacimiento 3/',
                   'Número de Documento 10/',
                   'Domicilio 12/',
                   'Numero de Crédito 18/'], inplace=True, how='all')
#%%

df['Tipo de Producto 43/'] = df['Tipo de Producto 43/'].astype(float).astype(int)
def producto_txt(df_resultado_2):
    tipo_producto = df_resultado_2['Tipo de Producto 43/']
    
    if tipo_producto in [34, 35, 36, 37, 38, 39]:
        return 'DXP'
    elif tipo_producto in [30, 31, 32, 33]:
        return 'LD'
    elif tipo_producto in [21, 22, 23, 24, 25, 29]:
        return 'MICRO'
    elif tipo_producto in [15, 16, 17, 18, 19]:
        return 'PEQUEÑA'
    elif tipo_producto in [95, 96, 97, 98, 99]:
        return 'MEDIANA'
    elif tipo_producto in [41, 45]:
        return 'HIPOTECARIA'

df['TIPO DE PRODUCTO TXT'] = df.apply(producto_txt, axis=1) #chequear, aún no está probado



resultado = df.groupby('Código Socio 7/')['TIPO DE PRODUCTO TXT'].nunique()

#%%
resultado = resultado.reset_index()
#%%
resultado = resultado[resultado['TIPO DE PRODUCTO TXT'] > 1]

#%% filtradoo
def es_o_no_es(k):
    if k['Código Socio 7/'] in list(resultado['Código Socio 7/']):
        return 'es'
    else:
        return 'no es'

df['es?'] = df.apply(es_o_no_es, axis=1) #chequear, aún no está probado

              #%%
uwu = df[df['es?'] == 'es']

uwuuu =  uwu[uwu['Dias de Mora 33/'] > 30 ]            

#%%

def ahora_si(kk):
    if kk['Código Socio 7/'] in list(uwuuu['Código Socio 7/']):
        return 'sii'
    else:
        return 'ño'
    
df['es?????'] = df.apply(ahora_si, axis=1) #chequear, aún no está probado

#%% filtrado final

kho = df[df['es?????'] == 'sii']
    
kho.to_excel('creditos con diferente producto.xlsx',
                      index=False)


