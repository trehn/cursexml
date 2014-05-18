from setuptools import setup

setup(
    name='cursexml',
    version="0.1.0",
    author="Torsten Rehn",
    author_email="torsten@rehn.email",
    license="GPLv3",
    url="http://github.com/trehn/cursexml",
    py_modules=['cursexml'],
    entry_points={
        'console_scripts':
        ['cursexml = cursexml:main'],
    },
    long_description=open('README.md').read(),
    keywords=["XML", "viewer", "syntax", "pretty"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Markup :: XML",
    ],
)
