rem test include bad scripts but stop on first bad script
ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "." --debug -soe
