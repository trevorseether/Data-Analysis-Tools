# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:26:48 2024

@author: sanmiguel38
"""

import pandas as pd

# Ejemplo de datos
data = {'nro de crédito': [1, 1, 1, 2, 2, 3, 3, 3, 3],
        'valor cuota': [100, 100, 100, 200, 200, 150, 150, 150, 150],
        'enumeración original': [0, 1, 2, 0, 1, 1, 2, 3, 4]}  # Ejemplo con errores en la enumeración
df = pd.DataFrame(data)

# Ajustar enumeración usando transform
def ajustar_enumeracion(grupo):
    if grupo.iloc[0] == 1:  # Si el primer valor del grupo empieza en 1
        return range(1, len(grupo) + 1)
    else:  # Si empieza en 0
        return range(len(grupo))

df['enumeración ajustada'] = (
    df.groupby('nro de crédito')['enumeración original']
    .transform(ajustar_enumeracion)
)
