# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 18:06:24 2025

@author: sanmiguel38
"""

# =============================================================================
#                                   BD - 02
# =============================================================================

import pandas as pd
import os
import pyodbc
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('R:/REPORTES DE GESTIÓN/Insumo para Analisis/prppgs, cortes trimestrales')

cuotas = pd.read_csv('prppg 2024-12-31.csv')

#%%









'''








select top 1000 CodEstado,* from PrestamoCuota
where CodEstado = 1003

CodEstado = 22 -- cancelado
1003 = -- cuota cero amortización de capital

---- para los 1003 (cuotas reprogramadas)
select * from PrestamoCuota
where CodPrestamo = 1890
and CodEstado not in ( 379 , 24)
order by CodPrestamoCuota












'''