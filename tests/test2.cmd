rem test exclude bad scripts
ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "." --exclude-pattern "^!.*" -l "log.log" --stoponerror --debug