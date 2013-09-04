
from distutils.core import setup
from stypes.version import get_version

long_description = open("README.md").read()

setup(
    name='stypes',
    version=get_version('short'),
    description='rich type library for textual data records',
    long_description=long_description,
    provides=['stypes'],
    packages=['stypes'],
    author="Jeremy Lowery",
    author_email="jeremy@bitrel.com",
    url="http://github.com/jeremylowery/stypes",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration'
    ],
)
