from flask import Flask, request, render_template
from sqlalchemy import exists
from datetime import datetime
import os

# ================ USER LIBRARIES ===================== #
import modals
import barcode_maker
import gen_utils

app = Flask(__name__)



@app.route("/manager-ui")
def manager_ui():
    return render_template('manager_interface.html')


@app.route("/manager-ui", methods=['POST'])
def enter_master_batch():
    master_batch = request.form["master_batch"]
    batch = request.form["batch"]
    master_batch = "".join(n for n in master_batch if n.isnumeric())
    try:
        master_batch = int(master_batch)
    except:
        return render_template("manager_interface.html")

    Session = modals.db.get_session()

    # check if there's already an entry for the MasterBatch
    master_batch_exists = Session.query(exists().where(modals.MasterBatch.id == master_batch)).scalar()

    if not master_batch_exists:
        master_batch_entry = modals.MasterBatch(id=master_batch, pickerid=0, date=datetime.now(),
                                                time=gen_utils.time_to_float())
        Session.add(master_batch_entry)
        Session.commit()


    if "," in batch:
        gen_utils.add_multiple_batch_entries(batch, Session, master_batch)
    else:
        batch_exists = Session.query(exists().where(modals.Batch.id == batch)).scalar()
        if not batch_exists:
            batch_entry = modals.Batch(id=batch, MasterBatch=master_batch,
                                       date=datetime.now(), time=gen_utils.time_to_float())
            Session.add(batch_entry)
            Session.commit()
        else:
            Session.query().filter(modals.Batch.id == batch).update({"MasterBatch": master_batch,
                                                                     "date": datetime.now(),
                                                                     "time": gen_utils.time_to_float()})
            Session.commit()

        Session.close()
    return render_template('manager_interface.html', success=True)


@app.route("/picker-ui")
def picker_ui():
    return render_template('picker_interface.html')


@app.route("/picker-ui", methods=['POST'])
def get_data():
    picker_name = request.form['picker_name']
    master_batch = request.form['master_batch']
    try:
        assert(master_batch[0] == "$")
        assert(picker_name[0] == "$")
        assert(picker_name[-1] == "$")
        picker_name = picker_name.strip("$")
        master_batch = master_batch.strip("$")
        _ = int(master_batch)

    except:
        return render_template('picker_interface.html', status="ERROR")
    Session = modals.db.get_session()
    master_batch_exists = Session.query(exists().where(modals.MasterBatch.id == master_batch)).scalar()

    if not master_batch_exists:
        Session.close()
        return render_template('picker_interface.html', status='manager')

    picker_exists = Session.query(exists().where(modals.Picker.name == picker_name)).scalar()
    if not picker_exists:
        picker_entry = modals.Picker(name=picker_name)
        Session.add(picker_entry)
        Session.commit()
    else:
        picker_entry = Session.query(modals.Picker).filter(modals.Picker.name == picker_name).one()

    master_batch_entry = Session.query(modals.MasterBatch).filter(modals.MasterBatch.id == master_batch).one()

    master_batch_entry.pickerid = picker_entry.id
    Session.commit()
    Session.close()
    return render_template('picker_interface.html', status="OK")


@app.route("/batch-viewer")
def get_active_pickers():
    Session = modals.db.get_session()
    #  Get unique pickers
    entries = Session.query(modals.Picker.name).distinct()
    pickers = [entry.name for entry in entries]
    Session.commit()
    Session.close()
    #  Pass that array to the HTML to create a drop down menu of pickers

    offset = dict()
    offset["offset"] = 0
    offset["limit"] = 1

    return render_template("batch_viewer.html", active_pickers=pickers, offset=offset)


@app.route("/batch-viewer", methods=["POST"])
def see_the_batches():
    offset = dict()
    picker = request.form["picker"]
    offset["offset"] = request.form["offset"]
    offset["limit"] = 1
    Session = modals.db.get_session()
    if picker == "All":
        entries = Session.query(modals.Picker, modals.Batch, modals.MasterBatch)\
                            .filter(modals.MasterBatch.pickerid == modals.Picker.id)\
                            .filter(modals.Batch.MasterBatch == modals.MasterBatch.id)\
                            .order_by(modals.Batch.date.desc(), modals.Batch.time.desc())\
                            .limit(500)

    else:
        entries = Session.query(modals.Picker, modals.Batch, modals.MasterBatch)\
                            .filter(modals.Picker.name == picker)\
                            .filter(modals.MasterBatch.pickerid == modals.Picker.id)\
                            .filter(modals.Batch.MasterBatch == modals.MasterBatch.id) \
                            .order_by(modals.Batch.date.desc(), modals.Batch.time.desc())\
                            .limit(500)
    table_items = []

    for picker_entry, batch, master in entries:
        item = dict()
        item["name"] = picker_entry.name
        item["batch"] = batch.id
        item["date"] = master.date
        hour, minute = gen_utils.float_to_time(master.time)
        item["time"] = str(hour) + ":" + str(minute)
        table_items.append(item)

    entries = Session.query(modals.Picker.name).distinct()
    pickers = [entry.name for entry in entries]
    Session.commit()
    Session.close()
    return render_template("batch_viewer.html", items=table_items, active_pickers=pickers, offset=offset)


@app.route("/drop_station", methods=["POST"])
def add_to_drop_station():

    Session = modals.db.get_session()

    dropstation = dict()
    picker = request.form["picker"]
    picker_id = Session.query(modals.Picker.id)\
                       .filter(modals.Picker.name == picker).one()
    dropstation["station"] = request.form["station"]
    dropstation["date"] = datetime.now()
    dropstation["time"] = gen_utils.time_to_float()
    dropstation["picker_id"] = picker_id.id

    db_entry = modals.DropStation(pickerid=dropstation["picker_id"], date=dropstation["date"],
                                  time=dropstation["time"], station=dropstation["station"])
    Session.add(db_entry)
    Session.commit()
    Session.close()
    return ""

@app.route('/')
@app.route('/<variable>')
def get_index(variable=None):
    return render_template("index.html")


@app.route("/display_barcodes")
def display_barcodes():
    wd = "./static/barcodes/barcodes/"
    barcodes_to_serve = []
    for file in os.listdir(wd):
        barcodes_to_serve.append(wd + file)

    return render_template("barcode_viewer.html", barcodes=barcodes_to_serve)


@app.route("/display_barcodes", methods=["POST"])
def gen_barcodes():

    n = request.form["n"]
    if n == "":
        return render_template("barcode_viewer.html")
    barcode_maker.gen(n)
    return render_template("barcode_viewer.html")


@app.route("/barcodes")
def read_barcodes():
    wd = "./static/barcodes/barcodes/"
    barcodes_to_serve = []
    for file in os.listdir(wd):
        barcodes_to_serve.append(wd + file)
    return render_template("barcodes.html", barcodes=barcodes_to_serve)


if __name__ == '__main__':
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.run(debug=True, host="0.0.0.0", port=80)
