# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 18:04:24 2024

@author: sanmiguel38
"""

# !pip install PyPDF2
import PyPDF2
import pandas as pd
import os
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\parámetros netbank')

# Función para extraer texto de un PDF
def extraer_texto(pdf_path):
    with open(pdf_path, 'rb') as archivo_pdf:
        lector_pdf = PyPDF2.PdfReader(archivo_pdf)
        texto = ''
        for pagina in range(len(lector_pdf.pages)):
            texto += lector_pdf.pages[pagina].extract_text()
        return texto

# Ruta al archivo PDF
ruta_pdf = "parametros maestro netbank.pdf"

# Extraer texto del PDF
texto_pdf = extraer_texto(ruta_pdf)

# Convertir texto a un DataFrame (ejemplo simple)
# Aquí puedes procesar el texto extraído según la estructura de tu PDF
# Por ejemplo, puedes dividir el texto en líneas y luego en columnas, etc.

lineas = texto_pdf.split('\n')
data = [linea.split(',') for linea in lineas]

# Crear DataFrame
df = pd.DataFrame(data)

#%%
df = df.fillna('') # eliminación de NULL

df['concatenado'] = df[0] + df[1] + df[2] + df[3] + df[4] #columna con solo los datos relevantes
df['concatenado'] = df['concatenado'].str.strip()

x = df['concatenado'].str.split('  ', expand=True) #separado cuando hay 2 espacios

###### arreglando unas columnas que no tenían datos
x[1] = x[1].fillna('')
def arreglando_1_null(df):
    if df[1] == '':
        return df[0]
    else:
        return df[1]
    
x[1] = x.apply(arreglando_1_null, axis=1)

###### reemplazando unas celdas completas por 'Tipo:'
def asd(row):
    if 'Tipo:' in row[0]:
        return 'Tipo:'
    else:
        return row[0]
x[0] = x.apply(asd, axis=1)   
#####

df[1] = df[1].str.replace('Tipo: ', '') #reemplazo dentro de cadena string

df = x[x[0].str.contains(r'\d|Tipo:')] #filtramos filas
df = df[~df[0].str.match(r'\d{2}:\d{2}:\d{2}')] #eliminamos las que tienen fechas

df['Tipo'] = df[1].where(df[0] == 'Tipo:').ffill() #forward fill para autompletar los valores hacia abajo

df['Tipo'] =df['Tipo'].str.replace('Tipo: ', '') #reemplazo dentro de cadena string

#%%
nuevo_df = df[['Tipo', 0 , 1]] # nuevo df con las columnas necesarias

nuevo_df['Tipo'] = nuevo_df['Tipo'].str.strip() 
nuevo_df[1] = nuevo_df[1].str.strip()

nuevo_df[['Numero', 'Texto']] = nuevo_df['Tipo'].str.split(' ', 1, expand=True) #separación del texto

nuevo_nuevo = nuevo_df[['Numero', 'Texto', 0 , 1]]  #columnas necesarias

nuevo_nuevo = nuevo_nuevo[nuevo_nuevo[0] != 'Tipo:'] #eliminamos filas que ya no necesitamos

# nuevo_nuevo['Numero'] = nuevo_nuevo['Numero'].astype(int) #conversión a int

# nuevo_nuevo[0] = nuevo_nuevo[0].astype(int) #conversión a int

#%% creación del excel

nuevo_nuevo.to_excel('parámetros estructurados.xlsx',
                     index = False)

