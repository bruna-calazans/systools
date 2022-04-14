# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 08:32:27 2020

@author: bcalazans

Funções para plotar resultados da regressão em um arquivo HTML
"""
import os, sys
import pandas as pd
import scipy as sp
import numpy as np


import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
import statsmodels.stats.api as sms
import statsmodels.tsa.api as smt
import statsmodels.stats.stattools as st
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.graphics import utils
from statsmodels.tsa.stattools import acf, pacf

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.tools as tls
import plotly.express as px
import plotly.figure_factory as ff
import plotly as py
from plotly.figure_factory import create_distplot


# systools modules
# TODO ideally i do not want to mess around with path
sys.path.insert(1, os.path.abspath('.'))
from report import text2html

#%% nomeia arquivo HTML no formato desejado 
#regModel_Ycolumns=Xcolumns_intercepYESorNO_ZNnumberOfRows.html
def concatena_cols(df):
    columns = list(df.columns) if len(df.shape) > 1 else df.name
    tam = len(columns)
    palavra = ''
    for pos in range(tam):
        if(pos<(tam-1)):
            palavra = palavra + columns[pos] + '+'
        else:
            palavra = palavra + columns[pos]
    return palavra

# Monta o nome do HTML
def give_name(x, y, intercept):
    Ycolumns = y.name
    Xcolumns = concatena_cols(x)
    if(intercept):
        inter = '_intercepYES_ZN'
    else:
        inter = '_intercepNO_ZN'
    number_of_rows = str(len(x))
    return 'regModel_' + Ycolumns + '=' + Xcolumns + inter + number_of_rows + '.html'


#%% Aux plots
def plot_predictions(y, y_predicted, student_residuals):
    '''Plota lado a lado gráfico de Observed X Predicted + Studentized Errors'''
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Valores observados X estimados',
                                                   'Scale Location'])
    
    # Observed X Predicted
    X_plot = [min(y), max(y)]
    fig.add_trace(go.Scatter(x=y, y=y_predicted, 
                             #name="pontos", 
                             mode='markers', 
                             marker=dict(color='darkblue', size=8),
                             hovertext=y.index),
                 row=1, col=1)
    fig.add_trace(go.Scatter(x=X_plot, y=X_plot, line=dict(color='darkred', width=3)),
                 row=1, col=1)
    fig.update_xaxes(title_text="Observado", row=1, col=1)
    fig.update_yaxes(title_text="Estimado", row=1, col=1)
    
    # Scale-location
    fig.add_trace(go.Scatter(x=y_predicted, y=student_residuals, 
                             mode='markers', 
                             marker=dict(color='darkblue', size=8)),
                 row=1, col=2)
    fig.update_xaxes(title_text="Estimado", row=1, col=2)
    fig.update_yaxes(title_text="Studentized Residuals", row=1, col=2)
    fig.update_layout(showlegend=False)
    return fig


def residuals_histogram(residuals):
    #this works
    '''
    fig = go.Figure(
        layout=dict(
            title="Residuals Histogram",
            xaxis_title='Residuals',
            yaxis_title='',
        )
    )
    
    #fig = go.Figure(data=[go.Histogram(x=residuals, histnorm='probability')])
    
    fig.add_trace(
            go.Histogram(x=residuals,  histnorm='density', xbins=dict(size=10))
    )
    '''
    # this also works
    #fig = px.histogram(x=residuals, nbins=10, title='Histogram of the Residuals')
    fig, (aq, ax) = plt.subplots(1,2, figsize=(16,5))
    _, (__, ___, r) = sp.stats.probplot(residuals, plot=aq, fit=True)
    aq.spines['top'].set_visible(False)
    aq.spines['right'].set_visible(False)

    # Create distplot in matplolib (there is no kde func in plotly)
    #fig, ax = plt.subplots()
    ax=residuals.plot.kde(ax=ax, title='Histograma dos residuais')
    mean_val = np.mean(ax.get_children()[0]._x)
    std_val = np.std(ax.get_children()[0]._x)
    max_val = np.max(ax.get_children()[0]._y)
    # Annotate points
    ax.annotate('{:10}{:>10,.2f}<br>{:10}{:>10,.2f}'.format('  Média',mean_val,'  Desvio',std_val), 
                xy=(mean_val, max_val),verticalalignment='top')
    # vertical dotted line originating at mean value
    #plt.axvline(mean_val, linestyle='dashed', linewidth=2, color='#202231') # does not work with plotly
    ax.plot([mean_val,mean_val], [0,max_val], linestyle='dashed', linewidth=2, color='#202231')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # plot histogram
    ax=residuals.hist(density=1, ax=ax, grid=False)
        
    #transform in plotly object figure
    fig = py.tools.mpl_to_plotly(fig)
    
    return fig


def plot_harvey(PVALUE):
    fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = PVALUE,
    number = {'suffix': "%"},
    mode = "gauge+number",
    title = {'text': "Harvey-Collier", 'font': {'size': 24}},
    #delta = {'reference': 380},
    gauge = {'axis': {'range': [0, 100]},
             'bar': {'thickness': 0},
             'steps' : [
                 {'range': [0, 5], 'color': "darkred"},
                 {'range': [5, 100], 'color': "green"}],
             'threshold' : {
                 'line': {'color': "black", 'width': 4}, 'value': PVALUE}}))
    return fig 


def tablePlot(df_table, index=False):
    '''
    fig = go.Figure(
        layout=dict(
            title="Homoscedasticity"
        )
    )
    fig.add_trace(
            go.Table(
                    header=dict(
                            values = names,
                            font = dict(size=10),
                            align = "left"),
                    cells=dict(
                            values = param,
                            align = "left")
            )
    )
    '''
    
    fig =  ff.create_table(df_table, index=index)
    fig.update_layout(title="Durbin-Watson",hovermode=False, width=800)
    return fig


def durbin_watson(pvalue):
    '''
    fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = PVALUE,
    mode = "gauge+number+delta",
    title = {'text': "Durbin-Watson", 'font': {'size': 24}},
    #delta = {'reference': 380},
    gauge = {'axis': {'range': [0, 4]},
             'bar': {'thickness': 0},
             'steps' : [
                 {'range': [0, 2], 'color': "darkred"},
                 {'range': [2, 4], 'color': "darkblue"}],
             'threshold' : {
                 'line': {'color': "black", 'width': 4}, 'value': PVALUE}}))
    '''
    #pvalue=1.437
    pvalue = round(pvalue, 4)
    img = np.tile(np.linspace(0,4, num=200),(2,1))
    #img = [np.linspace(0,4, num=100)]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    #fig.add_trace(px.imshow(img,color_continuous_scale ='RdBu').data[0], row=1, col=1)
    #fig = px.imshow(img,color_continuous_scale ='RdBu')
    fig.add_trace(go.Heatmap(z=img, colorscale='RdBu',showscale =False), 
              secondary_y=False)

    fig.add_trace(go.Scatter(
                    x=[pvalue*50, pvalue*50],
                    y=[0, 2],
                    mode="lines+text",
                    line=go.scatter.Line(color="black"), 
                    showlegend=False,hoverinfo='skip'),
    secondary_y=True
    )
    fig.update_layout(
    annotations=[
        dict(
            x=pvalue*50-4,
            y=0.55, textangle=-90,
            showarrow=False,
            text=str(pvalue))])
    fig.update_yaxes(title_text="Correlação <b>negativa</b>", showticklabels=False, secondary_y=False)
    fig.update_yaxes(title_text="Correlação <b>positiva</b>", showticklabels=False, secondary_y=True)

    fig.update_xaxes(title_text="",
                 tickmode="array",tickvals =[0,50,100,150,199],ticktext=['0','1','2','3','4'])

    fig.update_layout(title="Durbin-Watson",hovermode=False, height=330)
    fig.show()
    return fig
    

def prepare_data_corr_plot_alterado(x, lags, zero):
    zero = bool(zero)
    irregular = False if zero else True
    if lags is None:
        # GH 4663 - use a sensible default value
        nobs = x.shape[0]
        lim = min(int(np.ceil(10 * np.log10(nobs))), nobs - 1)
        lags = np.arange(not zero, lim + 1)
    elif np.isscalar(lags):
        lags = np.arange(not zero, int(lags) + 1)  # +1 for zero lag
    else:
        irregular = True
        lags = np.asanyarray(lags).astype(np.int)
    nlags = lags.max(0)

    return lags, nlags, irregular
    
    

def plot_acf_durbin_watson(pvalue, x, ax=None, lags=None, alpha=.05, 
                           use_vlines=True, qstat=False,fft=False, 
                           zero=True,
                           vlines_kwargs=None, **kwargs):
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Autocorrelation','Durbin Watson = ' + '{:.5}'.format(pvalue)], 
                        specs=[[{},{"secondary_y": True}]])

    # PLOT ACF
    #fig, ax = utils.create_mpl_ax(ax)
    
    lags, nlags, irregular = prepare_data_corr_plot_alterado(x, lags, zero)
    vlines_kwargs = {} if vlines_kwargs is None else vlines_kwargs
    
    nlags=len(x)-1
    lags = np.arange(not zero, nlags + 1)
    
    confint = None
    # acf has different return type based on alpha
    if alpha is None:
        acf_x = acf(x, nlags=nlags, alpha=alpha, fft=fft,qstat=qstat)
    else:
        acf_x, confint = acf(x, nlags=nlags, alpha=alpha, fft=fft,qstat=qstat)
    
    if irregular:
        acf_x = acf_x[lags]
        if confint is not None:
            confint = confint[lags]

    lags_original = lags
    acf_x_original = acf_x

    if confint is not None:
        if lags[0] == 0:
            lags = lags[1:]
            confint = confint[1:]
            acf_x = acf_x[1:]
        lags = lags.astype(np.float)
        lags[0] -= 0.5
        lags[-1] += 0.5
        #ax.fill_between(lags, confint[:, 0] - acf_x,confint[:, 1] - acf_x, alpha=.25)
        
        fig.add_trace(go.Scatter(x=lags, y=confint[:, 0] - acf_x,
                        fill=None,
                        mode='lines',
                        line_color='rgb(234, 188, 196)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=lags,
                        y=confint[:, 1] - acf_x,
                        fill='tonexty', # fill area between trace0 and trace1
                        mode='lines', line_color='rgb(234, 188, 196)'), row=1, col=1)       
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, xaxis_zeroline=False, showlegend=False)#plot_bgcolor='white'
        
        fig.add_trace(go.Scatter(x=lags_original, y=acf_x_original, mode='markers', marker=dict(color='darkblue', size=6)), row=1, col=1)
        #fig.show()
        
    # PLOT DURBIN WATSON
    
    pvalue = round(pvalue, 4)
    img = np.tile(np.linspace(0,4, num=200),(2,1))
    #img = [np.linspace(0,4, num=100)]
    
    #fig = make_subplots(specs=[[],[{"secondary_y": True}]])
    
    #fig.add_trace(px.imshow(img,color_continuous_scale ='RdBu').data[0], row=1, col=1)
    #fig = px.imshow(img,color_continuous_scale ='RdBu')
    #fig.add_trace(go.Heatmap(z=img, colorscale='RdBu',showscale =False), secondary_y=False, row=1, col=2)
    fig.add_trace(go.Heatmap(z=img, colorscale='RdBu',showscale =False), row=1, col=2)
    fig.add_trace(go.Scatter(
                    x=[pvalue*50, pvalue*50],
                    y=[0, 2],
                    mode="lines+text",
                    line=go.scatter.Line(color="black"), 
                    showlegend=False,hoverinfo='skip'),
    secondary_y=True, row=1, col=2)
    fig.update_layout(
        annotations=[
            dict(
                x=pvalue*50-4,
                y=0.55, textangle=-90,
                showarrow=False,
                text=str(pvalue))])
    
    fig.update_yaxes(title_text="Correlação <b>negativa</b>", showticklabels=False, secondary_y=False,row=1, col=2)
    fig.update_yaxes(title_text="Correlação <b>positiva</b>", showticklabels=False, secondary_y=True,row=1, col=2)
    '''
    
    fig.update_yaxes(title_text="Correlação <b>negativa</b>", showticklabels=False, row=1, col=2)
    fig.update_yaxes(title_text="Correlação <b>positiva</b>", showticklabels=False, row=1, col=2)
    '''
    fig.update_xaxes(title_text="",tickmode="array",tickvals =[0,50,100,150,199],ticktext=['0','1','2','3','4'], row=1, col=2)

    #fig.update_layout(title="Durbin-Watson",hovermode=False, height=330, row=1, col=2)
    
    return fig

                    

def multicollinearity(corr_df):
        '''
        fig = go.Figure(data=go.Heatmap(z=val_x.corr().values.tolist()),
                    x = list(val_x.columns),
                    y = list(val_x.columns))
        #fig.add_trace(go.Heatmap(x))
        fig.update_layout(title='Multicollinearity of features')
        '''
        # good color scales: Blues, bluyl, brwnyl, bugn, bupu, ylorrd
        fig = px.imshow(corr_df, color_continuous_scale ='Blues', 
                        title='Multicollinearity of features'
                        )
        
        return fig


def write_formula_fancy(model, y):
    formula = ''
    for var, coef in zip(reversed(model.params.index.tolist()), reversed(model.params.values)):
        if var =='const': formula = formula + '{0:+.3f}'.format(coef)
        else: formula = formula + '{0:+.3f}'.format(coef) + ' * ' + var + ' '
    formula = y.name + ' = ' + formula
    return formula

#%% main plotter
def plot_regression(model, x,y, intercept):
    list_2_plots = []
    residuals = model.resid
        
    # Escreve equação no início do documento        
    formula = write_formula_fancy(model, y)
    list_2_plots.append(
        text2html(title='REGRESSÃO LINEAR - ' + y.name + ' - ' + str(len(y)) + ' ZONAS',
                  subtitle=formula,
                  text='R-squared {:10.4}'.format(model.rsquared)))
    
    # see exog vars
    #for X_var in x.columns: _ = sm.graphics.plot_regress_exog(model, X_var)

    ## Observed vs Predicted values and Studentized residuals         
    student_residuals = pd.Series(np.abs(model.get_influence().resid_studentized_internal))
    list_2_plots.append(
        plot_predictions(y, model.fittedvalues, student_residuals))
    
    list_2_plots.append(
        text2html(text=[
                   'Para cada variável dependente, observar se:',
                   '   * p-value < 5%',
                   '   * t-value > 2',
                   'Caso contrário, tente retirar a variável da regressão para melhorar o modelo']
            ))
    
    values = pd.DataFrame([model.pvalues,model.tvalues], index=['p-val', 't-val']).T
    
    values['status'] = np.where((values['p-val'] < 0.05) & (values['t-val'] > 2),
                                'Passed!','A regressão deve melhorar sem essa variável... =/')
    values['p-val'] = values['p-val'].map('{:,.4%}'.format)
    values['t-val'] = values['t-val'].map('{:,.4f}'.format)
    #values['p-val'].style.applymap(lambda val: 'color:red' if val < 0 else 'black'])
    list_2_plots.append(tablePlot(values, index=True))
    
    ## TEST ASSUMPTIONS TO REGRESSION
    # 1)LINEARITY: Harvey-collier multiplier and Rainbow  
    list_2_plots.append(
        text2html('TEST ASSUMPTIONS TO REGRESSION',
                  '1# LINEARITY',
                  ['''This test performs a t-test with parameter degrees of freedom on the recursive residuals. 
                   Recursive residuals are linear transformations of ordinary residuals and are independently
                   and identically distributed. If the true relationship is not linear but convex or concave the mean of 
                   the recursive residuals should differ from zero significantly. A statistically significant result (pvalue>0,05) means
                   that we can reject the null hypothesis of the true model being linear.''']
                  ))
    
    # harvey dá erro se enviar SingularMatrix
    try: list_2_plots.append(plot_harvey(sms.linear_harvey_collier(model).pvalue * 100))
    except: list_2_plots.append(plot_harvey(0))
    #sm.stats.linear_rainbow(model)   # indicate whether the linear fit of the model is adequate even if some underlying relationships are not linear
    
    # Harvey, we will accept linearity if p-value > 5%
    # The Harvey-Collier test performs a t-test (with parameter degrees of freedom) on the recursive residuals. If the true relationship is not linear but convex or concave the mean of the recursive residuals should differ from 0 significantly.
    # HARVEY: indicates whether the residuals are linear
    '''
    print('HARVEY IS HAPPY =D') if sms.linear_harvey_collier(model).pvalue > 0.05 else print('HAVEY IS SAD =/')
    linearity_test = pd.DataFrame([sms.linear_harvey_collier(model).pvalue], 
                     index=['Harvey-collier (residuals teste)'])
    linearity_test.columns = ['p-values']
    linearity_test['p-value %'] = linearity_test.applymap(lambda x: '{0:.4%}'.format(x))
    linearity_test['t-value'] = model.tvalues
    list_2_plots.append(tablePlot(linearity_test, index=True))
    '''
    list_2_plots.append(
        text2html('',
                  '2# NORMALITY',
                  ['Os pontos longe da reta no QQ-plot indicam outliers ou que a regressão não consegue explicá-los muito bem',
                   'No histograma, esperamos ver a bell-curve dos residuais com média 0 e variância 1'])
        )
    
    # 2) NORMALITY: check if residuals are normally distributed
    # Plot residual Q-Q plot
    # Plot Histogram of residuals distribution
    # If the residuals are normally distributed, we should see a bell-shaped histogram centred on 0 and with a variance of 1.
    list_2_plots.append(residuals_histogram(residuals))

    #TODO - STEFANY URGENTE ERRO NA LINHA ACIMA

    # TODO chekcing OMnibus...Bruna entender isso
    #Omnibus is a test of the skewness and kurtosis of the residual. A high value indicates a skewed distribution whereas a low value (close to zero) would indicate a normal distribution
    #The Prob (Omnibus) performs a statistical test indicating the probability that the residuals are normally distributed. We hope to see something close to 1.
    
    list_2_plots.append(
        text2html('',
                  '3# HOMOSCEDASTICITY',
                  ['residuals should be equal for all predicted dependent variables scores',
                   'Breush-Pagan test: measures how errors increase across the explanatory variable',
                   'hight values of Legrange indicates presence of heteroskedasticity (i.e. bad!)'])
        )
    # 3) HOMOSCEDASTICITY: residuals should be equal for all predicted dependent variables scores
    # Breush-Pagan test: measures how errors increase across the explanatory variable        
    names=['Lagrange multiplier statistic', 'p-value','f-value', 'f p-value']
    param=list(sms.het_breuschpagan(model.resid, model.model.exog))      
    # hight values of Legrange indicates presence of heteroskedasticity (i.e. bad!)
    list_2_plots.append(tablePlot(pd.DataFrame(data={'Indicadores':names, 
                                                      'Valores': param})))
    
    # check here if p-value < 5% then Homoscedasticity is FALSE
    #TODO se descobrir range do Lagrange multiplier, colcoar um hodometro Bruna
    
    list_2_plots.append(
        text2html('',
                  '4# INDEPENDENCE',
                  ['Check independence of residuals. The less correleted, the better.'])
        )
    
    # 4) INDEPENDENCE
    # ACF plot - every row should be under the blue box  
    # TODO - ACF plot
    # TODO colocar ACF plot e DurbinWatson lado a lado
    #_ = smt.graphics.plot_acf(model.resid, alpha=0.05)
    
    # TENTANDO JUNTAR ACF COM DURBIN-WATSON


    # Durbin-Watson : check independence of the residuals
        # value = 2 means that there is no autocorrelation in the sample,
        # values < 2 indicate positive autocorrelation,
        # values > 2 negative autocorrelation.
        #The Durbin-Watson statistic will always have a value between 0 and 4. A value of 2.0 means that there is no autocorrelation detected in the sample. Values from 0 to less than 2 indicate positive autocorrelation and values from from 2 to 4 indicate negative autocorrelation.
    print('Durbin-Watson',st.durbin_watson(residuals, axis=0))
    PVALUE = st.durbin_watson(residuals, axis=0)
    #list_2_plots.append(durbin_watson(PVALUE))
    list_2_plots.append(plot_acf_durbin_watson(PVALUE, model.resid, alpha=0.05))
    # If has more then one column, check MULTICOLLINEARITY
    if len(x.columns) > 1:        
        list_2_plots.append(
            text2html('',
                      '5# MULTICOLLINEARITY',
                      ['Variáveis devem ter pouca correlação entre si',
                       'VIF of 5 or 10 and above indicates a multicollinearity problem'])
            )

        # 5) MULTICOLLINEARITY
        # VIF of 5 or 10 and above indicates a multicollinearity problem
        # For each X, calculate VIF and save in dataframe
        
        #A VIF of over 10 for some feature indicates that over 90\% of the variance in that feature is explained by the remaining features. Over 100 indicates over 99\%.
        
        df_vif = pd.DataFrame(index=x.columns)
        df_vif["VIF Factor"] = [variance_inflation_factor(x.values, i) for i in range(x.shape[1])]
        df_vif["VIF Factor"] = df_vif["VIF Factor"].map('{:,.4f}'.format)
        list_2_plots.append(tablePlot(df_vif, index=True))
        
        #another ways is to see teh correlation directly                
        list_2_plots.append(multicollinearity(x.corr()))
        

        # TODO colocar a tabela do VIF ao lado da grafico de multicorrlinear
        # TODO salvar o sns.pairplot como PNG e colcoar ele no HTML
        #sns.pairplot(data =x)  
 
    return list_2_plots
    



    
  