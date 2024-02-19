# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:32:35 2022

@author: bcalazans

Módulo da regressão linear
> útil para a determinação de GERAÇÂO DE VIAGENS no modelo 4 etapas

Dado um conjunto de variáveis socioeconomicas e atração/produção das zonas,
gera todas as regressões estatisticamente plausíveis e solta uma tabela para
avalição crítica dos resultados

É possível gerar relatório em HTML de regress~eos específicas, para visualizar 
os testes estatísticos realizados no processo
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from tqdm import tqdm

# Systool modules
from .utils import linear_regression_make as lrm
from .utils.linear_regression_plot import plot_regression, give_name
from .utils import report


def fit_model(x, y, intercept=False, cov_type='nonrobust', plot=False, path=None, custom_name=''):
    """
    Executa regressão e testa retirada de outliers
    Retorna dois modelos, um completo e outro sem outliers

    Parameters
    ----------
    x : pd.Series ou pd.DataFrame
        Variáveis independentes do modelo de regressão.
    y : pd.Series
        Variável dependente do modelo de regressão. Geralmente, ATRAÇÃO ou PRODUÇÃO de viagens.
    intercept : bool, optional
        True para forçar que regressão cruze o eixo 0. The default is False.
    cov_type : str, optional
        See regression.linear_model.RegressionResults for a description of the available covariance estimators...
        The default is 'nonrobust'.
    plot : bool, optional
        Gera um arquivo HTML com vários testes estatísticos. The default is False.
    path : str, optional
        Salva o arquivo HTML no caminho indicado. The default is None (does not save file)

    Returns
    -------
    model : container or StatsModelResults
        Modelo com todos os registors.
    model_out : container or StatsModelResults
        Modelo otimizado sem outliers.

    """
    # TODO - mudar o default para o default so stats

    if isinstance(x, pd.Series):
        x = pd.DataFrame(x)
    # if isinstance(y,pd.Series): y = pd.DataFrame(y)
    # http s://stats.stackexchange.com/questions/47913/pandas-statsmodel-scikit-learn
    y = y.fillna(0)
    
    # TODO -- if X has N/a drop zones
    # TODO -- if ZN missing in X or Y, drop in both    
    
    # substitui zeros com pequeno ruído para evitar SingularMAtrix error
    x = x+0.00001*np.random.rand(*x.shape)
    y = y+0.00001*np.random.rand(*y.shape)
    
    if intercept:
        model = sm.OLS(y, sm.add_constant(x)).fit(cov_type=cov_type)
    else:
        model = sm.OLS(y, x).fit(cov_type=cov_type)
    
    model_out, dfr, xx, yy, grafico_html = lrm.find_outliers(model, x, y, intercept, cov_type, plot)
    if plot: 
        # Monta o nome do HTML e gráficos
        if path is None:
            path = os.getcwd()
        name = give_name(x, y, intercept, custom_name)
        
        # plota gráficos e salva HTML
        list_2_plots_a = plot_regression(model, x, y, intercept)
        
        if model_out is None:
            report.save_html(path, name, list_2_plots_a)
        else:
            list_2_plots_b = plot_regression(model_out, xx, yy, intercept)
            dict_pages = {'Modelo completo': list_2_plots_a,
                          'Modelo sem outliers': list_2_plots_b,
                          'Grafico R²': grafico_html}
            report.save_html(path, name, dict_pages)    
        
        # tenta abrir HTML automaticamente
        report.open_html(path, name)
    return model, model_out


