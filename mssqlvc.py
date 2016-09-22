# -*- coding: utf-8 -*-
"""
    mssqlvc
    ~~~~~~~

    Database version control utility for Microsoft SQL Server. See README.md for more information.

    Licensed under the BSD license. See LICENSE file in the project root for full license information.
"""

import argparse
import datetime
import io
import logging
import os
import re
import sys
import urlparse

try:
    import clr
except ImportError:
    print('Cannot import crl module, make sure you run this script using IronPython')
    exit(2)
import System

clr.AddReference('Microsoft.SqlServer.Smo')
clr.AddReference('Microsoft.SqlServer.SqlEnum')
clr.AddReference('Microsoft.SqlServer.ConnectionInfo')
import Microsoft.SqlServer.Management.Smo as Smo
import Microsoft.SqlServer.Management.Common as Common

__author__ = 'Ivan Kozhin'
__copyright__ = 'Copyright (c) 2015-2016, Ivan Kozhin'
__license__ = 'BSD'
__version__ = '1.4.3'
__all__ = ['MsSqlVersion']

class ScriptExecutionError(Exception):
    pass

class MsSqlVersion(object):
    """
    SQL Server patch migration class.
    """
    class bcolors:
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'

    def __init__(self, connection_string, patch_dir='.', exclude_pattern=None, logger=None,
        stop_on_error=False, noexecute=False, case_insensitive=False, record_files_only=False):
        """
        Initialize instance with connection and database objects.

        :param connection_string: Connection string in rfc1738 url format
        :param patch_dir: Patch directory with .sql files
        :param exclude_pattern: String with regular expression the patch files should match
        :param logger: Logger that is used for logging
        :param stop_on_error: Stop execution on error, default behavior is to continue
        :param case_insensitive: Use case insensitive to compare patch files
        :param record_files_only: Only file names will be stored to patch table without folder paths
        """
        url = urlparse.urlparse(connection_string)

        is_local_login = not url.username
        self.connection = Common.ServerConnection(LoginSecure=is_local_login, ServerInstance=url.hostname,
            DatabaseName=url.path.replace('/', ''), ConnectTimeout=90)
        if not is_local_login:
            self.connection.Login = url.username
            self.connection.Password = url.password
        self.server = Smo.Server(self.connection)
        self.database = self.server.Databases[self.connection.DatabaseName]
        self.exclude_pattern = exclude_pattern
        self.patch_dir = patch_dir
        self.stop_on_error = stop_on_error
        self.case_insensitive = case_insensitive
        self.record_files_only = record_files_only
        self.executed_count = 0

        self.logger = logging.NullHandler() if not logger else logger

        if not os.path.exists(patch_dir):
            raise Exception('Patch folder does not exist')
        if 'mssql' not in connection_string:
            raise Exception('Wrong connection string, it should contain mssql word')

        exists = self._create_patch_table_if_not_exists(self.database)
        if not exists:
            self.logger.info('[%s] created _patch_history table' % (self.database.Name,))

    def __del__(self):
        if self.server:
            self.server.ConnectionContext.Disconnect()

    def update(self):
        """Executes database update process"""
        patches = self.get_pending_patches()
        self.logger.debug('Files to execute %s' % (patches,))
        for patch in patches:
            success = self.execute_file(patch)
            if success:
                self.executed_count += 1
                self.put_patch(patch)
            if not success and self.stop_on_error:
                self.logger.critical(MsSqlVersion.bcolors.WARNING + 'Execution stopped. Please fix errors and try again.'
                    + MsSqlVersion.bcolors.ENDC)
                raise ScriptExecutionError()
        self.logger.info('[%s] Executed %d patch(-es)' % (self.database.Name, self.executed_count))

    def fill(self):
        """Skip scripts execution but add them to patches table"""
        patches = self.get_pending_patches()
        for patch in patches:
            self.logger.info('Add file %s' % (patch,))
            self.put_patch(patch)

    def get_pending_patches(self):
        applied_patches = self.get_applied_patches()
        if self.record_files_only:
            applied_patches = [os.path.basename(f) for f in applied_patches]
        patches = self._get_sql_files_from_dir(applied_patches)
        patches.sort()
        return patches

    def execute_file(self, file):
        """Executes file against database in transaction, returns True if success"""
        ret = True
        try:
            full_name = os.path.join(os.path.normpath(self.patch_dir), file)
            with io.open(full_name, 'r', encoding='utf8') as sql_file:
                sql = sql_file.read()
                self.logger.info('[%s] Executing %s...' % (self.database.Name, file))
                
                self.connection.BeginTransaction()
                self.database.ExecuteNonQuery(sql)
                self.connection.CommitTransaction()
        except Exception as e:
            self.connection.RollBackTransaction()
            self.logger.error('Exception on %s' % (file,))

            message = e.message or e
            if e.clsException.InnerException is not None and e.clsException.InnerException.InnerException is not None:
                message += ' ' + e.clsException.InnerException.InnerException.Message

            self.logger.error('[%s] %s (%s)' % (self.database.Name, full_name, message))
            ret = False
        return ret

    def put_patch(self, file):
        """Write record that file has been executed"""
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.record_files_only:
            file = os.path.basename(file)
        sql = 'insert [_patch_history] (name, applied_at) values(\'%s\', \'%s\');' % (file, now)
        self.database.ExecuteNonQuery(sql)

    def get_applied_patches(self):
        rows = self.database.ExecuteWithResults('select name from [_patch_history];').Tables[0].Rows
        return set([row['name'] for row in rows])

    def _get_sql_files_from_dir(self, exclude_list=[]):
        """Get all script files from directory"""
        _exclude_list = set(exclude_list) if not self.case_insensitive else [f.lower() for f in exclude_list]
        prevdir = os.getcwd() 
        os.chdir(self.patch_dir)
        sql_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                file = os.path.normpath(os.path.join(root, file))
                _file = file
                if self.case_insensitive:
                    _file = _file.lower()
                if self.record_files_only:
                    _file = os.path.basename(_file)
                if (_file in _exclude_list or not _file.lower().endswith('.sql') or
                    (self.exclude_pattern and re.search(self.exclude_pattern, file))):
                    continue
                sql_files.append(file)
        os.chdir(prevdir)
        return sql_files

    @staticmethod
    def _create_patch_table_if_not_exists(database):
        """Create patch table in database if not exists"""
        sql = 'select * from sys.objects where object_id = object_id(\'_patch_history\') AND type in (\'U\');'
        exists = database.ExecuteWithResults(sql).Tables[0].Rows.Count > 0
        if not exists:
            sql = """
                create table [_patch_history] (id int not null identity(1, 1), name varchar(100) not null,
                    applied_at datetime not null);
                alter table [_patch_history] add constraint _patch_history_PK primary key clustered (id);
                """
            database.ExecuteNonQuery(sql)
        return exists


