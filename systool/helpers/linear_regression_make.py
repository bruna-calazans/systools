# -*- coding: utf-8 -*-
"""
REFERENCIAS:
    https://towardsdatascience.com/perform-regression-diagnostics-and-tackle-uncertainties-of-linear-models-1372a03b1f56
    https://zhiyzuo.github.io/Linear-Regression-Diagnostic-in-Python/
    https://boostedml.com/2018/08/testing-linear-regression-assumptions-the-kaggle-housing-price-dataset.html
    https://pythonfordatascienceorg.wordpress.com/linear-regression-python/
    https://blog.minitab.com/blog/adventures-in-statistics-2/understanding-t-tests-t-values-and-t-distributions#:~:text=A%20test%20statistic%20is%20a,data%20during%20a%20hypothesis%20test.&text=A%20t%2Dvalue%20of%200,of%20the%20t%2Dvalue%20increases.
    https://stats.stackexchange.com/questions/137498/how-to-interpret-the-direction-of-the-harvey-collier-test-and-rainbow-test-for-l

Created on Mon Aug 31 09:36:40 2020

@author: bcalazans

OBJETIVO GERAL
Criar uma rotina do Modelo 4-etapas rapidamente replicável para todas as cidades

SEQUENCIA DE PASSOS
## STEP 1 : Geração
    > Fazer levantamento de variáveis socioeconômicas explicativas
    > Fazer a matriz OD do TCol usando (SBE+GPS) (ou teremos uma ref externa)
    > Fazer um modelo de regressão

## STEP 2 : Distribuição

## STEP 3 : Divisão modal (+ projeção ?)

## STEP 4 : Alocação
    > TransCAD modelling 

------------------------
OBJETIVO
Definir um modelo de regreção pra ATRAÇÃO e outro pra PRODUÇÃO

Como:
    
    1. Determinação de variáveis explicativas que vão influenciar na geração 
        de viagens, ora na atração de viagens, ora na produção
        a. Esta etapa está associada a um passo preliminar que envolve 
        estabelecer/conhecer as principais motivações e comportamentos
        de viagens dentro do universo de estudo. Motivações genéricas 
        de viagens: por motivo trabalho; por motivo estudo.
        
        b. as variáveis explicativas selecionadas devem apresentar baixa 
        correlação entre si. Variáveis com forte relação de dependência 
        (alta correlação) riscam tendencionar os resultados da regressão 
        linear e  prejudicam a interpretação dos resultados 
        (análise da relação causa-efeito). 
             
    2. Determinação da relação de causa e efeito (modelo de regressão linear)
        a. Testar regressão para diferentes combinações de variáveis
        b. Testes possíveis para melhorar os resultados dos modelos de regressão:
            i. testar partindo ou não da origem
            ii. tirar outliers (tira de todos os BDs)
            
    3. Validação dos modelos de regressão:
        a. Verificar resultados dos testes estatísticos
            i. test-T,  p-value, F-score, R², etc
        b. Conferência dos coeficientes atribuídos a cada variável
            i. interpretação da equação de regressão final obtida
                > coeficientes negativos assosciados a alguma variável podem 
                ser contra-intuitivos;
                > constantes - coeficiente "b" - muito elevadas podem ser 
                contra-intuitivas em análises de projeção de demanda

INPUTS
    1. alpha = confiabilidade = 0,05 = 95% de confiabilidade
    2. Entrada de dados: associados a cada ZONA de tráfego
        (y) = atração OU produção = tiradas da OD SBE
        (x) = bancos de dados oficiais (IBGE, RAIS, etc)

OUTPUTS
Página HTML para cada regressão realizada, a página permite a análise crítica
do modelo gerado e decisão de qual equação utilizar
"""
import os
import warnings
import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.stats.api as sms
import statsmodels.stats.stattools as st
import base64
from io import BytesIO
from itertools import combinations 
from tqdm import tqdm


