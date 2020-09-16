from setuptools import setup

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Operating System :: OS Independent'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

description = "Test Runner"

setup(
    name='tunner',
    version='0.2.1',
    packages=['tunner'],
    package_data={
        "tunner": ["configuration/*.json"],
    },
    url='https://github.com/ShadowCodeCz/tunner',
    project_urls={
        'Source': 'https://github.com/ShadowCodeCz/tunner',
        'Tracker': 'https://github.com/ShadowCodeCz/tunner/issues',
    },
    author='ShadowCodeCz',
    author_email='shadow.code.cz@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=classifiers,
    keywords='test runner',
    install_requires=[]
)
