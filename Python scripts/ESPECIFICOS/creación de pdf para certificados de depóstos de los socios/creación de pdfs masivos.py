# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 11:59:37 2024

@author: sanmiguel38
"""

# pip install PyPDF2 pandas reportlab
# =============================================================================
#      CREADOR DE PDFS CON CONTRASEÑA
# =============================================================================

import pandas as pd
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import os
#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\envio de pdfs padron de socios y aportes\\AHORA SÍ\\REINGRESANTES\\I')

# Leer el archivo Excel
excel_file = 'reingresantes inactivos.xlsx'
df = pd.read_excel(excel_file,
                   dtype = {'Nro Doc Identidad Unificado' : str})

# Leer el PDF de 5000 hojas
input_pdf = 'I.pdf'
pdf_reader = PdfReader(input_pdf)

'''
Este script para funcionar recibe como input:
    un pdf con X cantidad de páginas
    un excel con X cantidad de filas
    en cada fila del excel debe haber un nombre de un pdf y una columna de nro de doc
    en el orden del excel, separará el pdf en cada hoja individualmente y les asignará
    el nombre y contraseña (nro documento) en orden (1era hoja, 1era fila, etc etc)
'''
#%%%
# Función para agregar contraseña a un PDF
def add_password(input_pdf, output_pdf, password):
    pdf_writer = PdfWriter()
    pdf_writer.append(input_pdf)
    
    pdf_writer.encrypt(user_pwd=password, owner_pwd=None, use_128bit=True)
    
    with open(output_pdf, 'wb') as output_file:
        pdf_writer.write(output_file)

# Crear los PDFs individuales
conteo = 1
for index, row in df.iterrows():
    
    nombre_pdf = row['Nombre pdf']
    contraseña = row['Nro Doc Identidad Unificado']
    
    # Crear un PDF en blanco y agregar la página del PDF original
    output_pdf_path = f"{nombre_pdf}.pdf"
    pdf_writer = PdfWriter()
    pdf_writer.add_page(pdf_reader.pages[index])
    
    # Guardar el PDF sin contraseña
    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    
    # Agregar contraseña al PDF
    add_password(output_pdf_path, output_pdf_path, contraseña)
    
    print(f"Guardado {output_pdf_path} con contraseña")
    
    print(conteo)
    conteo += 1
    
print("Proceso completado.")
