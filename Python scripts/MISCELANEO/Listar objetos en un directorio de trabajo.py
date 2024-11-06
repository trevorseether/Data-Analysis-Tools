# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:44:02 2024

@author: sanmiguel38
"""
# =============================================================================
# LISTAR TODOS LOS ARCHIVOS EXISTENTES EN UN DIRECTORIO DE TRABAJO
# =============================================================================
import os
import pandas as pd

#%%
directorio = 'R:\\REPORTES DE GESTIÓN\\Insumo para Analisis\\CHERNANDEZ\\Cartas por Cartera Vendida Oct24\\pdfs para envío masivo\\correo bien tipeado'

#%%
def listar_objetos_en_directorio(directorio):
    try:
        # Obtiene la lista de objetos en el directorio
        objetos = os.listdir(directorio)
        return objetos
    except FileNotFoundError:
        print("El directorio especificado no existe.")
        return []

# Ejemplo de uso
objetos = listar_objetos_en_directorio(directorio)


#%%


numbers_list = list(range(1, len(objetos)+1))

# Crear el DataFrame con nombres de columnas
datos = {
    "pdefes": objetos,
    "numero": numbers_list
}

df = pd.DataFrame(datos)
# Mostrar el DataFrame