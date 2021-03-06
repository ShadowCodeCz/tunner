from setuptools import setup, find_packages

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
    version='0.3.2',
    packages=find_packages(),
    # TODO: fix
    package_data={
        "tunner": ['*', '*/*', '*/*/*', '*/*/*/*'],
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
    install_requires=["alphabetic-timestamp", "Pillow", "generic_design_patterns", "yapsy"],
    entry_points={
        'console_scripts': [
            'tunner=tunner.panel_app:run',
        ]
    }
)
