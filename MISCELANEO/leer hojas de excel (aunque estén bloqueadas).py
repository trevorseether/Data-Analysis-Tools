# -*- coding: utf-8 -*-
"""
Created on Wed May 24 18:33:42 2023

@author: Joseph Montoya
"""
import pandas as pd
import os

os.chdir('C:\\Users\\user\\Desktop') #ubicación

objeto_excel = pd.ExcelFile('ddatos.xlsx') #nombre del excel

nombres_hojas = objeto_excel.sheet_names #aquí obtenemos el nombre de las sheets

#%%
#obtenemos los datos:
    
df = pd.read_excel('ddatos.xlsx', sheet_name= 'Hoja2')

