from datetime import datetime
from sqlalchemy import exists
import modals

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




if __name__ == "__main__":
    hour = datetime.now().hour
    minute = datetime.now().minute
    h, m = float_to_time(str(time_to_float()))
    assert(h == hour)
    assert(m == minute)
