import os
import barcode as b
import modals
from barcode.writer import ImageWriter

'''
Control flow for this file

    Someone makes a request to generate a new set of barcodes
    The script will make a database lookup to see the last barcode made [barcodes are made in order]
    it will then generate a file with 10 barcodes to be printed out
    the program will then enter those 10 barcodes into the database
    
'''
db = modals.SqlLitedb()


def gen(n=None):
    def _custom(n):
        if n != "submit":
            n = "$" + n + "$"
        barcode_object = b.get_barcode_class("code128")
        wd = "./static/barcodes/barcodes/"
        barcode = barcode_object(str(n), writer=ImageWriter())
        barcode.save(wd + str(n))
        return

    wd = "./static/barcodes/barcodes/"
    print("DELETING BARCODES")
    for file in os.listdir(wd):
        os.remove(wd + file)
    try:
        n = int(n)
    except:
        _custom(n)
        return
    session = db.get_session()
    amt = n if n else 10
    amt = 20 if amt >= 100 else amt
    last_entry = session.query(modals.MasterBatch).order_by(modals.MasterBatch.id.desc()).first()
    if last_entry is None:
        last_entry = modals.MasterBatch()
        last_entry.id = 99999999
        session.add(last_entry)
        session.commit()
    batches_to_print = [ "$" + str(batch_id) for batch_id in range(last_entry.id + 1, last_entry.id + amt + 1)]
    session.close()

    barcode_object = b.get_barcode_class("code128")

    barcodes_to_print = [barcode_object(str(bcode), writer=ImageWriter()) for bcode in batches_to_print]
    for fname, barcode in zip(batches_to_print, barcodes_to_print):
        barcode.save(wd + str(fname))

