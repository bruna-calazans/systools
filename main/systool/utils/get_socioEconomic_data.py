# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 08:30:04 2020

@author: bcalazans

Organiza dados socioenconomicos baixados do FTP para uso futuro

INPUTS
---
Shapefile do zoneamento da área de interesse para recorte dos dados
Shapefile dos setores censitários para recorte dos dados
Caminho dos dados baixados do FTP (todos em um mesmo lugar, sem subpastas)


OUTPUT
---
Salva um Excel contendo duas ABAS
    SC_UF: Dados desagregados segundo setor censitário
        POPULAÇÃO segregada por grupos etários
        POPULAÇÃO segregada por grupos de remuneração x SM = Salário Mínimo
        NÚMERO DE ESTABELECIMENTOS por tipo 
        NÚMERO DE EMPREGOS estimado por setor censitário
            Distribui os empregos do RAIS (registrado por CEP) com o registro
            dos CEPs do CNEFE e sua associação a um setor censitário
    Muni_UF: Dados desagregados por município e ANO de referência
        PIB
        PIB nominal
        NÚMERO DE EMPREGOS por setor
"""
#%% imports
from zipfile import ZipFile 

import os
import geopandas as gpd
import pandas as pd
import numpy as np
from tqdm import tqdm

#%% functions
def read_cnefe(path, UF_id):
    ''' Lê CNEFE - cda linha é um registro de um estabelecimento '''
    colspecs = [(0,2),(2,7),(7,9),(9,11),(11,15),(15,16),(16,36),(36,66),(66,126),(126,134),(134,141),(141,161),(161,171),(171,191),(191,201),(201,221),(221,231),(231,251),(251,261),(261,281),(281,291),(291,311),(311,321),(321,336),(336,351),(351,411),(411,471),(471,473),(473,513),(513,514),(514,544),(544,547),(547,550),(550,558)]
    df = pd.read_fwf(os.path.join(path, str(UF_id) + '.txt'), colspecs=colspecs, header=None)
    df.columns = ['COD_UF','COD_MUNI','COD_DIST','COD_SUBDIST','COD_SETOR','SITUACAO_SETOR','TIPO_LOGRADOURO','TITULO_LOGRADOURO','NOME_LOGRADOURO','NUM_LOGRADOURO','MODIFICADOR_NUMERO','ELEMENTO_1','VALOR_1','ELEMENTO_2','VALOR_2','ELEMENTO_3','VALOR_3','ELEMENTO_4','VALOR_4','ELEMENTO_5','VALOR_5','ELEMENTO_6','VALOR_6','LAT','LON','LOCALIDADE','NULO','ESPECIE_ENDERECO','IDENTIF_ESTABELECIMENTO','INDICADOR_ENDERECO','IDENTIF_DOM_COLETIVO','NUM_QUADRO','NUM_FACE','CEP']

    # ajusta código do setor censitário
    df.COD_UF = df.COD_UF.map(str).str.zfill(2)
    df.COD_MUNI = df.COD_MUNI.map(str).str.zfill(5)
    df.COD_DIST = df.COD_DIST.map(str).str.zfill(2)
    df.COD_SUBDIST = df.COD_SUBDIST.map(str).str.zfill(2)
    df.COD_SETOR = df.COD_SETOR.map(str).str.zfill(4)
    
    df['COD_SC'] = ( df.COD_UF.map(str) + 
                         df.COD_MUNI.map(str) + 
                         df.COD_DIST.map(str) + 
                         df.COD_SUBDIST.map(str) + 
                         df.COD_SETOR.map(str)
                        )
    return df


def get_estab_cnefe(df, setores2filter):
    #Baseado no campo ESPECIE ENDEREÇO dos endereços com valores de 8 a 12 decidimos fazer as seguintes adaptações 
    #  8 => RURAL => 03
    #  9 => EDUCAÇÃO => 04
    #  10 => SAUDE => 05
    #  11 => OUTROS => 06
    #  12 => IGNORAR => deletar da base
    #Os pontos marcados como 12 não contém qualquer informação, seja da espécia de endereço, ou coordenadas geográficas (LAT,LON). Apesar de possuirem CEP, como representam menos de 2% dos dados, decidiu-se expurgar

    df.ESPECIE_ENDERECO = df.ESPECIE_ENDERECO.replace(8, 3).replace(9,4).replace(10,5).replace(11,6)
    #df.ESPÉCIE_DE_ENDEREÇO.value_counts()
    mask = df.COD_SC.isin(setores2filter)
    info = df[mask].groupby(['COD_SC','ESPECIE_ENDERECO']).size().unstack().fillna(0)

    info = info.drop([12], axis=1)
    # info.drop(index='ESPÉCIE_DE_ENDEREÇO', columns=12)
    info = info.rename(columns={
                                1:'#DOMICILIO_PARTICULAR',
                                2:'#DOMICILIO_COLETIVO',
                                3:'#ESTAB_AGROPECUARIO',
                                4:'#ESTAB_ENSINO',
                                5:'#ESTAB_SAUDE',
                                6:'#ESTAB_OUTROS',
                                7:'#EM_CONSTRUCAO',
                                })
    return info


def get_cols(cols_ibge, lower, upper):
    ''' Retorna o nome das colunas que caem em determinada categoria de idade'''
    mask = (cols_ibge.IDADEemANOS >=lower) & (cols_ibge.IDADEemANOS <= upper)
    return cols_ibge.loc[mask, 'COL_IBGE'].tolist()
    

def get_popByAge(path, UF, setores2filter):
    # dicionário das colunas de interesse do relatório Pessoas13.txt
    cols_ibge = pd.DataFrame({
        'COL_IBGE':	  ['V022','V023','V024','V025','V026','V027','V028','V029','V030','V031','V032','V033','V034','V035','V036','V037','V038','V039','V040','V041','V042','V043','V044','V045','V046','V047','V048','V049','V050','V051','V052','V053','V054','V055','V056','V057','V058','V059','V060','V061','V062','V063','V064','V065','V066','V067','V068','V069','V070','V071','V072','V073','V074','V075','V076','V077','V078','V079','V080','V081','V082','V083','V084','V085','V086','V087','V088','V089','V090','V091','V092','V093','V094','V095','V096','V097','V098','V099','V100','V101','V102','V103','V104','V105','V106','V107','V108','V109','V110','V111','V112','V113','V114','V115','V116','V117','V118','V119','V120','V121','V122','V123','V124','V125','V126','V127','V128','V129','V130','V131','V132','V133','V134'],
        'NOME_IBGE':  ['Pessoas com menos de 1 ano de idade','Pessoas com menos de 1 mês de idade','Pessoas com 1 mês de idade','Pessoas com 2 meses de idade','Pessoas com 3 meses de idade','Pessoas com 4 meses de idade','Pessoas com 5 meses de idade','Pessoas com 6 meses de idade','Pessoas com 7 meses de idade','Pessoas com 8 meses de idade','Pessoas com 9 meses de idade','Pessoas com 10 meses de idade','Pessoas com 11 meses de idade','Pessoas de 1 ano de idade','Pessoas com 2 anos de idade','Pessoas com 3 anos de idade','Pessoas com 4 anos de idade','Pessoas com 5 anos de idade','Pessoas com 6 anos de idade','Pessoas com 7 anos de idade','Pessoas com 8 anos de idade','Pessoas com 9 anos de idade','Pessoas com 10 anos de idade','Pessoas com 11 anos de idade','Pessoas com 12 anos de idade','Pessoas com 13 anos de idade','Pessoas com 14 anos de idade','Pessoas com 15 anos de idade','Pessoas com 16 anos de idade','Pessoas com 17 anos de idade','Pessoas com 18 anos de idade','Pessoas com 19 anos de idade','Pessoas com 20 anos de idade','Pessoas com 21 anos de idade','Pessoas com 22 anos de idade','Pessoas com 23 anos de idade','Pessoas com 24 anos de idade','Pessoas com 25 anos de idade','Pessoas com 26 anos de idade','Pessoas com 27 anos de idade','Pessoas com 28 anos de idade','Pessoas com 29 anos de idade','Pessoas com 30 anos de idade','Pessoas com 31 anos de idade','Pessoas com 32 anos de idade','Pessoas com 33 anos de idade','Pessoas com 34 anos de idade','Pessoas com 35 anos de idade','Pessoas com 36 anos de idade','Pessoas com 37 anos de idade','Pessoas com 38 anos de idade','Pessoas com 39 anos de idade','Pessoas com 40 anos de idade','Pessoas com 41 anos de idade','Pessoas com 42 anos de idade','Pessoas com 43 anos de idade','Pessoas com 44 anos de idade','Pessoas com 45 anos de idade','Pessoas com 46 anos de idade','Pessoas com 47 anos de idade','Pessoas com 48 anos de idade','Pessoas com 49 anos de idade','Pessoas com 50 anos de idade','Pessoas com 51 anos de idade','Pessoas com 52 anos de idade','Pessoas com 53 anos de idade','Pessoas com 54 anos de idade','Pessoas com 55 anos de idade','Pessoas com 56 anos de idade','Pessoas com 57 anos de idade','Pessoas com 58 anos de idade','Pessoas com 59 anos de idade','Pessoas com 60 anos de idade','Pessoas com 61 anos de idade','Pessoas com 62 anos de idade','Pessoas com 63 anos de idade','Pessoas com 64 anos de idade','Pessoas com 65 anos de idade','Pessoas com 66 anos de idade','Pessoas com 67 anos de idade','Pessoas com 68 anos de idade','Pessoas com 69 anos de idade','Pessoas com 70 anos de idade','Pessoas com 71 anos de idade','Pessoas com 72 anos de idade','Pessoas com 73 anos de idade','Pessoas com 74 anos de idade','Pessoas com 75 anos de idade','Pessoas com 76 anos de idade','Pessoas com 77 anos de idade','Pessoas com 78 anos de idade','Pessoas com 79 anos de idade','Pessoas com 80 anos de idade','Pessoas com 81 anos de idade','Pessoas com 82 anos de idade','Pessoas com 83 anos de idade','Pessoas com 84 anos de idade','Pessoas com 85 anos de idade','Pessoas com 86 anos de idade','Pessoas com 87 anos de idade','Pessoas com 88 anos de idade','Pessoas com 89 anos de idade','Pessoas com 90 anos de idade','Pessoas com 91 anos de idade','Pessoas com 92 anos de idade','Pessoas com 93 anos de idade','Pessoas com 94 anos de idade','Pessoas com 95 anos de idade','Pessoas com 96 anos de idade','Pessoas com 97 anos de idade','Pessoas com 98 anos de idade','Pessoas com 99 anos de idade','Pessoas com 100 anos ou mais de idade'],
        'IDADEemANOS':[0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]
        })
    # dicionário personalizado
    cols_agreg = {
        'POP_00a06_anos': get_cols(cols_ibge, 0, 6),
        'POP_07a14_anos': get_cols(cols_ibge, 7, 14),
        'POP_15a25_anos': get_cols(cols_ibge, 15, 25),
        'POP_26a65_anos': get_cols(cols_ibge, 26, 65),
        'POP_66+_anos': get_cols(cols_ibge, 66, 100),
         }
    
    # lê tabela do IBGE
    df = pd.read_csv(os.path.join(path, "Pessoa13_"+UF+".csv"), sep=';')
    df = df.fillna(0)
    df = df.apply(pd.to_numeric, errors='coerce') 
    
    # ajustes 
    df.Cod_setor = df.Cod_setor.map(str)
    df = df.set_index('Cod_setor')
    mask = df.index.isin(setores2filter)
    info = pd.DataFrame(index=df.loc[mask].index)
    
    # pra cda grupo criado, soma as colunas correspondentes
    for col in cols_agreg.keys():
        info[col] = df.loc[mask, cols_agreg[col]].sum(axis=1)
    
    return info


def get_popByMoney(path, UF, setores2filter):
    cols_ibge = {
        'V001': 'POP_0a0.5_SM',
        'V002':'POP_0.5a1_SM',
        'V003':'POP_1a2_SM',
        'V004':'POP_2a3_SM',
        'V005':'POP_3a5_SM',
        'V006':'POP_5a10_SM',
        'V007':'POP_10a15_SM',
        'V008':'POP_15a20_SM',
        'V009':'POP_20+_SM',
        'V010':'POP_semSM'}
    
    # lê tabela do IBGE
    df = pd.read_csv(os.path.join(path, "PessoaRenda_"+UF+".csv"), sep=';')
    df = df.fillna(0)
    df = df.apply(pd.to_numeric, errors='coerce') 
    
    # filtra info  
    df.Cod_setor = df.Cod_setor.map(str)
    df = df.set_index('Cod_setor')
    mask = df.index.isin(setores2filter)
    info = df.loc[mask, cols_ibge.keys()]
    info = info.rename(columns=cols_ibge)   
    return info


def get_codes2filter(path_files, plot=False):
    # read shapefile to get SC list of interest
    setores = gpd.read_file(path_files['setores'])
    zns = gpd.read_file(path_files['zoneamento'])
    setores = setores.to_crs(zns.crs)
    
    if plot:
        ax=setores.plot(facecolor='none', edgecolor='lightgray')
        ax=zns.plot(ax=ax, color='red')
    
    print('Regioes Metropolitanas disponíveis',setores.NM_MESO.unique())
    print()
    # pega dados diretamente do layer oficial do IBGE
    if 'NM_MESO' in setores.columns:
        print('Pegando setores da *{}* segundo IBGE'.format(path_files['NM_MESO']))
        mask = setores.NM_MESO == path_files['NM_MESO']
        setores2filter = setores[mask].CD_GEOCODI.unique()
        municip2filter = setores[mask].CD_GEOCODM.unique()
    else:
        print('Usa tag geográfico do geopandas para achar setores no layer de Zonas fornecido')
        setores_zns = gpd.overlay(setores, zns[['ID','geometry']], how='intersection')
        
         # salva variáveis com os códigos da zona de interesse
        setores2filter = setores_zns.CD_GEOCODI.unique()
        municip2filter = setores_zns.CD_GEOCODM.unique()
        #subdist2filter = setores_RM.CD_GEOCODS.unique()
    
    print('Setores filtrados:    {:,}'.format(len(setores2filter))) 
    print('Municipios filtrados: {:,}'.format(len(municip2filter))) 
    return setores2filter, municip2filter, setores[setores.CD_GEOCODI.isin(setores2filter)]


def build_cep_data_from_cnefe(df_cnefe):
    ''' Constrói uma base de cadastro de CEP e de LAT,LONs '''
    # idealmente deveríams ter um cadastro oficial de endereços com Latlon do BRASIL
    
    # temos um cadastro de endereços de BH baixado de:
    # http://bhmap.pbh.gov.br/v2/mapa/
    # le cadastro pronto de BH
    from shapely import wkt
    PATH = 'C:\\Users\\bcalazans\\SystraGroup\\BNDES-CBTU-Produção - General\\01.MG\\02.Produção\\Planilhas\\'
    cep = pd.read_csv(PATH + 'cadastro_CEP.csv', engine='python')
    cep['geometry'] = cep['GEOMETRIA'].apply(wkt.loads)
    cep = gpd.GeoDataFrame(cep) 
    # código EPSG para UTM 23S
    #cep.set_crs(epsg=32723, inplace=True)  # fails
    #cep.crs = 'EPSG:32723'                 # fails
    cep.crs =  {'init' :'epsg:32723'}       # works
    cep = cep.loc[cep.CEP.notnull(), ['CEP','geometry']]
    cep = cep.to_crs({'init' :'epsg:4326'})
    
    # cria cadastro com base no CNEFE
    df = df_cnefe[['COD_SC', 'CEP','LAT', 'LON']]
    mask = df.LAT.isnull() | df.LON.isnull()
    print('{:.2%} {:}'.format(
        mask.sum()/len(df), 'registros com LAT LON nulos, serão deletados'))
    df = df.loc[~mask]
    
    # transforma lat/lon em número
    def dms_to_dd(degree, minutes, seconds, NSLO):
        decimals = float(degree) + float(minutes)/60 + float(seconds)/3600
        signal = -1 if NSLO in 'SO' else 1
        return decimals * signal
    
    df['LAT'] = df.apply(lambda row: dms_to_dd(*row['LAT'].split(' ')), axis=1)
    df['LON'] = df.apply(lambda row: dms_to_dd(*row['LON'].split(' ')), axis=1)

    # remove duplicatas
    df = df.drop_duplicates()
    # transforma em shape
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LON, df.LAT))
    df.crs =  {'init' :'epsg:4326'}       # works
    
    # agrega bases de dados e remove duplicatas
    df = df.append(cep,sort=True)
    df = df[['CEP','geometry']]
    return df.drop_duplicates()


def get_jobs_from_rais(path_data, file, municip2filter):
    ''' Lê RAIS mais novo e agrega trabalhos
    RETURNS: trabalhos agg por CEP, trabalhos agg por MUNICIPIO'''
    rais = pd.read_csv(os.path.join(path_data, file), engine='python',sep=';')
    
    # Add cod de município do IBGE, o RAIS usa um dígito a menos
    rais = rais.merge(pd.DataFrame({
        'Município':(pd.Series(municip2filter).map(str).str[:-1]).astype(int).tolist(),
        'COD_MUNI':municip2filter}))
    
    # cda linha do RAIS é um estabelecimento, agregar por CEP o #jobs
    # seleciona apenas estabelecimentos funcionando
    mask = rais['Ind Atividade Ano'] == 1 
    rais = rais.loc[mask]
    #seleciona apenas municipios de interesse
    mask = rais['COD_MUNI'].isin(municip2filter)
    rais = rais.loc[mask]
    
    # agrega por CEP para poder jogar na tabela por Setor Censitário
    raisByCep = rais.groupby(['CEP Estab'])['Qtd Vínculos Ativos'].sum().rename('NUM_JOBS')
    # TODO tratar CEP = 9999999 = NaN
    
    # agrega por muni pra ter os totais
    raisByMuni = rais.groupby(['COD_MUNI'])['Qtd Vínculos Ativos'].sum().rename('NUM_JOBS').reset_index()
    return raisByCep, raisByMuni


def read_pib(path, municip2filter):
    colspecs = [(0,4),(5,6),(7,19),(20,22),(23,25),(26,45),(46,53),(54,94),(95,205),(206,210),(211,251),(252,257),(258,298),(299,305),(306,372),(373,383),(384,388),(389,424),(425,435),(436,443),(444,511),(512,599),(600,607),(608,694),(695,727),(728,746),(747,751),(752,843),(844,887),(888,892),(893,897),(898,902),(903,921),(922,940),(941,959),(960,978),(979,997),(998,1016),(1017,1035),(1036,1054),(1055,1149),(1150,1244),(1245,1339)]
    df = pd.read_fwf(os.path.join(path, 'PIB dos Municípios - base de dados 2010-2017.txt'), colspecs=colspecs, header=None)
    df.columns = ['ANO','Código da Grande Região','Nome da Grande Região','Código da Unidade da Federação','Sigla da Unidade da Federação','Nome da Unidade da Federação','COD_MUNI','MUNICIPIO','Região Metropolitana','Código da Mesorregião','Nome da Mesorregião','Código da Microrregião','Nome da Microrregião','Código da Região Geográfica Imediata','Nome da Região Geográfica Imediata','Município da Região Geográfica Imediata','Código da Região Geográfica Intermediária','Nome da Região Geográfica Intermediária','Município da Região Geográfica Intermediária','Código Concentração Urbana','Nome Concentração Urbana','Tipo Concentração Urbana','Código Arranjo Populacional','Nome Arranjo Populacional','Hierarquia Urbana','Hierarquia Urbana (principais categorias)','Código da Região Rural','Nome da Região Rural','Região rural (segundo classificação do núcleo)','Amazônia Legal','Semiárido','Cidade-Região de São Paulo','Valor adicionado bruto da Agropecuária, a preços correntes','Valor adicionado bruto da Indústria, a preços correntes','Valor adicionado bruto dos Serviços, a preços correntes – exceto Administração, defesa, educação e saúde públicas e seguridade social','Valor adicionado bruto da Administração, defesa, educação e saúde públicas e seguridade social, a preços correntes','Valor adicionado bruto total, a preços correntes','Impostos, líquidos de subsídios, sobre produtos, a preços correntes','PIB_BRUTO','PIB_PER_CAPTA','Atividade econômica com maior valor adicionado bruto','Atividade econômica com segundo maior valor adicionado bruto','Atividade econômica com terceiro maior valor adicionado bruto']
    
    # filtra colunas de interesse
    mask = df['COD_MUNI'].isin(municip2filter)
    df = df.loc[mask, ['ANO','COD_MUNI','MUNICIPIO','PIB_BRUTO','PIB_PER_CAPTA']]
    return df


def read_rais_all_years(path, municip2filter):
    ''' Lê os dados dos RAIS disponíveis (2005 a 2018)
    RETURNS: número de empregos formais por município'''
    rais_files = pd.DataFrame({
        'FILE':["RAIS_ESTAB_PUB.txt",# 2018
                #2017 a 2007
                "ESTB2017.txt","ESTB2016.txt","ESTB2015.txt","ESTB2014.txt",'ESTB2013.txt','Estb2012.txt','ESTB2011.txt','ESTB2010.txt', "ESTB2009.txt",'ESTB2008.txt', "ESTB2007.txt",
                "consulta60747774.txt", # 2006
                "consulta8599625.txt", # 2005
                "consulta44651176.txt", #2004
                "consulta66624895.txt"], #2003
        'ANO':list(range(2018,2002,-1))
        })
    # funciona por hora apenas para RAIS >= 2005
    rais_files = rais_files[rais_files.ANO >= 2005]
    
    raisByMuni = pd.DataFrame(columns=['COD_MUNI', 'NUM_JOBS','ANO'])
    for i, row in tqdm(rais_files.iterrows(), desc='Lendo todos os RAIS'): 
        file = row['FILE']
        year = row['ANO']
        rais = pd.read_csv(os.path.join(path,file), engine='python',sep=';')
        #print(file, year)
        rais = rais.rename(columns={'ESTOQUE':'Qtd Vínculos Ativos'})
    
    
        # Add cod de município do IBGE, o RAIS usa um dígito a menos
        rais = rais.merge(pd.DataFrame({
            'Município':(pd.Series(municip2filter).map(str).str[:-1]).astype(int).tolist(),
            'COD_MUNI':municip2filter}))
        
        # cda linha do RAIS é um estabelecimento, agregar por CEP o #jobs
        # seleciona apenas estabelecimentos funcionando
        mask = rais['Ind Atividade Ano'] == 1 
        rais = rais.loc[mask]
        #seleciona apenas municipios de interesse
        mask = rais['COD_MUNI'].isin(municip2filter)
        rais = rais.loc[mask]
    
        # agrega por muni pra ter os totais
        raisByMuni = raisByMuni.append(
            rais.groupby(['COD_MUNI'])['Qtd Vínculos Ativos'].sum().rename('NUM_JOBS').reset_index(),
            sort=True, ignore_index=True)
        raisByMuni['ANO'] = raisByMuni['ANO'].fillna(year)
    
    # por via das dúvidas...
    raisByMuni.ANO = raisByMuni.ANO.astype(int)
    raisByMuni.COD_MUNI = raisByMuni.COD_MUNI.astype(int)
    return raisByMuni


#TODO
def get_vagas_educ_by_SC(df_sc):
    '''
    Pega número de vagas do ensino básico e superior do censo de educação e 
    redistribui nos setores censitários com base nos subdistritos e municipios
    
    Resgatar a coluna do CNAE do RAIS no get_rais e separar os estabelecimentos
    de ensino. Depois, distribui usando a mesma metodologia do get_jobs,
    porém, ao invés de usar #estab, usa #estab_ensino
    
    Verificar se tem como obter #estab_ensino superior/médio/fundamental

    rais['CNAE 2.0 Subclasse']
        8511200:Educação Infantil - Creche
        8512100:Educação Infantil - Pré-Escola
        8531700:Educação Superior - Graduação
        8532500:Educação Superior - Graduação e Pós-Graduação
        8533300:Educação Superior - Pós-Graduação e Extensão
        8541400:Educação Profissional de Nível Técnico
        8542200:Educação Profissional de Nível Tecnológico

    Returns
    -------
    None.
    '''
    #--- ensino básico
    # le arquivo do relatorio de vagas nacional
    path_file = 'C:\\Users\\bcalazans\\Desktop\\getSocioeconomicsData\\data\\TURMAS.CSV'
    
    df = pd.read_csv(path_file, sep='|', encoding='latin1')
    df = (df.groupby('CO_DISTRITO').QT_MATRICULAS.sum().rename('QT_VAGAS_EDUC_BASbyCO_DIST')).reset_index()
    
    # usa codigo do distrito como chave para parear
    df_sc['CO_DISTRITO'] = df_sc.index.map(str).str[:9].astype('int')
    df_sc = df_sc.reset_index().merge(df, how='left').set_index('index')
    
    df_sc['#ESTAB_ENSINObyCOD_DIST'] = df_sc.groupby('CO_DISTRITO')['#ESTAB_ENSINO'].transform(sum)
    df_sc['NUM_EDUC_BAS'] = (df_sc['#ESTAB_ENSINO']/df_sc['#ESTAB_ENSINObyCOD_DIST'])*df_sc['QT_VAGAS_EDUC_BASbyCO_DIST']
    
    #--- ensino superior
    # le arquivo de vagas ensino superior
    zip_path = 'C:\\Users\\bcalazans\\Desktop\\getSocioeconomicsData\\microdados_educacao_superior_2019.zip'
    with ZipFile(zip_path, 'r') as zfile:
        #print(zfile.namelist())
        #with zfile.open("Microdados_Educacao_Superior_2019/dados/SUP_ALUNO_2019.CSV") as f:
        #  df1 = pd.read_csv(f,sep='|',encoding='latin1')
        with zfile.open("Microdados_Educacao_Superior_2019/dados/SUP_CURSO_2019.CSV") as f:
          df2 = pd.read_csv(f,sep='|',encoding='latin1')
          
    df2 = df2[['CO_MUNICIPIO','QT_INSC_VAGA_REMAN_MATUTINO','QT_INSC_VAGA_NOVA_MATUTINO']].set_index('CO_MUNICIPIO').sum(axis=1).rename('QT_VAGAS_EDUC_SUPbyCO_MUNI').rename_axis('COD_MUNI').reset_index()
    df2 = df2[df2.COD_MUNI.notnull()]
    df2['COD_MUNI'] = df2.COD_MUNI.astype(int).astype(str)
    df2 = df2.groupby('COD_MUNI').QT_VAGAS_EDUC_SUPbyCO_MUNI.sum().reset_index()
     # usa codigo do municipio como chave para parear
    df_sc = df_sc.reset_index().merge(df2, how='left').set_index('index')
    
    df_sc['#ESTAB_ENSINObyCOD_MUNI'] = df_sc.groupby('COD_MUNI')['#ESTAB_ENSINO'].transform(sum)
    df_sc['NUM_EDUC_SUP'] = (df_sc['#ESTAB_ENSINO']/df_sc['#ESTAB_ENSINObyCOD_MUNI'])*df_sc['QT_VAGAS_EDUC_SUPbyCO_MUNI']
      
    return df_sc
    
 

def get_jobs_by_SC(cep, setores, ans, raisByCep, raisByMuni):
    ''' Distribui informação de empregos do RAIS nos setores censitários
    1) usa o CEP para tentar distribuir proporcionalmente os empregos
    2) os empregos que não informaram CEP no RAIS são distribuidos usando o
    número de estabelecimento do CNEFE '''
    # associa CEPs aos SCs usando 'geometry'
    cep = cep.to_crs(setores.crs)    
    tag = gpd.sjoin(cep, setores, how='inner', op='within') 
    #tag = gpd.sjoin(cep, setores[setores.CD_GEOCODM.isin(['3135704'])], how='inner', op='within')
    tag['countCEP'] = tag.groupby('CEP').CEP.transform('count')
    tag = tag[['CD_GEOCODI', 'CD_GEOCODM','CEP','countCEP']]
    # associa empregos do RAIS aos setores com base na distribuição do CEP
    tag = tag.merge(raisByCep, left_on='CEP', right_index=True, how='inner')
    tag['NUM_JOBS'] = round(tag['NUM_JOBS'].div(tag.countCEP, axis=0),0)
    print('{:9,} endereçoes georeferenciados na zona de interesse'.format(len(tag)))
    # agrega por SC e Muni para o resultado
    tag = tag.groupby(['CD_GEOCODI','CD_GEOCODM']).NUM_JOBS.sum().reset_index()
    tag = tag.rename(columns=({'CD_GEOCODI':'COD_SC',
                               'CD_GEOCODM':'COD_MUNI',
                               'NUM_JOBS':'NUM_JOBSbyCEP'}))
    
    # TODO aqui o tag tem q ganhar todos os SC  pra poder fazer a conta
    # dos jobs a distribuir por muni
    tag = pd.DataFrame(
            # soma estabelecimentos ,ignora em construção
            ans[[c for c in ans.columns if 'ESTAB' in c]].sum(axis=1).rename('TOT_ESTAB') 
            ).merge(
            tag[['NUM_JOBSbyCEP','COD_SC']].set_index('COD_SC'), 
            left_index=True, right_index=True, how='left').fillna(0)
    # pega COD_MUNI pois ele não está completo em tag
    tag['COD_MUNI'] = tag.index.str[:7]
    
    # o total aqui não vai bater pois não temos cadastro de todos os ceps...
    # pega a soma por municipio e diminui do total real
    tag['TOT_MUNIbyCEP'] = tag.groupby('COD_MUNI').NUM_JOBSbyCEP.transform('sum')
    tag = tag.reset_index().merge(raisByMuni, on='COD_MUNI').set_index('index')
   
    # NUM_JOBSbyCEP: número de empregos distribuidos no SC usando CEP
    # TOT_MUNIbyCEP: número de empregos no município usando o método do CEP
    # NUM_JOBS: número de empregos REAL que deveria considerar naqle município
    # JOBSaDistribuir no municipio
    tag['JOBSaDistribuir'] = tag.NUM_JOBS - tag.TOT_MUNIbyCEP
    
    # (!) se JOBSaDistribuir é negativo (não entendi ainda porque isso acontece)
    # substitui o JOBSaDistribuir pelo total de JOBS e vai usar só estab
    mask = tag['JOBSaDistribuir'] < 0
    tag.loc[mask,'JOBSaDistribuir']  = tag.NUM_JOBS
    tag.loc[mask, 'NUM_JOBSbyCEP'] = 0
    
    # (!) se JOBSaDistribuir é positivo
    # divide restante dos empregos com base no número de estabelecimentos do CNEFE
    
    # distribui os empregos faltantes com base #estabelecimento CNEFE 2010
    tag['TOT_ESTABbyMUNI'] = tag.groupby('COD_MUNI').TOT_ESTAB.transform(sum)
    tag['NUM_JOBSbyMUNI'] = np.where(tag.TOT_ESTAB==0, 0, 
                                     round(
                                    tag.JOBSaDistribuir / tag.TOT_ESTABbyMUNI * tag.TOT_ESTAB,
                                     0))
    
    # num jobs = by CEP + _aprox
    tag['NUM_JOBS'] = tag.NUM_JOBSbyCEP + tag.NUM_JOBSbyMUNI
    
    # report tot
    print('{:9,.0f} empregos distribuidos por SC'.format( tag.NUM_JOBS.sum()))
    print('{:9,.0f} empregos no RAIS'.format(raisByMuni.NUM_JOBS.sum()))
    print('{:9,.0f} empregos de diferença --> {:.1%}'.format(
        tag.NUM_JOBS.sum()-raisByMuni.NUM_JOBS.sum(),
        (tag.NUM_JOBS.sum()-raisByMuni.NUM_JOBS.sum())/raisByMuni.NUM_JOBS.sum()))
    return tag


raise Exception ('Begin!')
#%% PARAMETERS
#https://atendimento.tecnospeed.com.br/hc/pt-br/articles/360021494734-Tabela-de-C%C3%B3digo-de-UF-do-IBGE
# caminho onde todos os arquivos foram salvos do get_ftp_data()
path_data = 'C:\\Users\\bcalazans\\Desktop\\getSocioeconomicsData\\data'

#%% BH  
dict_UF = {"UF": "MG", "code":31}  
path_shp = 'C:\\Users\\bcalazans\\SystraGroup\\BNDES-CBTU-Produção - General\\01.MG\\02.Produção\\Arquivos Geográficos\\SHP\\'
path_files = {
    'NM_MESO':'METROPOLITANA DE BELO HORIZONTE',
    'setores': path_shp + '31SEE250GC_SIR.shp',
    'zoneamento':path_shp + 'Zonas_115.shp'}

#%% RS
dict_UF = {"UF": "RS", "code":43}
path_shp = 'C:\\Users\\bcalazans\\SystraGroup\\BNDES-CBTU-Produção - General\\02.RS\\2.2.Produção\\Arquivos Geográficos\\SHP\\'
path_files = {
    'NM_MESO':'METROPOLITANA DE PORTO ALEGRE',
    'setores': path_shp + 'Setores_Censitarios_RS.shp',
    'zoneamento':path_shp + 'RMPA.shp'}

#%% PE
dict_UF = {"UF": "PE", "code":26}    
path_shp = 'C:\\Users\\bcalazans\\SystraGroup\\BNDES-CBTU-Produção - General\\03.PE\\02.Produção\\Arquivos Geográficos\\SHP\\'
path_files = {
    'NM_MESO':'METROPOLITANA DE RECIFE',
    'setores': path_shp + 'SetorCensitário_UTM.shp',
    'zoneamento':path_shp + 'zonas_584.shp'}

#%%#%% SP
dict_UF = {"UF": "SP", "code":26}    
path_shp = 'C:\\Users\\bcalazans\\SystraGroup\\PITU2040 - 06- PRODUÇÃO\\Arquivos Geográficos\\'
path_files = {
    'NM_MESO':'METROPOLITANA DE SAO PAULO',
    'setores': path_shp + 'SetorCensitário_UTM.shp',
    'zoneamento':path_shp + 'Zoneamento_origemdestino_2017.shp.shp'}


#%% MAIN - RESULTADOS POR SC
# rode uma das células acima para configurar os caminhos da cidade desejada
# pega códigos para filtrar na base de dados
setores2filter, municip2filter, setores = get_codes2filter(path_files) 
ans = pd.DataFrame(index=setores2filter)
  
# lê CNEFE: registro dos estabelecimentos
df_cnefe = read_cnefe(path_data, dict_UF['code'])
ans = ans.merge(get_estab_cnefe(df_cnefe, setores2filter), left_index=True, right_index=True, sort=True, how='left').fillna(0)
cep = build_cep_data_from_cnefe(df_cnefe)

# lê tabelas do CENSO IBGE 2010
ans = ans.merge(get_popByAge(path_data, dict_UF['UF'], setores2filter), left_index=True, right_index=True,sort=True, how='left').fillna(0)
ans = ans.merge(get_popByMoney(path_data, dict_UF['UF'], setores2filter),left_index=True, right_index=True, sort=True, how='left').fillna(0)

# le o RAIS mais novo e faz o paranauê do CEP
raisByCep, raisByMuni = get_jobs_from_rais(path_data, 'RAIS_ESTAB_PUB.txt',municip2filter)
df_sc = ans.merge(get_jobs_by_SC(cep, setores, ans, raisByCep, raisByMuni),left_index=True, right_index=True, sort=True, how='left').fillna(0)

df_sc = get_vagas_educ_by_SC(df_sc)
#%% RESULTADOS POR MUNICIPIO
df_pib = read_pib(path_data, municip2filter) # info do PIB
df_rais = read_rais_all_years(path_data, municip2filter) # info empregos por muni

#%% SALVA
# ordena colunas
cols = ['COD_MUNI','#DOMICILIO_PARTICULAR', '#DOMICILIO_COLETIVO', 
        '#ESTAB_AGROPECUARIO', '#ESTAB_ENSINO', '#ESTAB_SAUDE', '#ESTAB_OUTROS',
        '#EM_CONSTRUCAO','TOT_ESTAB',
        'POP_00a06_anos', 'POP_07a14_anos', 'POP_15a25_anos', 'POP_26a65_anos',
        'POP_66+_anos', 'POP_0a0.5_SM', 'POP_0.5a1_SM', 'POP_1a2_SM',
        'POP_2a3_SM', 'POP_3a5_SM', 'POP_5a10_SM', 'POP_10a15_SM',
        'POP_15a20_SM', 'POP_20+_SM', 'POP_semSM',
        'NUM_JOBS',
        'CO_DISTRITO','NUM_EDUC_BAS','NUM_EDUC_SUP']
file = 'BD_dadosSocioeconomicos_'+dict_UF["UF"]+'2.xlsx'
with pd.ExcelWriter(os.path.join(path_data, file)) as writer:  
    df_sc[cols].to_excel(writer, index=True, sheet_name=dict_UF["UF"]+'_CS')
    df_pib.merge(df_rais, on=['ANO','COD_MUNI'], how='outer').to_excel(writer, index=False, sheet_name=dict_UF["UF"]+'_MUNI')
print('File saved!')




