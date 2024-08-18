## Social Norms Trees

### Setup 
1. We will need to setup a virtual enviornment. The following command will create a virtual environment named ".venv" in the current directory.

```
python -m venv .venv
```

2. The following command will activate the newly created Python virtual environment on macOS or Linux.
```
source .venv/bin/activate
```
*After activation, your command prompt will typically change to indicate that you are now working within the virtual environment. You should see a (.venv) at the very beginning.*


3. Now we will install the required dependencies for py trees to run.
```
pip install --editable ".[test]"
```

4. (Temporary) You may need to install the py trees library 
```
pip install py_trees
```

5. Now you can navigate to the file you want to run, and press the triangle play button to run the py_tree file. 

