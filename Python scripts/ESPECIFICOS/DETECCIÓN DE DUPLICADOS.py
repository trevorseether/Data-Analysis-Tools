# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 17:29:23 2023

@author: sanmiguel38
"""
import pandas as pd
# import numpy as np
import os

ubicacion = 'R:\\REPORTES DE GESTIÓN\\Insumo para Analisis'
nombre = 'Filtro de CCI posibles duplicados - por depurar aun.xlsx'
sheet = 'Detalle'

os.chdir(ubicacion)
data = pd.read_excel(io          = ubicacion + '\\' + nombre, 
                     sheet_name  = sheet,
                     dtype = {'codigosocio'     : str,
                              'CodSocio'        : str,
                              'NroDocIdentidad' : str,
                              'CodigoCCI'       : str,
                              'CodigoBancario'  : str,
                              'CodMoneda'       : str,
                              'InformacionAl'   : str})

del ubicacion
del nombre
del sheet

#%% INDICACIÓN DE DUPLICADOS

data['CodigoCCI'] = data['CodigoCCI'].str.strip()
data['CodigoBancario'] = data['CodigoBancario'].str.strip()
data['Socio'] = data['Socio'].str.strip()
data['CodMoneda'] = data['CodMoneda'].str.strip()
data['Banco'] = data['Banco'].str.strip()


data['duplicado cci'] = data['CodigoCCI'].duplicated(keep = False).apply(lambda x: 'si' if x else '')
data['duplicado bancario'] = data['CodigoBancario'].duplicated(keep = False).apply(lambda x: 'si' if x else '')

#%%

data['eliminar por cci'] = data.duplicated(subset = ['Socio', 
                                                     'CodigoCCI',
                                                     'CodMoneda',
                                                     'Banco'],
                                           keep = False).apply(lambda x: 'queda igual' if x else None)

data['eliminar por bancario'] = data.duplicated(subset = ['Socio', 
                                                          'CodigoBancario',
                                                          'CodMoneda',
                                                          'Banco'],
                                                keep = False).apply(lambda x: 'queda igual' if x else None)

#%% queda igual
def ELIM_cci(data):
    if data['eliminar por cci'] == None and data['duplicado cci'] == 'si':
        return 'Dupl. Elim'
    else:
        return data['eliminar por cci']    
    
data['eliminar por cci'] = data.apply(ELIM_cci, 
                                      axis=1)

def ELIM_bancario(data):
    if data['eliminar por bancario'] == None and data['duplicado bancario'] == 'si':
        return 'Dupl. Elim'
    else:
        return data['eliminar por bancario']
    
data['eliminar por bancario'] = data.apply(ELIM_bancario, 
                                      axis=1)

#%% crear excel
data.to_excel('DUPLICADOS DETECTADOS.xlsx',
              index = False)




