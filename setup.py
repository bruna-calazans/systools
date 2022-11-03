from setuptools import setup


setup(
  
    name='systool',
    version='0.05.00',
    license='MIT',
    author="Bruna Calazans (bruna-calazans) & Pedro Chiachio (pcardoso-sk)",
    author_email='bcalazans@systra.com',
    package_dir={'': 'main'},
    include_package_data=True,
    package_data={'utils': ['charts.py', 'flatt_geom.py', 'get_ftp_data.py', 'get_socioEconomic_data.py', 
                            'maps.py', 'readWrite.py', 'report.py', 'linear_regression_make.py',
                            'linear_regression_plot.py', 'miscFunctions']},
    url='https://github.com/bruna-calazans/systools',
    keywords=['systool', 'engenharia', 'transportes', 'systra', 'engenharia de transportes'],
    install_requires=['pytest',
                      'pandas',
                      'numpy',
                      'matplotlib',
                      'matplotlib_scalebar',
                      'geopandas',
                      'openpyxl',
                      'seaborn',
                      'statsmodels',
                      'tqdm',
                      'scipy',
                      'plotly',
                      'shapely'],
)
