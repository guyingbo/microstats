try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os.path
import re
import sys

VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")
BASE_PATH = os.path.dirname(__file__)


with open(os.path.join(BASE_PATH, "microstats.py")) as f:
    try:
        version = VERSION_RE.search(f.read()).group(1)
    except IndexError:
        raise RuntimeError("Unable to determine version.")


with open(os.path.join(BASE_PATH, "README.md")) as readme:
    long_description = readme.read()


ext_modules = None
if (
    not any(arg in sys.argv for arg in ["clean", "check"])
    and "SKIP_CYTHON" not in os.environ
):
    try:
        from Cython.Build import cythonize
    except ImportError:
        pass
    else:
        # For cython test coverage install with `make build-cython-trace`
        compiler_directives = {}
        if "CYTHON_TRACE" in sys.argv:
            compiler_directives["linetrace"] = True
        os.environ["CFLAGS"] = "-O3"
        ext_modules = cythonize(
            "microstats.py",
            nthreads=int(os.getenv("CYTHON_NTHREADS", 0)),
            language_level=3,
            compiler_directives=compiler_directives,
        )

setup(
    name="microstats",
    description="A very simple in-memory statistics module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    version=version,
    author="Yingbo Gu",
    author_email="tensiongyb@gmail.com",
    maintainer="Yingbo Gu",
    maintainer_email="tensiongyb@gmail.com",
    url="https://github.com/guyingbo/microstats",
    py_modules=["microstats"],
    python_requires=">=3.6",
    ext_modules=ext_modules,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "coverage", "pytest-cov"],
)
