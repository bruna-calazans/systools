# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 16:18:33 2020

@author: bcalazans

Automatiza (na medidada do possível) o download de dados do FTP do Governo Brasileiro

Os dados podem ser usados em rotina futura para avaliação de dados socioeconomicos
"""

#%% imports
import pandas as pd
import zipfile as zf
import shutil
import glob, os
import sys
import py7zr
from datetime import datetime
from ftplib import FTP
import itertools

#%% FUNÇÕES AUXILIARES

def move(destination):
    ''' Move arquivos TXT ou CSV para mesmo diretório, deleta o resto'''
    all_files = []
    # para todos os diretórios filhos, lista abspath dos arquivos a mover
    for root, _dirs, files in itertools.islice(os.walk(destination), 1, None):
        for filename in files:
            if (filename[-3:] == 'txt') or (filename[-3:] == 'csv'):
                all_files.append(os.path.join(root, filename))
    # move todos os arquivos listados
    for filename in all_files:
        shutil.move(filename, destination)
    # deleta todos os diretórios
    for root, _dirs, files in itertools.islice(os.walk(destination), 1, None):
        shutil.rmtree(root)
    return
            
            
def unzip_All_Files(zipsDirectory, destinyDirectory):
    ''' Extrai todos os arquivos em uma pasta com o nome do zip de origem'''
    files = os.listdir(zipsDirectory)
    for file in files:
        if(file.endswith('.zip') or file.endswith('.7z')):
            print('Extraindo ' + file)
            unzip_file(os.path.join(zipsDirectory, file), 
                       os.path.join(destinyDirectory, file[:-4]))
    return        
        
    
def unzip_file(zipFileN, destinyDirectory):
    '''Unzipa arquivo no arquivo de destino. Avisa quando erro acontece'''
    try:
        with zf.ZipFile(zipFileN, 'r') as zip_ref:
            zip_ref.extractall(destinyDirectory)
# =============================================================================
#             # extracts all files AND fllatens hierarquy
#             for zip_info in zip_ref.infolist():
#                 if zip_info.filename[-1] == '/':
#                     continue
#                 zip_info.filename = os.path.basename(zip_info.filename)
#                 zip_ref.extract(zip_info, my_dir)            
# 
# =============================================================================

    except:
        try:
            #print("Ocorreu uma exceção ao extrair com a biblioteca Python ZipFile.")
            #print("Tentando extrair usando py7zr \n")
            archive = py7zr.SevenZipFile(zipFileN, mode='r')
            archive.extractall(path=destinyDirectory)
            archive.close()
        except:
            #print('Arquivo corrompido, em formato desconhecido ou com tipo de compressão não permitida, não foi possivel extrair o arquivo: ' + zipFileN + '\n')
            print('\t\t\tERRO! Extraia manualmente SOMENTE ARQUIVO DE TEXTO para a pasta\n\t\t\t' + destinyDirectory)

    return


def get_rais_zips(url, path, save_path):
    print("Executando RAIS")
    print()
    ftp =  FTP(url)
    ftp.login()
    #Endereço do servidor FTP. Não incluir o protocolo, senão não funciona!
    mainPath = path
    ftp.cwd(mainPath)
    #Listando as pastas para acompanhamento:
    print('Listando as pastas do FTP:')
    listFolders = ftp.nlst()
    print (listFolders)
    print('Entrando nas pastas e listando os arquivos:')
    rais_years = list(range(2003,2019)) #2003 a 2018
    for folder in listFolders:
        if(folder.isdigit() and int(folder) in rais_years):
            ftp.cwd(mainPath + '/' + folder)
            listSubFolders = ftp.nlst()
            for i in listSubFolders:
                if('estb' in i.lower() or 'estab' in i.lower() ):
#                     baixe
                    # Inicia o download:
                    filename = i 
                    print('Baixando o arquivo: '+filename)
                    with  open(os.path.join(save_path, filename), 'wb') as file:
                        ftp.retrbinary('RETR ' + filename, file.write)
                    os.rename(os.path.join(save_path, filename),
                              os.path.join(save_path, 'RAIS_'+dict_UF['UF']+folder+'.zip'))

        ftp.cwd(mainPath)
    #unzip_All_Files(save_path, save_path)
    
    
def get_censo_zips(url, path, save_path, **dict_UF):
    print("Executando CENSO")
    ftp =  FTP(url)
    ftp.login()

    #Endereço do servidor FTP. Não incluir o protocolo, senão não funciona!
    mainPath = path
    ftp.cwd(mainPath)

    #Listando as pastas para acompanhamento:
    print('Listando as pastas do FTP:')
    listFiles = ftp.nlst()
#     del(listFolders[9])
    print (listFiles)
    print('Entrando nas pastas e listando os arquivos:')
    for files in listFiles:
        if(files[:2] == dict_UF["UF"]):
            filename = files
            print('Baixando o arquivo: '+filename)
            with  open(os.path.join(save_path, filename), 'wb') as file:
                ftp.retrbinary('RETR ' + filename, file.write)
            os.rename(os.path.join(save_path, filename),
                      os.path.join(save_path, 'POPibge2010_'+dict_UF['UF']+'.zip'))
#         ftp.cwd(mainPath)
    #unzip_All_Files(save_path, save_path)
    #moveArchive(getExcelDirctory(save_path), local_path["censo_excel"])
    return
    
def get_cnefe_zips(url, path, save_path, **dict_UF):
    print("Executando CNEFE")
    ftp =  FTP(url)
    ftp.login()

    #Endereço do servidor FTP. Não incluir o protocolo, senão não funciona!
    mainPath = path
    ftp.cwd(mainPath)

    #Listando as pastas para acompanhamento:
    print('Listando as pastas do FTP:')
    listFolders = ftp.nlst()
    del(listFolders[9])
    print (listFolders)
    print('Entrando nas pastas e listando os arquivos:')
    for folder in listFolders:
        activePath = folder
        if (dict_UF is not None) and (activePath in dict_UF.values()):
            ftp.cwd(activePath)
            print('Pasta Atual'+activePath+' :')
            listFiles = ftp.nlst()
    #         print(listFiles)
            # Inicia o download:
            filename = listFiles[0]
            print('Baixando o arquivo: '+filename)
            with open(os.path.join(save_path, filename), 'wb') as file:
                ftp.retrbinary('RETR ' + filename, file.write)
            os.rename(os.path.join(save_path, filename),
                      os.path.join(save_path, 'CNEFE_'+dict_UF['UF']+'.zip'))
        ftp.cwd(mainPath)
    return
    #unzip_All_Files(save_path, save_path)
    
    
def get_pib_zips(url, path, save_path):
    print("Executando PIB")
    ftp =  FTP(url)
    ftp.login()

    #Endereço do servidor FTP. Não incluir o protocolo, senão não funciona!
    mainPath = path
    #print(mainPath)
    ftp.cwd(mainPath)
    #print('Pasta Atual'+mainPath+' :')
    listFiles = ftp.nlst()
    # Inicia o download:
    local_filename = os.path.join(save_path, "base_de_dados_2010_2017_txt.zip")
    filename = "base_de_dados_2010_2017_txt.zip"
    print('Baixando o arquivo: '+filename)
    with open(local_filename, 'wb') as file:
        ftp.retrbinary('RETR ' + filename, file.write)
    #unzip_All_Files(save_path, save_path)

#%% PARAMETERS
save_path = 'C:\\Users\\bcalazans\\Desktop\\getSocioeconomicsData\\data'

url ={
    "ftp_ibge": "ftp.ibge.gov.br",
    "ftp_microdados": "ftp.mtps.gov.br",
    "censo": "/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/",
    "cnefe": "/Censos/Censo_Demografico_2010/Cadastro_Nacional_de_Enderecos_Fins_Estatisticos/",
#     "pib": "/Pib_Municipios/2017/base/base_de_dados_2010_2017_txt.zip",
    "pib": "/Pib_Municipios/2017/base/",
    "rais": "/pdet/microdados/RAIS/",
    
    # TODO - trazer num vagas por setor censitario
    "ftp_inep" : "ftp.inep.gov.br",
    "microdados_edu_basica":"\\microdado\\microdados_educacao_basica_2018.zip\\microdados_ed_basica_2018\\DADOS\\TURMAS.zip\\TURMAS.CSV",
    "microdados_edu_superior":""
    
}

'''
   "vagas_educa":"\\microdado\\microdados_educacao_basica_2018.zip\\microdados_ed_basica_2018\\DADOS"
    ESCOLAS.zip//ESCOLAS.CSV 
        CO_DISTRITO, QT_FUNCIONARIOS (sum)
    MATRICULA_CO.zip//MATRICULA_CO.CSV  
        CO_DISTRITO, ID_ALUNO (count)
    etc... _NORDESTE _NORTE _SUL _SUDESTE
    TURMAS.zip/TURMAS.CSV
        CO_DISTRITO, QT_MATRICULAS (sum)
'''

write_mode = "w+"
dict_UF = {"UF": "RS", "code":43}
# https://atendimento.tecnospeed.com.br/hc/pt-br/articles/360021494734-Tabela-de-C%C3%B3digo-de-UF-do-IBGE

#%% begin   

# Rodar as funções necessárias para cada projeto
# CNEFE: dados de número de estabelecimento por setor censitário (SC)
# CENSO: dados de população do censo 2010 por IDADE e RENDA NOMINAL por SC
# PIB:   dados de PIB e PIB per capta por município
# RAIS:  dados de empregos formais por municipio 2013 a 2018

# dados municipais Brasil
get_pib_zips(url["ftp_ibge"], url["pib"], save_path)
get_rais_zips(url["ftp_microdados"], url["rais"], save_path) 

# dados por UF
dict_UF = {"UF": "RS", "code":43}
get_cnefe_zips(url["ftp_ibge"], url["cnefe"], save_path, **dict_UF)
get_censo_zips(url["ftp_ibge"], url["censo"], save_path, **dict_UF)

dict_UF = {"UF": "MG", "code":31}
get_cnefe_zips(url["ftp_ibge"], url["cnefe"], save_path, **dict_UF)
get_censo_zips(url["ftp_ibge"], url["censo"], save_path, **dict_UF)
 
dict_UF = {"UF": "PE", "code":26}
get_cnefe_zips(url["ftp_ibge"], url["cnefe"], save_path, **dict_UF)
get_censo_zips(url["ftp_ibge"], url["censo"], save_path, **dict_UF)
#%% UNZIP MANUAL
# Selecione todos os zips baixados e unzip manualmente
# é mais seguro do que rodar o código que falha em alguns PCs

# TODO -- extrair todos os arquivos para um mesmo diretório
# unzip_All_Files(save_path, save_path)
#%% move todos os arquivos de interesse pro dir raiz
move(save_path)
#%%

