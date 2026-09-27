from setuptools import Extension, setup

setup(
    name="starkit",
    version="0.0.4",
    description="ROKI leg inverse kinematics, based on starkit 0.0.3 from PyPI",
    author="Babaev Azer Kahraman Ogly",
    maintainer="Алексей Ягубов",
    maintainer_email="alekos.belgorod6@gmail.com",
    url="https://github.com/aleksey-yagubov/starkit",
    license="MIT",
    packages=[],
    ext_modules=[Extension("starkit", ["src/starkit.c"], libraries=["m"])],
    python_requires=">=3.9",
)
