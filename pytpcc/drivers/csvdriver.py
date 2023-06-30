# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# Copyright (C) 2011
# Andy Pavlo
# http://www.cs.brown.edu/~pavlo/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import os
import csv
from datetime import datetime
from pprint import pprint,pformat

from .abstractdriver import *

## ==============================================
## CSVDriver
## ==============================================
class CsvDriver(AbstractDriver):
    DEFAULT_CONFIG = {
        "table_directory": ("The path to the directory to store the table CSV files", "/tmp/tpcc-tables" ),
        "txn_directory": ("The path to the directory to store the txn CSV files", "/tmp/tpcc-txns" ),
    }
    
    def __init__(self, ddl):
        super(CsvDriver, self).__init__("csv", ddl)
        self.denormalize = False
        self.warehouses = 0
        self.read_preference = "primary"
        self.no_transactions = False
        self.batch_writes = True
        self.agg = False
        self.find_and_modify = True
        self.write_concern = 1
        self.causal_consistency = True
        self.all_in_one_txn = True
        self.retry_writes = True
        self.read_concern = 'majority'
        
        self.table_directory = None
        self.table_outputs = { }
        self.txn_directory = None
        self.txn_outputs = { }
        self.txn_params = { }
        
        self.result_doc = {}
    ## DEF
    
    def makeDefaultConfig(self):
        return CsvDriver.DEFAULT_CONFIG
    ## DEF
    
    def loadConfig(self, config):
        for key in list(CsvDriver.DEFAULT_CONFIG.keys()):
            assert key in config, "Missing parameter '%s' in %s configuration" % (key, self.name)
        
        self.table_directory = config["table_directory"]
        assert self.table_directory
        if not os.path.exists(self.table_directory): os.makedirs(self.table_directory)
        
        self.txn_directory = config["txn_directory"]
        assert self.txn_directory
        if not os.path.exists(self.txn_directory): os.makedirs(self.txn_directory)
    ## DEF
    
    def loadTuples(self, tableName, tuples):
        if not tableName in self.table_outputs:
            path = os.path.join(self.table_directory, "%s.csv" % tableName)
            self.table_outputs[tableName] = csv.writer(open(path, 'w'), quoting=csv.QUOTE_ALL)
        ## IF
        self.table_outputs[tableName].writerows(tuples)
    ## DEF
    
    def executeTransaction(self, txn, params):
        if not txn in self.txn_outputs:
            path = os.path.join(self.txn_directory, "%s.csv" % txn)
            self.txn_outputs[txn] = csv.writer(open(path, 'w'), quoting=csv.QUOTE_ALL)
            self.txn_params[txn] = list(params.keys())[:]
            self.txn_outputs[txn].writerow(["Timestamp"] + self.txn_params[txn])
        ## IF
        row = [datetime.now()] + [params[k] for k in self.txn_params[txn]]
        self.txn_outputs[txn].writerow(row)
    ## DEF
    
    def save_result(self, result_doc):
        self.result_doc.update(result_doc)
        #self.result_doc['after']=self.get_server_status()
        # saving test results and server statuses ('before' and 'after') into MongoDB as a single document
        #self.client.test.results.insert_one(self.result_doc)
        
## CLASS

        
