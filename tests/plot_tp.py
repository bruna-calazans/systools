def hist_tp():
    import os
    import pandas as pd
    from systool import plot

    file_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(file_path, r'test_databases\test_plot.csv'), encoding='latin1', sep=';')
    df = pd.pivot_table(df, values='Nº_boletim', index='tipo_logradouro', aggfunc='count')
    fig = plot.hist(df['Nº_boletim'], title='Número de Acidentes de Tráfego em Belo Horizonte',
                    subtitle='Por Tipo de Logradouro', legenda='Qtd. Acidentes',
                    xlabel='Analized Intervals', source='BhTrans',
                    comentario='Dados retirados do serviços de dados abertos da BhTrans',
                    bins=4, lwl=0, upl=200, report_nan=True)
    fig.savefig(r'test_databases\plot_tp.png')
    
    assert os.path.exists(r'test_databases\plot_tp.png')