def loop_models(df, xcols, ycol, mask=None, keep_all=False, cut_r=0.5, force_intercept=False, kargs={}):
    """
    Realiza a regressão de todas as combinações não correlacionadas
    Faz testes para ver se a regressão é válida ou não e salva informações em
    um dataframe para investigação

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    mask : boolean series, OPTIONAL
        Pass a mask to dataframe and rows can be ignored
    xcols : list
        List of column names for independent stuff.
    ycol : string
        NAme of column for the dependent variable.
    keep_all : TYPE, optional
        Manter todas as regressões, ainda que não tenham passado nos testes. 
        The default is False.
    cut_r : TYPE, optional
        Rsquared de linha de corte. Valores maiores indicam que regressão pode
        melhorar tirando outliers. Realiza então a regressão do outlier. 
        The default is 0.5.
    force_intercept : bool
        if TRUE best model is alwys the model that intercepts
    kargs : DICT, optional
        Parâmetros para fit_model: 
            > intercept (True or Flse)
            > plot (True or False)
            > covType (nonrobust, HC3, etc)

    Returns
    -------
    df_regs : pandas dataFrame
        Contains all regressions found with some indicator to help us choose for the best one.

    """
    warnings.filterwarnings('ignore')
    if mask is None:
        mask = np.ones(len(df), dtype=bool)
    # TODO -- criar status se reg teve outliers eliminados ou não
    print('Default regressions performed with {:.1%} of data'.format(mask.sum()/len(mask)))
    df_regs = pd.DataFrame(columns=['x', 'Rsquared', 'intercept', 'covType', 'ZONAS',
                                    'PASS_TESTS', 'NUM_COEF_NEGATIVO'])
    # calcula todas possibilidades de regressões em que não há muita correlação
    comb = lrm.get_combinations(xcols)
    corr_pairs = lrm.get_correlated_pairs(df, xcols)
    comb = lrm.drop_combinations(comb, corr_pairs, xcols)

    # calcula um modelo para cada possibilidades
    for c in tqdm(comb, position=0, leave=True, desc='Making regressions...'):
        
        if isinstance(c, tuple):
            c = list(c)
        else:
            c = [c]  # need this for one column value
        
        x = df.loc[mask, c]
        y = df.loc[mask, ycol]
       
        # make two possible regressions
        model_a, model_a_out = fit_model(x, y, intercept=True, **kargs)
        model_b, model_b_out = fit_model(x, y, intercept=False, **kargs)
           
        # choose best model
        if force_intercept:
            model = model_a
            model_out = model_a_out
            intercept = True
        else:
            if model_a.rsquared > model_b.rsquared:
                model = model_a
                model_out = model_a_out
                intercept = True
            else: 
                model = model_b
                model_out = model_b_out
                intercept = False
        
        # se modelo é aceitavel, salva as regressões
        if model.rsquared > cut_r:
            df_regs = lrm.save_model(model, df_regs, intercept, lrm.test_conditions(model))
            df_regs = lrm.save_model(model_out, df_regs, intercept, lrm.test_conditions(model_out))

    print('{:5} regressões decentes (R² > {:}) foram geradas'.format(len(df_regs), cut_r))
    print('{:5} regressões passaram nos testes'.format((df_regs.PASS_TESTS == 'SIM').sum()))
    # TODO - imprimir aqui as condições impostas para passar nos testes
    
    if not keep_all:
        df_regs = df_regs[df_regs.PASS_TESTS == 'SIM']
    
    df_regs['numXvars'] = df_regs.x.str.len().astype(int)
    df_regs['numZones'] = df_regs.ZONAS.str.len()
    df_regs['Rsquared'] = df_regs['Rsquared'].astype('float').round(4)
    df_regs.sort_values('Rsquared', ascending=False, inplace=True)
    
    if len(df_regs) > 0:
        # plot the R results  
        plt.subplots()
        sns.set_style("ticks")
        sns.swarmplot(data=df_regs, x="numXvars", y="Rsquared", 
                      hue="PASS_TESTS",
                      palette={'NOP': 'red', 'SIM': 'green'}
                      )
        sns.despine(trim=True)
        
        # plot the usage of the variabels
        # mostra quantas vezes uma variável X foi usada em um modelo contendo numXvars
        usage = df_regs.set_index('numXvars').x.explode().reset_index().groupby(['numXvars', 'x']).size().unstack().T
        plt.subplots()
        sns.heatmap(usage, cmap='Blues', annot=True)
    return df_regs
