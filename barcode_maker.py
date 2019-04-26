import os
import barcode as b
import modals

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
        barcode_object = b.get_barcode_class("code128")
        wd = "./static/barcodes/barcodes/"
        barcode = barcode_object(str(n))
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
    amt = 20 if amt >= 100 else amt #  Playing around with ternary operators. Prefer the C++ version for sure
    last_entry = session.query(modals.MasterBatch).order_by(modals.MasterBatch.id.desc()).first()
    print("last entry", last_entry.id)
    batches_to_print = [batch_id for batch_id in range(last_entry.id + 1, last_entry.id + amt + 1)]
    print("GENERATING BARCODES")
    print("Batches to print", batches_to_print)
    session.close()

    barcode_object = b.get_barcode_class("code128")

    barcodes_to_print = [barcode_object(str(bcode)) for bcode in batches_to_print]
    for fname, barcode in zip(batches_to_print, barcodes_to_print):
        barcode.save(wd + str(fname))

