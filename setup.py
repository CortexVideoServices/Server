from setuptools import setup, find_namespace_packages
import sys

settings = {
    'name': 'CVS',
    'version_config': {
        'version_style': {
            'metadata': True,
            'dirty': True,
        }
    },
    'zip_safe': False,
    'setup_requires': ['setuptools-vcs-version'],
    'packages': find_namespace_packages(),
    'install_requires': [
        'aiohttp==3.7.2',
        'configargparse',
        'SQLAlchemy==1.3.15',
        'psycopg2-binary==2.8.4',
        'aiopg==1.0.0',
        'alembic'
    ]
}

setup(**settings)
