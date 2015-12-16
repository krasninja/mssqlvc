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

Examples
--------

- `ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "."`
- `ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "." --exclude-pattern "^!.*" -l "log.log" --stoponerror`

Requirements
------------

- IronPython 2.7+
- Microsoft SQL Shared Management Objects
