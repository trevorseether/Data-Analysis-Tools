# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 10:19:10 2024

@author: sanmiguel38
"""

import os

# Define el directorio
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\CSV COSECHA\\2024\\SETIEMBRE'

# Crea el directorio si no existe, incluyendo subdirectorios
os.makedirs(directorio, exist_ok=True)

# Cambia al directorio especificado
os.chdir(directorio)
