rem test with ci and record_files_only
ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" --exclude-pattern "^!.*" --stop-on-error --record-files-only --case-insensitive --debug
