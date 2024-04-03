import os.path
import sqlite3
import dateutil
from typing import Optional, Tuple
import datetime
from dateutil.parser import parse

class TrainStatus:
    def __init__(self, operator: str, normal_operations: bool, description='',
                 timepoint: Optional[datetime.datetime] = None):
        self.operator = operator
        self.normal_operations = normal_operations
        self.description = description
        self.timepoint = timepoint if timepoint is not None else datetime.datetime.now()

    def __str__(self):
        return f"Operator {self.operator} : {'OK' if self.normal_operations else 'Delay'} ({self.description})"

    def __repr__(self):
        return f"TrainStatus(operatior='{self.operator}', normal_operations='{self.normal_operations}', " \
               f"description='{self.description}', timepoint={self.timepoint}"

    def __eq__(self, other):
        if isinstance(other, TrainStatus):
            return self.operator == other.operator and self.normal_operations == other.normal_operations and self.timepoint == other.timepoint and self.description == other.description
        return False

class StatusDatabase:

    def __init__(self, filename=':memory:'):
        if not os.path.exists(filename):
            self._connection = sqlite3.connect(filename)
            self._create_database()
        else:
            self._connection = sqlite3.connect(filename)

        self._connection.row_factory = sqlite3.Row

    def insert_train_status(self, status: TrainStatus):
        operator = self._get_operator_key(status.operator)
        params = (status.timepoint, operator, status.description, status.normal_operations)
        self._connection.execute("INSERT INTO operation_status(timepoint, operator, description, operation_status) VALUES(?,?,?,?)",params)
        self._connection.commit()
    def _get_operator_key(self, operator_name) -> int:
        res = self._connection.execute("SELECT key FROM operators WHERE name = ?", (operator_name,))
        keys = res.fetchone()
        if keys:
            return keys[0]
        else:
            raise sqlite3.Error(f"{operator_name} is not a valid operator")

    def _create_database(self):
        cur = self._connection.cursor()

        res = cur.execute("SELECT name FROM sqlite_master")
        if res.fetchone() is None or 'operators' not in res:
            cur.execute('CREATE TABLE operators(key INTEGER PRIMARY KEY , name UNIQUE)')
            # populate operators we care about
            params = [("小田急線",),("相鉄線",),("千代田線",)]
            for param in params:
               cur.execute("INSERT INTO operators(name) VALUES(?)",param)

        if res.fetchone() is None or 'operation_status' not in res:
            cur.execute('CREATE TABLE operation_status('
                        'key INT PRIMARY KEY,'
                        'timepoint, '
                        'operator INT REFERENCES operators(key),'
                        'description,'
                        'operation_status INT)')

        self._connection.commit()

    def get_latest_train_status(self, operator:str) -> Optional[TrainStatus]:
        cur = self._connection.execute('SELECT s.*,o.name '
                                       'FROM operation_status s, operators as o '
                                       'WHERE s.operator = o.key AND o.name = ? '
                                       'ORDER BY timepoint DESC '
                                       'LIMIT 1',(operator,))
        result = cur.fetchone()
        if result:
            return self._row_to_trainstatus(result)

    def _row_to_trainstatus(self, result: Tuple):
        """We expect to get a tuple with all columns from operation_status and the operator name at the end"""
        return TrainStatus(operator=result['name'],
                           normal_operations=True if result['operation_status'] else False,
                           description=result['description'],
                           timepoint=parse(result['timepoint'])
                           )

    def get_status_history(self, operator):
        cur = self._connection.execute('SELECT s.*,o.name '
                                       'FROM operation_status s, operators as o '
                                       'WHERE s.operator = o.key AND o.name = ? '
                                       'ORDER BY timepoint ASC ',(operator,))
        return [self._row_to_trainstatus(r) for r in cur.fetchall()]

    def when_status_changed_to(self, operator:str, status:bool) -> Optional[TrainStatus]:
        """
        Returns the TrainStatus (including its timepoint) for when the status changed to <status>
        for the given operator
        """
        stats = self.get_status_history(operator)
        timepoint = None
        for index,s in enumerate(stats):
            if index == 0:
                # skip first record as there is nothing we can do here
                continue
            if s.normal_operations == status and stats[index-1].normal_operations != status:
                timepoint = s.timepoint

        return timepoint


if __name__ == '__main__':
    StatusDatabase()
