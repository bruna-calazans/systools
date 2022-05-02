from setuptools import setup, find_packages


setup(
    name='SysTool',
    version='0.0.10',
    license='MIT',
    author="Bruna Calazans & Pedro Chiacchio",
    author_email='pcardoso@systra.com',
    packages=find_packages('systool'),
    package_dir={'': 'systool'},
    url='https://github.com/bruna-calazans/SysTool',
    keywords='systool',
    install_requires=[
          'pytest',
          'pandas',
          'geopandas',
          'openpyxl'
      ],

)
