# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 14:08:42 2024

@author: sanmiguel38
"""

import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter

# Ruta al archivo Excel
ruta_excel = "R:\\REPORTES DE GESTIÓN\\Procesos para Envio Masivo\\Notificacion por venta de cartera Oct.24\\ENVÍOS FÍSICOS PENDIENTES - 20-11-24\\Envío físico pendiente.xlsx"
# Carpeta donde están los PDFs
carpeta_pdf = "R:\\REPORTES DE GESTIÓN\\Procesos para Envio Masivo\\Notificacion por venta de cartera Oct.24\\ENVÍOS FÍSICOS PENDIENTES - 20-11-24\\CARTAS"
# Carpeta para guardar los PDFs sin contraseña
carpeta_salida = os.path.join(carpeta_pdf, "PDFs_sin_contraseña")
os.makedirs(carpeta_salida, exist_ok=True)

# Leer el Excel con pandas
df = pd.read_excel(ruta_excel,
                   dtype = str)

# Iterar sobre cada fila del Excel
for _, fila in df.iterrows():
    nombre_pdf = fila["nombre pdf"]
    contraseña = fila["CONTRASEÑA PDF"]

    # Rutas de entrada y salida
    ruta_pdf = os.path.join(carpeta_pdf, nombre_pdf)
    salida_pdf = os.path.join(carpeta_salida, nombre_pdf)

    # Intentar procesar el PDF
    try:
        lector = PdfReader(ruta_pdf)

        # Desbloquear el PDF
        if lector.is_encrypted:
            lector.decrypt(contraseña)

        # Crear un nuevo PDF sin contraseña
        escritor = PdfWriter()
        for pagina in lector.pages:
            escritor.add_page(pagina)

        # Guardar el PDF sin contraseña
        with open(salida_pdf, "wb") as salida:
            escritor.write(salida)

        print(f"Desbloqueado: {nombre_pdf}")
    except Exception as e:
        print(f"Error al procesar {nombre_pdf}: {e}")
