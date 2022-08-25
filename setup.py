import setuptools
from stypes.version import get_version

long_description = open("README.md").read()

setuptools.setup(
    name='stypes',
    version=get_version('short'),
    description='Encode and Decode Textual Data into Rich Python Data Structures',
    long_description=long_description,
    long_description_content_type="text/markdown",
    provides=['stypes'],
    packages=['stypes'],
    author="Jeremy Lowery",
    author_email="jeremy@bitrel.com",
    url="http://github.com/jeremylowery/stypes",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Text Processing',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration'
    ],
)