def find_outliers(model, x, y, intercept, cov_type,plot=False):  
    '''
    Dado um modelo, re-faz regressões graduais a partir das 10 observações mais
    relevantes até incluir todas as observações.
    
    Analisa o resultado e retorna o modelo de maior R² dentro de um limite de 
    retirar apenas 10% das observações

    Parameters
    ----------
    model : statsmodels.regression.linear_model.RegressionResultsWrapper
        modelo inicial base de regressão
    x : pandas.core.frame.DataFrame
        variáveis explicativas
    y : pandas.core.series.Series
        variável dependente
    intercept : bool
        True or False para interceptar o eixo em zero
    cov_type : string
        parâmetro de fit_model()

    Returns
    -------
    model_out : statsmodels.regression.linear_model.RegressionResultsWrapper
        modelo da melhor regressão sem outliers.
    dfR : pandas.core.frame.DataFrame
        lista das regressões progressivas realizadas.
    Xoutlier : pandas.core.frame.DataFrame
        variáveis independentes, sem os outliers.
    Youtlier : pandas.core.series.Series
        variável dependente, sem os outliers.

    '''
    model_out = None # will return an empty list if there is "no" outlier
    # para o modelo encontrado, refaz a regressão um a um para estudar a evolução do R²
    df = x.merge(y,left_index=True, right_index=True)
    df['RESID'] = abs(model.resid)
    df = df.sort_values(by=["RESID"],ascending=True)
    
    # realiza regressões cada hora aumentando o número de observações
    dfR=pd.DataFrame(columns=['R2','NofObservations','Zones'], dtype=float)
    for i in range(10, df.shape[0]+1):
        zones = df.index[:i].values
        if intercept: model_out = sm.OLS(y.loc[zones], sm.add_constant(x.loc[zones])).fit(cov_type=cov_type)
        else:  model_out = sm.OLS(y.loc[zones], x.loc[zones]).fit(cov_type=cov_type)

        new_line={'R2':model_out.rsquared,
                 'NofObservations':len(zones),
                 'Zones':zones.tolist()}
        dfR = pd.concat([dfR, 
                         pd.DataFrame.from_records([new_line])],ignore_index=True)
        
    min_zn_out = len(zones)-int(0.1*len(zones)) # Qtd total de zonas menos os 10% de outliers
    xmax = len(zones)
    xmin = dfR['NofObservations'].min()
    zn_rmax = int(dfR.set_index('NofObservations').loc[min_zn_out:,'R2'].idxmax())
    rmax = dfR.set_index('NofObservations').loc[zn_rmax,'R2']

    # Para gerar o mapa   
    mask = dfR.NofObservations.isin(list(range(zn_rmax+1,xmax+1)))
    dfR['Bool']=np.where(mask,1,0)
    
    fightml = ''
#   maphtml = ''
    ymin = dfR['R2'].min()
    if plot:
    # TODO mudar esse código para linear_regression_make e ver se tem como enxugar ele
        lastick = [xmax]
        plt.style.use('ggplot')
        plt.figure(figsize=(26.6667,15))
        plt.gcf().subplots_adjust(right=2)
        dfR.plot(x='NofObservations',y='R2',color='darkblue', label='R²')
        plt.xticks(list(plt.xticks()[0])+lastick)
        plt.axis([xmin-2, xmax, ymin-0.01, 1.005])
        plt.axvline(min_zn_out,label='10% outliers',color='darkred')
        plt.axhline(rmax,linestyle='--',color='black')
        plt.ylabel('Rsquared',
                   fontdict={'weight':'bold',
                             'size':10,
                             'fontfamily':'serif'})
        plt.xlabel('Number of Observations',
                   fontdict={'weight':'bold',
                             'size':10,
                             'fontfamily':'serif'})
        plt.text(xmax+0.3,rmax,str('R² max = {0:.4f}'.format(rmax) + " ({} zonas)".format(zn_rmax)))
        plt.text(min_zn_out-1.7,ymin-0.02,str(min_zn_out),fontsize=12, color='darkred')
        plt.legend(facecolor='white')
        plt.title('Evolução do R² com o aumento do número de observações',
                  fontdict={'family': 'arial',
                            'color': 'black',
                            'weight': 'bold',
                            'size': 11})
        tmpfile = BytesIO()
        plt.savefig(tmpfile, format='png', bbox_inches = "tight")
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        fightml = '''<img src=\'data:image/png;base64,{}\'>'''.format(encoded)

