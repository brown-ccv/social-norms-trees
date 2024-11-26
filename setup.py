from setuptools import setup

setup(
    name="social-norms-trees",
    py_modules=["ui_wrapper"],
    entry_points={
        "console_scripts": [
            "ui_wrapper=ui_wrapper:main",
        ],
    },
)
