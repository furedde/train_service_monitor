import time
import sqlite3

import pytest

from db import StatusDatabase
from train_service_monitor import TrainStatus


class TestStatusDatabase:
    def test_insert_train_status(self):
        db = StatusDatabase(filename=":memory:")
        status_ok = TrainStatus(normal_operations=True,
                                description='Dummy',
                                operator='小田急線')
        status_ng = TrainStatus(normal_operations=True,
                                description='Dummy',
                                operator='Dummy')
        with pytest.raises(sqlite3.Error) as e_info:
            db.insert_train_status(status_ng)
        db.insert_train_status(status_ok)

        assert db.get_latest_train_status(operator=status_ok.operator) == status_ok

    def test_status_history(self):
        db = StatusDatabase(filename=":memory:")
        stats = []
        for i in range(0,5):
            stats.append(TrainStatus(normal_operations=True, description='dummy', operator='小田急線'))
            db.insert_train_status(stats[-1])
            time.sleep(0.001)
        stats.append(TrainStatus(normal_operations=False, description='dummy', operator='小田急線'))
        db.insert_train_status(stats[-1])
        for i in range(0,5):
            stats.append(TrainStatus(normal_operations=False, description='dummy', operator='小田急線'))
            db.insert_train_status(stats[-1])
            time.sleep(0.001)
        stats.append(TrainStatus(normal_operations=True, description='dummy', operator='小田急線'))
        db.insert_train_status(stats[-1])
        # 5 True, 6 False, 1 True

        assert db.get_status_history(operator=stats[0].operator) == stats
        assert db.get_latest_train_status(stats[0].operator) == stats[-1]
        assert db.when_status_changed_to(operator=stats[0].operator,status=True) == stats[-1].timepoint
        assert db.when_status_changed_to(operator=stats[0].operator,status=False) == stats[5].timepoint

    def test__get_operator_key(self):
        db = StatusDatabase(filename=":memory:")
        status_ok = TrainStatus(normal_operations=True,
                                description='Dummy',
                                operator='小田急線')
        assert db._get_operator_key("小田急線") == 1

        with pytest.raises(sqlite3.Error) as e_info:
            db._get_operator_key("Dummy")
