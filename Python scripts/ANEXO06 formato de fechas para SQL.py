# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:14:46 2023

@author: CORRECTOR DE FECHAS PARA EL ANEXO06 AMPLIADO PARA SQL SERVER
"""

#%% MÓDULO NECESARIO
import pandas as pd
import os

#%% PARÁMETROS INICIALES:
anexo_del_mes = 'Rpt_DeudoresSBS Anexo06 - Diciembre 2023 - campos ampliados version final para reportes.xlsx'
ubicación = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 DICIEMBRE\\V FINAL\\para reportes'

#%% FUNCIÓN DE PARSEO
#este parseador de datos es una basura, nunca me ha funcionado
formatos = [ '%Y%m%d' ]  # Lista de formatos a analizar

def parse_date(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(arg = date_str, 
                                  format = formato,)
        except ValueError:
            pass
    return pd.NaT

#%% lectura del archivo

os.chdir(ubicación)

df =pd.read_excel(anexo_del_mes,
                 dtype={'Registro 1/'                   : object, 
                        'Fecha de Nacimiento 3/'        : object,
                        'Código Socio 7/'               : object,
                        'Tipo de Documento 9/'          : object,
                        'Número de Documento 10/'       : object,
                        'Relación Laboral con la Cooperativa 13/'   : object, 
                        'Código de Agencia 16/'         : object,
                        'Moneda del crédito 17/'        : object, 
                        'Numero de Crédito 18/'         : object,
                        'Tipo de Crédito 19/'           : object,
                        'Sub Tipo de Crédito 20/'       : object,
                        'Fecha de Desembolso 21/'       : object,
                        'Cuenta Contable 25/'           : object,
                        'Cuenta Contable Crédito Castigado 39/'     : object,
                        'Tipo de Producto 43/'          : object,
                        'Fecha de Vencimiento Origuinal del Credito 48/': object,
                        'Fecha de Vencimiento Actual del Crédito 49/': object,
                        'Nro Prestamo \nFincore'        : object,
                        'Refinanciado TXT'              : object
                        },
                 skiprows = 0)

df.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                   'Fecha de Nacimiento 3/',
                   'Número de Documento 10/',
                   'Domicilio 12/',
                   'Numero de Crédito 18/'], 
          inplace = True, 
          how = 'all')

#%% cambiando los formatos de fechas

df['Fecha de Nacimiento 3/'] = df['Fecha de Nacimiento 3/'].apply(parse_date)

df['Fecha de Desembolso 21/'] = df['Fecha de Desembolso 21/'].apply(parse_date)

df['Fecha de Vencimiento Origuinal del Credito 48/'] = df['Fecha de Vencimiento Origuinal del Credito 48/'].apply(parse_date)

df['Fecha de Vencimiento Actual del Crédito 49/'] = df['Fecha de Vencimiento Actual del Crédito 49/'].apply(parse_date)

#%% creamos el excel
try:
    ruta = 'Anx06 ' + str(anexo_del_mes[26:40]) + ' para SQL.xlsx'
    os.remove(ruta)
except FileNotFoundError:
    pass

df.to_excel(ruta,
            index = False)


