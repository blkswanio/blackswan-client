from setuptools import setup

setup(name='baseliner-py',
      version='0.0.1',
      description='Baseliner Client',
      author='Jayjeet Chakraborty',
      author_email='jayjeetchakraborty25@gmail.com',
      packages=['baseliner'],
      install_requires=[
          'pandas',
          'numpy',
          'influxdb'
      ],
      license='MIT')