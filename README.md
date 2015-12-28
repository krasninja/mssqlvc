Microsoft SQL Version Control
=============================

Overview
--------

The script allows to apply patches to SQL Server database using plain sql files. Every developer creates sql files to apply to database in special folder. To execute scripts in the order everybody should follow special naming convention with dates include. For example.

```
D:\1\mssqlvc\tests>dir /B
201512114_User_001.sql
201512114_User_002.sql
201512114_User_003.sql
```

The script creates special table `_patch_history` in database that contains all scripts that has been already executed against database. So it walks from file to file, executes and puts to `_patch_history` table. Every file executes in transaction.

The script also allows to filter by regular expression and stop on first exception.

Parameters
----------

Name                                                     | Description
----                                                     | -----------
--connection CONNECTION, -c CONNECTION                   | connection string in rfc1738 url format, required
--directory DIRECTORY, -d DIRECTORY                      | directory with patch files
--log LOG, -l LOG                                        | log file
--noexecute, -n                                          | displays pending script files with no execution
--noexecute-fill, -nf                                    | displays pending script files with no execution and fills patch table
--stoponerror, -soe                                      | stops execution if any script fails
--exclude-pattern EXCLUDE_PATTERN, -ep EXCLUDE_PATTERN   | skips files match to regular expression
--record-files-only, -rfi                                | only file names will be stored to patch table without folder paths
--case_insensitive, -ci                                  | use case insensitive to compare patch files so "PatchName.sql" and "patchname.sql" is the same
--debug                                                  | enables debug output
--version, -v                                            | show program's version

Examples
--------

- `ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "."`
- `ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "." --exclude-pattern "^!.*" -l "log.log" --stoponerror`

Requirements
------------

- IronPython 2.7+
- Microsoft SQL Shared Management Objects
