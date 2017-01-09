
from distutils.core import setup
from stypes.version import get_version

## broken difference between markdown and rst. These patterns
## blow up python setup.py register
long_description = open("README.md").read()
long_description = long_description.replace('```python', '::')
long_description = long_description.replace('```bash', '::')
long_description = long_description.replace('```', '\n')

setup(
    name='stypes',
    version=get_version('short'),
    description='Encode and Decode Textual Data into Rich Python Data Structures',
    long_description=long_description,
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
