from setuptools import setup


setup(
    name='systool',
    version='0.03.00',
    license='MIT',
    author="Bruna Calazans (bruna-calazans) & Pedro Chiachio (pcardoso-sk)",
    author_email='pedrochiachioet@gmail.com',
    package_dir={'': 'main'},
    include_package_data=True,
    package_data={'utils': ['charts.py', 'maps.py', 'readWrite.py', 'report.py', 'linear_regression_make.py',
                            'linear_regression_plot.py']},
    url='https://github.com/MoleDownTheHole/SysTool',
    keywords='systool',
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
