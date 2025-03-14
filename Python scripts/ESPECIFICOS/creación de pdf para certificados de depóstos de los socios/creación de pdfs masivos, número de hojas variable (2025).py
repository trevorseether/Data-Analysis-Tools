# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 18:26:36 2024

@author: sanmiguel38
"""

import pandas as pd
from PyPDF2 import PdfWriter, PdfReader
import os

# Cambiar al directorio donde tienes los archivos
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\PDFS CERTIFICADOS DE APORTES\\ACTIVOS\\correos correctos')

# Leer el archivo Excel
excel_file = 'output_part_1.xlsx'
df = pd.read_excel(excel_file, dtype={'Nro Doc Identidad Unificado': str}) # ESTE ES IMPORTANTE PORQUE SERÁ LA CONTRASEÑA DEL PDF

# Leer el PDF de origen
input_pdf = 'p1.pdf'
pdf_reader = PdfReader(input_pdf)

# Número de páginas por PDF (puedes modificar esta variable)
nro_hojas_por_pdf = 1  # Cambia a 1, 2, 3, etc. según número de hojas necesarias por pdf

agregar_contraseña = True #True o False

nombre_carpeta = excel_file.split(".")[0]

#%%

if not os.path.exists(nombre_carpeta):
    os.makedirs(nombre_carpeta)
else:
    print('la carpeta ya existe')

os.chdir(nombre_carpeta)


# Función para agregar contraseña a un PDF
def add_password(input_pdf, output_pdf, password):
    pdf_writer = PdfWriter()
    pdf_writer.append(input_pdf)
    pdf_writer.encrypt(user_pwd = password, owner_pwd = None, use_128bit = True)
    with open(output_pdf, 'wb') as output_file:
        pdf_writer.write(output_file)

# Crear los PDFs con la cantidad de páginas especificada
conteo = 1
for index, row in df.iterrows():
    nombre_pdf = row['Nombre pdf']
    contraseña = row['Nro Doc Identidad Unificado']   # ESTA COLUMNA ES LA CONTRASEÑA
    
    # Crear un nuevo PDF y agregar las páginas correspondientes
    output_pdf_path = f"{nombre_pdf}"
    pdf_writer = PdfWriter()
    
    # Agregar las páginas al PDF según el valor de nro_hojas_por_pdf
    for i in range(nro_hojas_por_pdf):
        page_index = index * nro_hojas_por_pdf + i
        if page_index < len(pdf_reader.pages):  # Verifica si la página existe
            pdf_writer.add_page(pdf_reader.pages[page_index])
    
    # Guardar el PDF sin contraseña
    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    
    # Agregar contraseña al PDF
    if agregar_contraseña == True:
        add_password(output_pdf_path, output_pdf_path, contraseña)
    
    print(f"Guardado {output_pdf_path} con contraseña")
    print(conteo)
    conteo += 1
    
print("Proceso completado.")
