## Things that I remind myself
### How to recompile locale
```shell
msgfmt -o sltools/locale/uk/LC_MESSAGES/sltools.mo sltools/locale/uk/LC_MESSAGES/sltools.po
```

### How build and to push to PyPI using token
```shell
python3 setup.py sdist 
twine upload dist/* --verbose --username __token__ --password pypi-AgEIcH....L65zvHSDNGBUUziA
```
