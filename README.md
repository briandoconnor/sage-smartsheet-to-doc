# sage-smartsheet-to-doc
a simple Python script to convert a Smartsheet to a doc

### Environment

```
conda create -n sage-smartsheet-to-doc-env python=3.6
source activate sage-smartsheet-to-doc-env
conda install jupyter
source deactivate
```

### Dependencies

```
pip install -r requirements.txt
```

### Running

You need to make sure you have your Smartsheet token saved as an env var called

    SMARTSHEET_API_TOKEN

You can then run the following (pass in the name of the smartsheet using --sheetname if you don't have
access to my test one).

```
python3 convert.py --pi 'James Eddy' > test.html
```

This will produce an HTML version of the smartsheet filtered by projects that are owned by James

You can then load the test.html in your browser and copy and paste into
a Google doc for sharing/editing by others.

### TODO

* the HTML format is really basic and could be greatly improved with tables/colors 
