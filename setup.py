from setuptools import setup


setup(
  
    name='systool',
    version='0.6.4',
    license='MIT',
    description='Set of high level funcions that optimize our work as transport planners',
    author="Bruna Calazans (bruna-calazans) & Pedro Chiachio (pcardoso-sk)",
    author_email='bcalazans@systra.com',
    package_dir={'': 'main'},
    include_package_data=True,
    packages=['systool','systool.utils'],
    #package_data={'utils': ['charts.py', 'flatt_geom.py', 'get_ftp_data.py', 'get_socioEconomic_data.py', 
    #                        'maps.py', 'readWrite.py', 'report.py', 'linear_regression_make.py',
    #                        'linear_regression_plot.py', 'miscFunctions']},
    url='https://github.com/bruna-calazans/systools',
    keywords=['systool', 'engenharia', 'transportes', 'systra', 'engenharia de transportes'],
    install_requires=['pytest==7.2.2',
                      'pandas==1.5.3',
                      'numpy==1.24.2',
                      'matplotlib==3.7.1',
                      'matplotlib-scalebar==0.8.1',
                      'pyqt5==5.15.7',
                      'geopandas==0.12.2',
                      'openpyxl==3.1.2',
                      'seaborn==0.12.2',
                      'statsmodels==0.13.5',
                      'tqdm==4.65.0',
                      'scipy==1.10.1',
                      'plotly==5.13.1',
                      'shapely==2.0.1'],
)
