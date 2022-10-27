def fitmodel_tp():

    import os
    import numpy as np
    import pandas as pd
    import main.systool.linreg as lr

    file_path = os.path.dirname(os.path.abspath(__file__))

    x = np.array([value for value in range(0, 11)])
    y = x * 2
    x[5] = 3
    y[5] = 200
    x = pd.Series(x)
    y = pd.Series(y)
    x.name = 'x'
    y.name = 'y'
    m1, m2 = lr.fit_model(x, y, plot=True, path=os.path.join(file_path, r'test_outputs'))

    assert 2 <= m1.params[0] <= 4
    assert 1.9 <= m2.params[0] <= 2
    assert os.path.exists(rf'test_outputs\regModel_y=x_intercepNO_ZN11.html')


def loopmodels_tp():

    import os
    import main.systool.linreg as lr
    import main.systool.data as data

    file_path = os.path.dirname(os.path.abspath(__file__))
    df_trip = data.open_file(os.path.join(file_path, r'test_databases\test_loop_models.xlsx'),
                             kwargs={'sheet_name': 'VIAGENS'})
    df_data = data.open_file(os.path.join(file_path, r'test_databases\test_loop_models.xlsx'),
                             kwargs={'sheet_name': 'DADOS'})
    df = df_trip.merge(df_data.rename(columns={'ZONAS': 'ZONA'}), how='outer')
    df_regs = lr.loop_models(df, xcols=['POP', 'DOMICILIOS', 'PEA'], ycol='PROD', mask=None, keep_all=False,
                             cut_r=0.5, force_intercept=False)

    reg_columns = ['x', 'Rsquared', 'intercept', 'covType', 'ZONAS', 'PASS_TESTS',
                   'NUM_COEF_NEGATIVO', 'DURBIN_WATSON', 'HARVEY_COLLIER', 'MEAN_KDE',
                   'STD_KDE', 'numXvars', 'numZones']

    for column in df_regs.columns:
        assert column in reg_columns

    assert df_regs.shape[0] > 0

    for index, row in df_regs.iterrows():
        assert row['Rsquared'] > 0.5
