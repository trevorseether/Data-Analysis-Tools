# -*- coding: utf-8 -*-
"""
Created on Wed May 24 18:33:42 2023

@author: Joseph Montoya
"""
import pandas as pd
import os

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\aasdasd') #ubicación

objeto_excel = pd.ExcelFile('EVALUADOR CREDITICIO SAN MIGUEL 31102023.ods') #nombre del excel

nombres_hojas = objeto_excel.sheet_names #aquí obtenemos el nombre de las sheets

#%%
#obtenemos los datos:
    
df = pd.read_excel('EVALUADOR CREDITICIO SAN MIGUEL 31102023.ods', 
                   sheet_name = 'Base Campaña')

df.dropna(subset = ['Unnamed: 0', 
                    'Unnamed: 1',
                    'Unnamed: 2',
                    'Unnamed: 4',
                    'Unnamed: 11'], 
          inplace = True, 
          how     = 'all')


