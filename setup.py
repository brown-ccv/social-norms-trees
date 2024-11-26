from setuptools import setup

setup(
    name='behavior tree prototype',                   # Name of your project
    py_modules=['src.social_norms_trees.ui_wrapper'],             # Name of the Python file (without the .py)
    entry_points={
        'console_scripts': [
            'ui-wrapper = ui_wrapper:main',  # Create the 'ui-wrapper' command
        ],
    },
)
