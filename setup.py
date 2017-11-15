from setuptools import setup, find_packages


setup(
    name="sweetest",
    version="0.1.10",
    author="Leo Tong",
    author_email="tonglei@qq.com",
    description="Web UI Autotest with Selenium & Excel",
    long_description=open("README.rst").read(),
    license="Apache License, Version 2.0",
    url="https://github.com/tonglei100/sweetest",
    packages=['sweetest', 'sweetest.sample'],
    package_data={'sweetest': ['*.pyc','sample\sweetest_sample.zip']},
    install_requires=[
        'selenium',
        'xlrd',
        'xlsxwriter'
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6"
    ],
    entry_points={
        'console_scripts': [
            'sweetest=sweetest:sweetest'
        ]
    }
)
