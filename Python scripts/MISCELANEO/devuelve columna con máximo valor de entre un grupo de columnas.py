# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:08:52 2024

@author: sanmiguel38
"""

import pandas as pd

def columna_maxima_en_fila(fila):

    """
    Devuelve el nombre de la columna con el valor numérico máximo en una fila.
    """

    return fila.idxmax()

# Ejemplo de DataFrame
data = {
    'Columna1': [1, 2, 3, 5, 5],
    'Columna2': [5, 4, 3, 2, 1],
    'Columna3': [2, 3, 4, 5, 1],
    'Columna4': [4, 1, 5, 2, 3],
    'Columna5': [3, 2, 1, 4, 5]
}
df = pd.DataFrame(data)

# Aplicar la función a cada fila y crear una nueva columna con el resultado
df['Columna_Max'] = df[['Columna5',
                        'Columna4',
                        'Columna3',
                        'Columna2',
                        'Columna1']].apply(columna_maxima_en_fila, axis=1)

print(df)

