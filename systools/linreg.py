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
import statsmodels.api as sm

import numpy as np
import pandas as pd

# systools modules
from helpers.linear_regression_make import fit_model, loop_models
from helpers.linear_regression_plot import plot_regression, open_html, html_abas

def fit_model(x, y, intercept=False, cov_type='nonrobust', plot=False):
    ''' Executa regressão e testa retirada de outliers
    Retorna dois modelos, um completo e outro sem outliers
    if plot=True, registra testes e resultados em um HTML 
    x: dataFrame com colunas das variáveis INDEPENDENTE
    y: dataFrame com as colunas da variável dependente (que queremos prever)
    '''
    model, model_out = fit_model(x, y, intercept, cov_type, plot)
    return model, model_out


def loop_models(df, Xcols, Ycol, mask=None, keepAll=False, CUT_R=0.5, force_intercept=False, kargs={}):
    '''
    Realiza a regressão de todas as combinações não correlacionadas
    Faz testes para ver se a regressão é válida ou não e salva informações em
    um dataframe para investigação

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    mask : boolean series, OPTIONAL
        Pass a mask to dataframe and rows can be ignored
    Xcols : list
        List of column names for independent stuff.
    Ycol : string
        NAme of column for the dependent variable.
    keepAll : TYPE, optional
        Manter todas as regressões, ainda que não tenham passado nos testes. 
        The default is False.
    CUT_R : TYPE, optional
        Rsquared de linha de corte. Valores maiores indicam que regressão pode
        melhorar tirando outliers. Realiza então a regressão do outlier. 
        The default is 0.5.
    force_intercert : bool
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

    '''
    df_regs = loop_models(df, Xcols, Ycol, mask, keepAll, CUT_R, force_intercept, kargs)
    return df_regs


def report_regression():
    # thos functions are on the linear_regression_plot
    plot_regression(model, x, y, intercept)
    open_html()
    html_abas(FileName, htmlFile, htmlFileOut, grafico)
    return namefile