# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 17:34:45 2024

@author: Joseph Montoya
"""

# =============================================================================
# INSERTAR DATOS EN SQL SERVER, DESDE PYTHON
# =============================================================================
import pyodbc
import pandas as pd

DATA_FRAME_DE_EJEMPLO = pd.DataFrame()
df  = DATA_FRAME_DE_EJEMPLO.copy()


cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
cursor = cnxn.cursor()
# Inserta el DataFrame en SQL Server
# PARA QUE EL CÓDIGO FUNCIONES, PRIMERO DEBES CREAR UNA TABLA EN EL SQL SERVER CON:

# CREATE TABLE [HumanResources].[DepartmentTest](
# [DepartmentID] INT            NOT NULL,
# [Name]         VARCHAR(255)   NOT NULL,
# [ALTURA]    FLOAT          NOT NULL
# )


for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO saldos_diarios.dbo.[2024_01] 
        ([Nro_Fincore], 
         [Saldodecolocacionescreditosdirectos24], 
         [FechadeDesembolso21], 
         [PRODUCTO TXT], 
         [PLANILLA_CONSOLIDADA], 
         [originador], 
         [administrador], 
         [FECHA_DÍA])
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    row['Nro_Fincore'],
    row['Saldodecolocacionescreditosdirectos24'],
    row['FechadeDesembolso21'],
    row['PRODUCTO TXT'],
    row['PLANILLA_CONSOLIDADA'],
    row['originador'],
    row['administrador'],
    row['FECHA_DÍA']
    )

cnxn.commit()
cursor.close()


