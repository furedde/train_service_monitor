import argparse
import requests as requests
from db import StatusDatabase
import monitors


parser = argparse.ArgumentParser(prog='Train Monitor',
                                 description='Checks registered train services and alert if their status changed.')
parser.add_argument('--db',help='path to sqlite db file, or :memory: for in memory db',default='db.sqlite')
parser.add_argument('--ntfy',help='https://ntfy.s notification name', default='')
parser.add_argument('--status',help='Always notify clients about the current status',action='store_true',default=False)

args = parser.parse_args()
db = StatusDatabase(filename=args.db)

if __name__ == '__main__':
    changed_status = []
    for monitor in monitors.MONITORS:
        latest_status = db.get_latest_train_status(monitor.operator())
        status = monitor.get_status()
        db.insert_train_status(status)

        if latest_status is None or latest_status.normal_operations != status.normal_operations:
            changed_status.append(status)

    if args.ntfy:
        message = ""
        if args.status:
            message = f"Status overview:\n"
            for monitor in monitors.MONITORS:
                status = db.get_latest_train_status(monitor.operator())
                message += f"{monitor.operator()} {'is ok.' if status.normal_operations else f'have delays ({status.description}).'}\n"
        elif changed_status:
            message = f"Operations with changed states:\n"
            for status in changed_status:
                message += f"{monitor.operator()} {'is ok.' if status.normal_operations else f'have delays ({status.description}).'}\n"

        if message:
            print(f"Clients notified with below message.")
            print(message)
            requests.post(f'https://ntfy.sh/{args.ntfy}',data=message.encode('utf-8'))

    else:
        message = f"Operations with changed states:"
        for status in changed_status:
            message += f"{monitor.operator()} {'is ok.' if status.normal_operations else f'have delays ({status.description}).'}\n"
        print(message)