#chama a função de gerar o mapa       
#      mapa_zn_out(zns,dfR)
    
    # Escolhe melhor regressão retirando no máx 10% dos outliers
    Xoutlier = []
    Youtlier = []
    from pandas.core.common import flatten    
    zones = dfR[dfR.NofObservations>=min_zn_out].query('R2==R2.max()').Zones.values.tolist()
    zones = list(flatten(zones))
    if len(zones) < len(y):
        Xoutlier = x.loc[zones]
        Youtlier = y.loc[zones]
        if intercept: model_out = sm.OLS(Youtlier, sm.add_constant(Xoutlier)).fit(cov_type=cov_type)
        else:  model_out = sm.OLS(Youtlier,Xoutlier).fit(cov_type=cov_type) 
        
    return model_out, dfR, Xoutlier, Youtlier, fightml  

#def mapa_zn_out(shp_zonas, dfR)

def corr_mtx(df):
    fig, ax = plt.subplots()
    mask = np.zeros_like(df.corr(), dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    sns.heatmap(df.corr(), mask = mask, annot=True,vmin=-1, vmax=1, center=0, cmap='RdBu')
    return
         

def linear_harvey_collier(model):
    ''' Test fot linearity unsing Harvey-Collier teory
    Original function has a bug
    sms.linear_harvey_collier(model)
    https://github.com/statsmodels/statsmodels/pull/6727
    
    Call this one instead
    '''   
    skip = len(model.params)  # bug in linear_harvey_collier
    rr = sms.recursive_olsresiduals(model, skip=skip, alpha=0.95)
    #try: rr = sms.recursive_olsresiduals(model, skip=skip, alpha=0.95)
    #except: rr = sms.recursive_olsresiduals(model, skip=skip, alpha=0.95)
    #dfDirty = dfClean+0.00001*np.random.rand(n, 2)
    return st.stats.ttest_1samp(rr[3][skip:], 0)


def test_conditions(model):
    ''' Testa várias condições estatísticas que norteiam a validação ou não 
    de um modelo de regressãol linear. O ideal é investigar no HTML resumo
        condition0 - verifica se há variáveis 100% correlacionadas
        condition1 - teste p-val < 0.05 e t-val> 2
        condition2 - harvey-colier (linearidade) > 0.05
        condition3 - DurbinWatson entre 1 e 3
    
    retorna VERDADEIRO apenas se passar em todas as condições acima
    '''
    condition1 = condition2 = condition3 = False
    
    # verifica se há variáveis 100% correlacioandas (ou colunas duplicadas)
    if len(model.params) == 1: condition0=True,
    else:
        corr = np.corrcoef(model.model.exog.T)
        mask = np.eye(len(model.model.exog_names), dtype = bool)
        non_diagonal_elements = corr[~mask]
        # remove potenciais NaN que acontece qndo tem CONSTANTE
        non_diagonal_elements = non_diagonal_elements[~np.isnan(non_diagonal_elements)]
        # se fora da diagnonal contem corr=1 então não deveria gerarl modelo!
        condition0 = (non_diagonal_elements < 0.9999).all()

    if condition0:
        # testa p-value e test T
        values = pd.DataFrame([abs(model.pvalues), abs(model.tvalues)], 
                              index=['p-val', 't-val']).T
        condition1 = ((values['p-val'] < 0.05) & 
                    (values['t-val'] > 2)).all()
        # testa harvey-colier > 5%
        #condition2 = sms.linear_harvey_collier(model).pvalue > 0.05
        try:condition2 = linear_harvey_collier(model).pvalue > 0.05
        except: 
            #print('There still a bug in HARVEY for singular matrix...')
            #print('\t', model.model.exog_names)
            #condtion2 = False
            raise Exception(model.model.exog_names)
        # Durbin-Watson aceitável para análise
        condition3 = ((1 < st.durbin_watson(model.resid, axis=0)) &
                      (3 > st.durbin_watson(model.resid, axis=0)))
   
    return condition0 & condition1 & condition2 & condition3


def get_combinations(cols):
    '''Get all combinations of the X variabels'''
    comb = []
    for i in tqdm(range(len(cols)), desc='Getting combinations for all variables'): 
        comb.extend(list(combinations(cols, i)) )
    del comb[0]
    print('{:,} possibilites of regression to do!'.format(len(comb)))
    return comb

    
def get_correlated_pairs(df, Xcols, LIMIT=0.5):
    ''' return a list of list of correlated enodg variables
    LIMIT: consider correlated with coef > LIMIT
    '''
    print('Get correlated pairs...')
    # get correlation values
    corr = df[Xcols].corr()
    # filter diagonal
    mask_diagonal = np.eye(len(Xcols), dtype = bool)
    # filter ultra correlated values
    mask_correlated = corr > LIMIT
    # filter upper triangle
    mask_upperTriangle = np.zeros_like(corr, dtype=np.bool)
    mask_upperTriangle[np.triu_indices_from(mask_upperTriangle)] = True
    
    # get True/False for ultra correlated
    corr = (~mask_diagonal) & mask_correlated & mask_upperTriangle

    # get names that are REALLY correlated
    corr = corr.reset_index().melt(id_vars='index').query('value == True')
    corr_pairs = corr[['index','variable']].values.tolist()
    return corr_pairs
  
    
def get_mean_and_std_from_kde(residuals):
    ''' Get meand and std values from the kde of the residuals
    não consegui fazer usando fórmula, então pra andar rápido usei o mesmo código
    que está em _plot'''
    import scipy as sp
    fig, (aq, ax) = plt.subplots(1,2, figsize=(16,5))
    _, (__, ___, r) = sp.stats.probplot(residuals, plot=aq, fit=True)
    aq.spines['top'].set_visible(False)
    aq.spines['right'].set_visible(False)

    # Create distplot in matplolib (there is no kde func in plotly)
    #fig, ax = plt.subplots()
    ax=residuals.plot.kde(ax=ax, title='Histograma dos residuais')
    mean_val = np.mean(ax.get_children()[0]._x)
    std_val = np.std(ax.get_children()[0]._x)
    plt.close(fig)
    return mean_val, std_val


def save_model(model, df_regs, intercept, condition):
    ''' Salva no DataFrame algumas informações sobre uma regressão gerada '''
    mean, std = get_mean_and_std_from_kde(model.resid)
    condition = 'SIM' if condition else 'NOP'
    df_regs = df_regs.append({'x':list(model.params.index), 
                              'Rsquared':model.rsquared,
                              'intercept':intercept,
                              'covType': model.cov_type,
                              'ZONAS': model.fittedvalues.index.values.tolist(),
                              'PASS_TESTS': condition,
                              'NUM_COEF_NEGATIVO':(model.params < 0).sum(),
                              'HARVEY_COLLIER':linear_harvey_collier(model).pvalue,
                              'DURBIN_WATSON':st.durbin_watson(model.resid, axis=0),
                              'MEAN_KDE':mean,
                              'STD_KDE':std}, 
                             ignore_index=True)
    
    return df_regs


def drop_combinations(myComb, corr_pairs, Xcols):
    '''drop combinations that we do not want to do a regression since contains 
    a pair of correlated variables'''
    
    myComb = pd.DataFrame({'combinations':myComb})
    myComb = myComb[myComb.combinations.apply(len)>1] # tira um prq está como tuple
    
    # build matrix that each column is the name of endog variable and 
    # each row sets to 1 if the column belogns to that combination arrange
    #temp = myComb.sample(10)
    temp = myComb.combinations.explode().reset_index().groupby(['index','combinations']).size().unstack()
    myComb = myComb.merge(temp, left_index=True, right_index=True)
    # if combination (row) contains a pair of correlated variables, dropit
    for pair in tqdm(corr_pairs, position=0, leave=True, desc="Droping combinations with correlated values..."):
        msk1 = myComb[pair[0]] == 1
        msk2 = myComb[pair[1]] == 1
        myComb = myComb[~(msk1 & msk2)]
    
    # add possibilidade de valores únicos
    myComb = myComb.combinations.tolist() + Xcols 
    print('{:,} non-correlated possibilities to do!'.format(len(myComb)))    
    return myComb

  

    
