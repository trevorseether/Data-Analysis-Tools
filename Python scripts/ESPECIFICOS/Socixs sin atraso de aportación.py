# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 09:48:59 2024

@author: Joseph Montoya
"""

import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\padron socios diciembre')

padron = 'Rpt_PadronSocios Diciembre-23 Ampliado - incl inhabiles.xlsx'

anexo  = 'Rpt_DeudoresSBS Anexo06 - Diciembre 2023 - campos ampliados version final v5.xlsx'

#%%
padron = pd.read_excel(io       = padron,
                       skiprows = 1,
                       dtype    = {'CodSoc': str})

anexo_06 = pd.read_excel(io       = anexo, 
                         skiprows = 2,
                         dtype    = {'Código Socio 7/': str})

#%%
morosos = anexo_06[anexo_06['Dias de Mora 33/'] > 45]
morosos = morosos[['Código Socio 7/',
                   'Dias de Mora 33/']]

#%%
padron['CodSoc']            = padron['CodSoc'].str.strip()
anexo_06['Código Socio 7/'] = anexo_06['Código Socio 7/'].str.strip()

#%%
padron_habiles = padron[padron['Condicion'] == 'HABIL']

#%% merge
buenos = padron_habiles[~padron_habiles['CodSoc'].isin(morosos['Código Socio 7/'])]


hombres_buenos = buenos[buenos['Sexo'] == 'M']
mujeres_buenas = buenos[buenos['Sexo'] == 'F']

