# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 19:29:47 2020

@author: bcalazans

simple example for linear regression
"""
import matplotlib.pyplot as plt
import pandas as pd
import linear_regression_make as lrm

#%%  LOAD FILES
#Tabela da ATRA e PROD de viagens por zona + variáveis explicativas
df = pd.read_csv('inputGeracao.txt', sep=";", decimal=',')
df.head()

#%% REGRESSÃO ATRAÇÃO
y = df['ATRA']                      # digite nome da coluna Y
x = df[['EMPREGOS','ENSINO']]       # digite nome das colunas X

model_a = lrm.fit_model(x, y, intercept=False, plot=True)
model_b = lrm.fit_model(x, y, intercept=True, plot=True)

# see percentual error (residual) to drop some outliers
fig, ax = plt.subplots()
plt.plot(sorted(abs(model_a.resid)/y))
values_to_drop = (abs(model_a.resid)/y).nlargest(5).index

model_c = lrm.fit_model(x[~x.index.isin(values_to_drop)], 
                    y[~y.index.isin(values_to_drop)], 
                    intercept=False, plot=False)


#%%REGRESSÃO PRODUÇÃO
y = df['PROD']      # digite nome da coluna Y
x = df['POP']       # digite nome das colunas X

model_a = lrm.fit_model(x, y, intercept=False, plot=False)
model_b = lrm.fit_model(x, y, intercept=True, plot=False)

#%% loop models
df_regs = lrm.loop_models(df,np.ones(len(df)),['EMPREGOS','ENSINO','POP'],'ATRA',keepAll=True)

