from setuptools import setup, find_packages

setup(
    name='qypi',
    #version - in setup.cfg
    packages=find_packages(),
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='qypi@varonathe.org',
    keywords='pypi warehouse search packages pip',
    description='Query PyPI from the command line',
    #long_description - in setup.cfg
    url='https://github.com/jwodder/qypi',

    python_requires='~=3.4',
    install_requires=['click~=6.5', 'packaging>=16', 'requests==2.*'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
    ],

    entry_points={
        "console_scripts": [
            'qypi = qypi.__main__:qypi',
        ]
    },
)
