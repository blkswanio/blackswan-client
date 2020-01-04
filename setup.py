from setuptools import setup

setup(name='blackswan_client',
      version='0.0.1',
      description='BlackSwan Client',
      author='Jayjeet Chakraborty',
      author_email='jayjeetchakraborty25@gmail.com',
      packages=['blackswan_client'],
      install_requires=[
          'pandas',
          'numpy',
          'influxdb'
      ],
      license='MIT')