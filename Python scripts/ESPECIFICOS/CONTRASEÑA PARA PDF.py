# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 09:29:26 2024

@author: sanmiguel38
"""

# pip install pypdf2

# =============================================================================
# ASIGNADOR DE CONTRASEÑA A PDF
# =============================================================================

import os
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\contraseña para pdf')
data_excel         = 'contraseñas, nombres.xlsx'
carpeta_resultados = 'resultados/'

#%%
listas = pd.read_excel(io = data_excel,
                       dtype = {'contraseña' : str})

listas['nuevo nombre'] = carpeta_resultados + listas['nuevo nombre']

#%% FUNCIÓN QUE LEE EL PDF, LO COPIA Y GUARDA OTRO, PERO CON CONTRASEÑA
def add_password(input_pdf, output_pdf, password):
    # Abrir el archivo PDF original
    with open(input_pdf, 'rb') as file:
        pdf_reader = PdfReader(file)
        pdf_writer = PdfWriter()

        # Añadir todas las páginas al PdfWriter
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        # Añadir la contraseña
        pdf_writer.encrypt(user_password  = password, 
                           owner_password = None, 
                           use_128bit     = True)

        # Escribir el PDF protegido
        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)

#%%
# # Uso de la función
# input_pdf  = 'SITUACION ECONÓMICA ABRIL 2024_CLIENTES CIB_03_04_2024.pdf'
# output_pdf = 'pdf_protegido.pdf'
# password   = '123'

# #%%
# add_password(input_pdf, output_pdf, password)

#%%
listas.apply(lambda row: add_password(row['nombre original'], 
                                      row['nuevo nombre']   , 
                                      row['contraseña'])    , axis = 1)




