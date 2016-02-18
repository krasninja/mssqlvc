rem test with absolute path and exclude bad scripts
ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "D:\1\mssqlvc\tests" --exclude-pattern "^!.*" --stop-on-error --debug
