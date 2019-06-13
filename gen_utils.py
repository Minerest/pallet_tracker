from datetime import datetime
from sqlalchemy import exists, and_
import modals
import csv
import calendar # for last day of the month

# My utility library


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


def add_multiple_batch_entries(batch, session, master_batch):

    bulk_entries = []
    batch = batch.split(",")

    for code in batch:
        code = int(code)
        batch_exists = session.query(exists().where(modals.Batch.id == code)).scalar()
        if not batch_exists:
            batch_entry = modals.Batch(id=code, MasterBatch=master_batch, date=datetime.now(),
                                       time=time_to_float())
            bulk_entries.append(batch_entry)
        else:

            batch_row = session.query(modals.Batch).get(code)
            batch_row.MasterBatch = master_batch
            batch_row.date = datetime.now()
            batch_row.time = time_to_float()

    session.bulk_save_objects(bulk_entries)
    session.commit()


def make_csv():
    ''' Gets a list of batches from the data base and creates a csv file for the excel web scraper to read into '''
    today = datetime.now()
    session = modals.db.get_session()
    active_batches = session.query(modals.Batch).filter(modals.Batch.date == datetime.date(today))
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


def import_csv_to_db():
    with open("pd_export.csv") as csv_file:
        reader = csv.reader(csv_file)
        b = True
        entries = []
        for row in reader:
            if b:  # skip header
                b = False
                continue
            entry = process_csv_row(row)
            entries.append(entry)

    session = modals.db.get_session()
    session.bulk_save_objects(entries)
    session.commit()
    session.close()


def process_csv_row(row):
    batch = row[0][-6:-1]
    carton_id = row[1]
    order = row[2][0:7]
    route = process_route(row[3])
    desc = process_desc(row[4])
    sku = row[5]
    status = True if row[6] == "Picked" else False
    user = row[7]
    entry = modals.Dematic(work_id=batch, suborder_id=carton_id, sales_id=order, route=route,
                               desc=desc, sku=sku, status=status, user_id=user)
    return entry


def process_route(r):
    try:
        route = r.split("+")[1]
    except:
        route = ""
    return route


def process_desc(d):
    desc = d.replace("+", " ")
    return desc


if __name__ == "__main__":
    hour = datetime.now().hour
    minute = datetime.now().minute
    h, m = float_to_time(str(time_to_float()))
    assert(h == hour)
    assert(m == minute)
    import_csv_to_db()