def get_cmd_line_parser():
    """Get initialized argparse.ArgumentParser object"""
    parser = argparse.ArgumentParser(
        description='MSSQL database patch history tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Example: %(prog)s -c "mssql://sa:123@host\instance/database" -d "D:/1/project/patch"''')
    parser.add_argument('--connection', '-c',
        required=True,
        dest='connection',
        action='store',
        help='connection string in rfc1738 url format, required')
    parser.add_argument('--directory', '-d',
        dest='directory',
        action='store',
        default='.',
        help='directory with patch files')
    parser.add_argument('--log', '-l',
        dest='log',
        action='store',
        help='log file')
    parser.add_argument('--noexecute', '-n',
        action='store_true',
        dest='noexecute',
        default=False,
        help='displays pending script files with no execution')
    parser.add_argument('--noexecute-fill', '-nf',
        action='store_true',
        dest='noexecute_fill',
        default=False,
        help='displays pending script files with no execution and fills patch table')
    parser.add_argument('--stop-on-error', '-soe',
        action='store_true',
        dest='stop_on_error',
        default=False,
        help='stops execution if any script fails')
    parser.add_argument('--exclude-pattern', '-ep',
        dest='exclude_pattern',
        help='skips files match to regular expression')
    parser.add_argument('--record-files-only', '-rfo',
        action='store_true',
        dest='record_files_only',
        default=False,
        help='only file names will be stored to patch table without folder paths')
    parser.add_argument('--case-insensitive', '-ci',
        action='store_true',
        dest='case_insensitive',
        default=False,
        help='use case insensitive to compare patch files so "PatchName.sql" and "patchname.sql" is the same')
    parser.add_argument('--debug',
        action='store_true',
        dest='debug',
        default=False,
        help='enables debug output')
    parser.add_argument('--version', '-v',
        action='version',
        version='%(prog)s ' + __version__)
    return parser


if __name__ == '__main__':
    # parser
    parser = get_cmd_line_parser()
    parser_args = parser.parse_args()
    if parser_args.connection is None or parser_args.directory is None:
        parser.print_help()
        exit(1)

    # logging
    logger = logging.getLogger('mssql')
    if parser_args.log:
        fh = logging.FileHandler(parser_args.log)
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.setLevel(logging.DEBUG if parser_args.debug else logging.INFO)
    logger.addHandler(ch)

    # database handle
    sqlvc = MsSqlVersion(parser_args.connection, parser_args.directory, exclude_pattern=parser_args.exclude_pattern,
       stop_on_error=parser_args.stop_on_error, case_insensitive=parser_args.case_insensitive,
       record_files_only=parser_args.record_files_only, logger=logger)
    if parser_args.noexecute:
        for patch in sqlvc.get_pending_patches():
            logger.info('  ' + patch)
    elif parser_args.noexecute_fill:
        sqlvc.fill()
    else:
        sqlvc.update()