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
--stop-on-error, -soe                                    | stops execution if any script fails
--exclude-pattern EXCLUDE_PATTERN, -ep EXCLUDE_PATTERN   | skips files match to regular expression
--record-files-only, -rfo                                | only file names will be stored to patch table without folder paths
--case-insensitive, -ci                                  | use case insensitive to compare patch files so "PatchName.sql" and "patchname.sql" are the same
--debug                                                  | enables debug output
--version, -v                                            | show program's version

Examples
--------

- `ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "."`
- `ipy ../mssqlvc.py -c "mssql://vctest:vctest@kawin/vctest" -d "." --exclude-pattern "^!.*" -l "log.log" --stop-on-error`

Workflow
--------

Every developer who needs to update the database:

1. Create a migration - a text file within special directory in repository with SQL commands that perform necessary changes. The migration file must be named according to a special naming convention: `yyyyMMdd-username-NNN.sql`. Where `yyyyMMdd` is current date i.e. 20160126, `username` is name of a user created this migration, and `NNN` is ordinal number (i.e. 001, 002, you can reset count every day). The main purpose of such a naming convention is to sort all migration files in chronological order and allow to apply them in order a user created them.

2. Run the created migration on local database to apply it and make sure it is working properly.

3. Continue to work on the code until it is ready to commit. A developer may create as many migrations as he needs in order to finish a task. But he is allowed to commit only when his code in synced with database state.

4. Commit the code along with created migration(-s) into a repository.

Pros
----

- The source code is always synced with database schema state it supports. Every revision in a repository have a database changeset which allows the code to work with database.

- No double waste of time. When a developer changes the database schema he already makes a work to describe these changes through SQL in order to apply it to his local database. Nobody needs to repeat this work nor during development nor during deployment.

- No matter what is the current version of the database schema. Database migrations are incremental and current state of the schema is stored to database, so there is no need to worry about what migrations need to be applied to production or development databases - only unapplied changes will be performed against the database.

- Automated database upgrades. No need to update a database schema manually when you are deploying a new revision. It's possible to automate database update since all the changes are stored into a repository and may be applied all at once by the migration tool.

- Less the risk to break or forget something. Database changes of one developer can be reviewed by others before anything may be broken.

- Safety. If something went wrong, the database will not be corrupted and not be in intermediate state because of SQL Server’s transactional DDL and DML. Each migration is performed within a transaction. No need to change source code in order to support database migration process. The migration tool is external.

Cons
----

- All developers engaged on the project should be familiar with the database migration workflow.

- Sometimes when a developer is using a graphical designer to change the database schema he needs to do additional actions to get corresponding SQL commands for this change.

- No possibility to roll back the migration.

Requirements
------------

- IronPython 2.7+
- Microsoft SQL Shared Management Objects
