from setuptools import setup, find_packages


setup(
    name='sysgadgets',
    version='0.0.10.6',
    license='MIT',
    author="Bruna Calazans & Pedro Chiacchio",
    author_email='pcardoso@systra.com',
    packages=find_packages('main'),
    package_dir={'': 'main'},
    url='https://github.com/bruna-calazans/sysgadgets',
    keywords='sysgadgets',
    install_requires=[
          'pytest',
          'pandas',
          'geopandas',
          'openpyxl'
      ],

)
