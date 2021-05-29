import os

from setuptools import setup, find_packages


def package_files(*dirs):
    paths = []
    for d in dirs:
        for (path, directories, filenames) in os.walk(d):
            for filename in filenames:
                paths.append(os.path.join('..', path, filename))
    return paths


setup_deps = [
                 'wheel',
                 'twine'
             ],
setup(name='kcapi',
      version='0.0.1',
      description='KC Processor',
      long_description='',
      long_description_content_type="text/markdown",
      classifiers=[],
      url='',
      maintainer='Danimae Vossen',
      maintainer_email='vossen.dm@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'pyyaml',
          'schema',
          'requests',
          'python-dateutil',
          'kucoin-python'
      ],
      extras_require={
          'setup': setup_deps,
      },
      setup_requires=setup_deps,
      )
