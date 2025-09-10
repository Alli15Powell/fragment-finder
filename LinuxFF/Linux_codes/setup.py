from setuptools import setup
from Cython.Build import cythonize
#import numpy

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

setup(
    ext_modules=cythonize("Procedure.pyx", annotate = True)
)