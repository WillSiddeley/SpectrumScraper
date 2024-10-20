from setuptools import setup, find_packages

setup(
    name='spectrum_scraper',
    version='0.1.0',
    description='A Python package to scrape spectrum license data from the Government of Canada website',
    author='WillSiddeley',
    author_email='void.ventures20@gmail.com',
    long_description=open('README.md').read(),
    packages=['spectrum_scraper'],
    package_dir={'spectrum_scraper': 'src'},
    install_requires=[
        'selenium',
        'pandas',
        'docker',
    ],
    entry_points={
        'console_scripts': [
            'spectrum_scraper = spectrum_scraper.main:main',
        ],
    },
)
