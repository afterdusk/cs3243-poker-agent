from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        [
            Extension("*", ["*.py"]),
            Extension("syncengine.*", ["syncengine/*.py"]),
            Extension("pypokerengine.*", ["pypokerengine/*.py"]),
            Extension("pypokerengine.api.*", ["pypokerengine/api/*.py"]),
            Extension("pypokerengine.engine.*", ["pypokerengine/engine/*.py"]),
            Extension("pypokerengine.utils.*", ["pypokerengine/utils/*.py"]),
        ],
        build_dir="build",
        compiler_directives=dict(
            always_allow_keywords=True
        )
    )
)

