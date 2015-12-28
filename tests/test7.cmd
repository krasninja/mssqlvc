rem test with ci and record_files_only
ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" --exclude-pattern "^!.*" --stoponerror --record-files-only --case-insensitive --debug
