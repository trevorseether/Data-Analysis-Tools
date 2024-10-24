# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 10:17:42 2024

@author: sanmiguel38
"""

import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\DEPURACIÓN NEGATIVOS')

base = pd.read_excel('Plantilla_Bloqueos_ListaNegra.xlsx',
                     sheet_name = 'Listas',
                     skiprows   = 21,
                     dtype = str)

base['lnlngnomc'] = base['lnlngnomc'].str.strip()
base['lnlngnomc'] = base['lnlngnomc'].str.replace(',', ' ', regex=False)
base['lnlngnomc'] = base['lnlngnomc'].str.strip()
base['lnlngnomc'] = base['lnlngnomc'].str.lstrip('.') # eliminación de punto al inicio del texto
base['lnlngnomc'] = base['lnlngnomc'].str.strip()

base['lnlngndid'] = base['lnlngndid'].str.strip()

base['nombre + documento'] = base['lnlngnomc'].fillna('') + ' ' + base['lnlngndid'].fillna('')
base['nombre + documento'] = base['nombre + documento'].str.strip()

#%% eliminación de caracteres especiales
# base['lnlngnomc'] = base['lnlngnomc'].str.replace('?', '', regex=False)
# base['lnlngnomc'] = base['lnlngnomc'].str.replace('¿', '', regex=False)
# base['lnlngnomc'] = base['lnlngnomc'].str.replace('|', '', regex=False)
# base['lnlngnomc'] = base['lnlngnomc'].str.replace('°', '', regex=False)
# base['lnlngnomc'] = base['lnlngnomc'].str.replace('*', '', regex=False)
# base['lnlngnomc'] = base['lnlngnomc'].str.replace(',', '', regex=False)
# base['lnlngnomc'] = base['lnlngnomc'].str.replace(';', '', regex=False)

# Inicializar un contador para cada carácter a reemplazar
total_reemplazos = 0

# Función para contar reemplazos
def contar_reemplazos(df, columna, char_a_reemplazar):
    global total_reemplazos
    # Calcular longitud antes del reemplazo
    longitud_antes = df[columna].str.len().sum()
    # Reemplazar el carácter
    df[columna] = df[columna].str.replace(char_a_reemplazar, '', regex=False)
    # Calcular longitud después del reemplazo
    longitud_despues = df[columna].str.len().sum()
    # Contar cuántos reemplazos se hicieron
    reemplazos = longitud_antes - longitud_despues
    total_reemplazos += reemplazos
    print(f"Reemplazos de '{char_a_reemplazar}': {reemplazos}")

# Aplicar los reemplazos y contar
contar_reemplazos( base, 'lnlngnomc', '?') 
contar_reemplazos( base, 'lnlngnomc', '¿') 
contar_reemplazos( base, 'lnlngnomc', '|') 
contar_reemplazos( base, 'lnlngnomc', '°') 
contar_reemplazos( base, 'lnlngnomc', '*') 
contar_reemplazos( base, 'lnlngnomc', ';') 
contar_reemplazos( base, 'lnlngnomc', '!') 
contar_reemplazos( base, 'lnlngnomc', '=') 
contar_reemplazos( base, 'lnlngnomc', '#') 

# Mostrar el total de reemplazos
print(f"Total de reemplazos realizados: {total_reemplazos}")

#%% ordenamiento para eliminar duplicados
base['lnlngcpri_int'] = base['lnlngcpri'].astype(int)

df_ordenado_multi = base.sort_values(by          = ['lnlngcpri_int'], 
                                     ascending   = [False], 
                                     na_position = 'first')

# df_ordenado_multi['nombre + documento'] = df_ordenado_multi['lnlngnomc'] + ' ' + df_ordenado_multi['lnlngndid']

df_ordenado_multi[df_ordenado_multi['nombre + documento'] == '7 KARNES']

#%%
df_sin_duplicados = df_ordenado_multi.drop_duplicates(subset = 'nombre + documento',
                                                      keep   = 'first')

#%%
lista_numeros = list(df_sin_duplicados['lnlngcpri_int'])

def depurar(base):
    if base['lnlngcpri_int'] in lista_numeros:
        return 'mantener'
    else:
        return 'depurar'

base['depuración'] = base.apply(depurar, axis = 1)

#%%
para_union = df_sin_duplicados[['lnlngndid', 'lnlngnomc', 'lnlngcpri_int']]
para_union.columns = ['num', 'nom', 'lnlngcpri_int']

base = base.merge(para_union,
                  on  = 'lnlngcpri_int',
                  how = 'left')

#%%%
# Crear una columna booleana indicando si la empresa tiene al menos un "documento" no nulo
base['tiene_documento'] = base.groupby('lnlngnomc')['lnlngndid'].transform(lambda x: x.notna().any())

# Añadir la etiqueta 'depurar' a aquellas filas donde 'lnlngndid' sea nulo pero la empresa tenga un registro con documento
base['depurar'] = base.apply(lambda row: 'Depurar' if pd.isna(row['lnlngndid']) and row['tiene_documento'] else 'No Depurar', axis=1)

# Eliminar la columna auxiliar 'tiene_documento'
# base = base.drop(columns=['tiene_documento'])

#%%
base.to_excel('revisar.xlsx',
              index = False)


