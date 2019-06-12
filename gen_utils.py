from datetime import datetime
from sqlalchemy import exists, and_
import modals
import csv
import calendar # for last day of the month

# utility library to perform calculations


def float_to_time(time_val):
    hour = int(float(time_val))
    time_str = str(time_val)

    try:
        _, mins = time_str.split(".")
        mins = float("." + mins)
        minutes = round(mins * 60)  # the floating point is the percentage of an hour.
    except:
        minutes = 0

    return hour, minutes


def time_to_float():
    hour = datetime.now().hour
    minute = datetime.now().minute
    minute = float(minute/60)
    return hour + minute


def add_multiple_batch_entries(batch, Session, master_batch):

    bulk_entries = []
    batch = batch.split(",")

    for code in batch:
        code = int(code)
        batch_exists = Session.query(exists().where(modals.Batch.id == code)).scalar()
        flag = False
        if not batch_exists:
            batch_entry = modals.Batch(id=code, MasterBatch=master_batch, date=datetime.now(),
                                       time=time_to_float())
            bulk_entries.append(batch_entry)
            flag = True
        else:

            batch_row = Session.query(modals.Batch).get(code)
            batch_row.MasterBatch = master_batch
            batch_row.date = datetime.now()
            batch_row.time = time_to_float()

    Session.bulk_save_objects(bulk_entries)
    Session.commit()


def make_csv():
    ''' Gets a list of batches from the data base and creates a csv file for the excel web scraper to read into '''
    today = datetime.now()
    Session = modals.db.get_session()
    active_batches = Session.query(modals.Batch).filter(modals.Batch.date == datetime.date(today))
    with open('daily_batches.csv', 'w') as batch_file:
        writer = csv.writer(batch_file)
        data = []
        data.append([])
        j = 0
        for i in active_batches:
            data[j].append(i.id)
            j += 1
            data.append([])
        writer.writerows(data)

if __name__ == "__main__":
    hour = datetime.now().hour
    minute = datetime.now().minute
    h, m = float_to_time(str(time_to_float()))
    assert(h == hour)
    assert(m == minute)
    make_csv()
