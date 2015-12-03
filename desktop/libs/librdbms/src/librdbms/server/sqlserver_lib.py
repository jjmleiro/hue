#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

try:
    import pymssql as Database
except ImportError, e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading SQL Server module: %s" % e)

from librdbms.server.rdbms_base_lib import BaseRDBMSDataTable, BaseRDBMSResult, BaseRDMSClient


LOG = logging.getLogger(__name__)


class DataTable(BaseRDBMSDataTable): pass


class Result(BaseRDBMSResult): pass


class SQLServerClient(BaseRDMSClient):
  """Same API as Beeswax"""

  data_table_cls = DataTable
  result_cls = Result

  def __init__(self, *args, **kwargs):
    super(SQLServerClient, self).__init__(*args, **kwargs)
    self.connection = Database.connect(**self._conn_params)

  @property
  def _conn_params(self):
    params = {
      'user': self.query_server['username'],
      'password': self.query_server['password'],
      'server': self.query_server['server_host'],
      'database': self.query_server['name']
    }

    if self.query_server['options']:
      params.update(self.query_server['options'])

    return params

  def use(self, database):    
    pass

  def execute_statement(self, statement):
    cursor = self.connection.cursor()
    cursor.execute(statement)
    
    if cursor.description:
      columns = [column[0] for column in cursor.description]
    else:
      columns = []
    return self.data_table_cls(cursor, columns)

  def get_databases(self):
    return [self._conn_params['database']]

  def get_tables(self, database, table_names=[]):
    # Doesn't use database and only retrieves tables for database currently in use.    
    cursor = self.connection.cursor()    
    cursor.execute("SELECT table_name FROM %s.information_schema.tables" % database)
    return [row[0] for row in cursor.fetchall()]

  def get_columns(self, database, table):
    cursor = self.connection.cursor()    
    cursor.execute("SELECT column_name FROM %s.information_schema.columns WHERE table_name = '%s'" % (database, table))
    
    return [row[0] for row in cursor.fetchall()]
