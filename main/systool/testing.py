# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 10:16:35 2023

@author: adefarias
"""


import sys
import os


#sys.path.append(os.path.abspath(os.path.join('..')))

import data

import pandas as pd

#Abrir um arquivo usando open_file

shp = data.open_file(r'C:\Users\adefarias\OneDrive - SystraGroup\SYSTRA - ARTHUR FARIAS\QGIS\PONTOS_DE_ONIBUS\PONTOS_DE_ONIBUS.shp')

#renomear a primeira coluna para ter 20 characters

shp = shp.rename(columns={'Bairro': 'Bairro_Alagoano'})

#salvar utilizando save_file

data.save_file(shp, r'C:\Users\adefarias\OneDrive - SystraGroup\SYSTRA - ARTHUR FARIAS\QGIS\NOVO_PONTOS_DE_ONIBUS', name='shp_file', ext='shp')

#abrir novamente o arquivo salvo
shp = data.open_file(r'C:\Users\adefarias\OneDrive - SystraGroup\SYSTRA - ARTHUR FARIAS\QGIS\NOVO_PONTOS_DE_ONIBUS\shp_file.shp')

#Colocar novo nome (Coluna "A")
shp = shp.rename(columns={'Bairro_Alagoano': 'PraiaDaPontaVerde'})

#salvar utilizando save_file
data.save_file(shp, r'C:\Users\adefarias\OneDrive - SystraGroup\SYSTRA - ARTHUR FARIAS\QGIS\NOVO_PONTOS_DE_ONIBUS', name='shp_file', ext='shp')
#reload data -> dá um googs hpw to reload module on spyder
