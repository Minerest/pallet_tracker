from flask import Flask, request, render_template
from sqlalchemy import exists
from datetime import datetime
import os

# ================ USER LIBRARIES ===================== #
import modals # database stuff
import barcode_maker # wraper for the py-barcode library
import gen_utils # general utilities

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
    offset["limit"] = 10

    return render_template("batch_viewer.html", active_pickers=pickers, offset=offset)


@app.route("/batch-viewer", methods=["POST"])
def see_the_batches():
    offset = dict()
    picker = request.form["picker"]
    Session = modals.db.get_session()
    offset["offset"] = request.form["offset"]
    offset["limit"] = 10
    if picker == "All":
        entries = Session.query(modals.MasterBatch, modals.Batch, modals.Picker, modals.DropStation) \
                         .outerjoin(modals.DropStation, modals.DropStation.pickerid == modals.Picker.id)\
                         .filter(modals.MasterBatch.pickerid == modals.Picker.id,
                                 modals.Batch.MasterBatch == modals.MasterBatch.id)\
                            .order_by(modals.Batch.date.desc(), modals.Batch.time.desc())\
                            .limit(offset["limit"])\
                            .offset(offset["offset"])

        offset["length"] = Session.query(modals.Picker, modals.Batch, modals.MasterBatch)\
                                  .filter(modals.MasterBatch.pickerid == modals.Picker.id,
                                          modals.Batch.MasterBatch == modals.MasterBatch.id).count()

    else:
        entries = Session.query(modals.MasterBatch, modals.Batch, modals.Picker, modals.DropStation) \
                         .outerjoin(modals.DropStation, modals.DropStation.pickerid == modals.Picker.id) \
                         .filter(modals.Picker.name == picker)\
                         .filter(modals.MasterBatch.pickerid == modals.Picker.id)\
                         .filter(modals.Batch.MasterBatch == modals.MasterBatch.id) \
                         .order_by(modals.Batch.date.desc(), modals.Batch.time.desc())\
                         .limit(offset["limit"])\
                         .offset(offset["offset"])

        offset["length"] = Session.query(modals.Picker, modals.Batch, modals.MasterBatch)\
                                  .filter(modals.Picker.name == picker)\
                                  .filter(modals.MasterBatch.pickerid == modals.Picker.id)\
                                  .filter(modals.Batch.MasterBatch == modals.MasterBatch.id).count()
    table_items = []

    for entry in entries:
        # entry[0] = masterbatch; entry[1] = batch; entry[2] = picker; entry[3] = dropstation
        item = dict()
        item["name"] = entry[2].name
        item["batch"] = entry[1].id
        item["date"] = entry[0].date
        hour, minute = gen_utils.float_to_time(entry[3].time if entry[3] else entry[1].time)
        item["time"] = str(hour) + ":" + str(minute)
        item["drop"] = entry[3].station if entry[3] else "Currently Picking"
        if entry[3]:
            item["drop"] = entry[3].station
        elif item["name"] == "Not Assigned":
            item["drop"] = ""
        else:
            item["drop"] = "Currently Picking"

        table_items.append(item)

    entries = Session.query(modals.Picker.name).distinct()
    pickers = [entry.name for entry in entries]
    Session.commit()
    Session.close()
    return render_template("batch_viewer.html", items=table_items, active_pickers=pickers, offset=offset)


@app.route("/cartons")
def display_the_cartons():

    batch = request.args.get("batch", None)
    if not batch:
        return render_template("batch_viewer.html")
    session = modals.db.get_session()
    entries = session.query(modals.Dematic).filter(modals.Dematic.work_id == batch)\
        .order_by(modals.Dematic.sales_id.desc())

    items = []
    for entry in entries:
        item = entry.__dict__
        items.append(item)
    session.close()
    return render_template("cartons.html", items=items)

@app.route("/drop_station", methods=["POST"])
def add_to_drop_station():

    Session = modals.db.get_session()

    dropstation = dict()
    picker = request.form["picker"]
    picker = picker.strip("$")
    try:
        picker_id = Session.query(modals.Picker.id)\
                       .filter(modals.Picker.name == picker).one()
    except:
        return "Error with the picker"
    dropstation["station"] = request.form["station"]
    dropstation["masterid"] = request.form["masterid"]
    dropstation["date"] = datetime.now()
    dropstation["time"] = gen_utils.time_to_float()
    dropstation["pickerid"] = picker_id.id
    dropstation["masterid"] = dropstation["masterid"].strip("$")

    b = Session.query(modals.MasterBatch).filter(modals.MasterBatch.id == dropstation["masterid"]).scalar()

    if not b:
        return "Error with the master batch"

    entry_exists = bool(Session.query(modals.DropStation)\
        .filter(modals.DropStation.masterid == dropstation["masterid"]).first())
    if entry_exists:
        dropstation["station"] += " OR "
        item = Session.query(modals.DropStation) \
            .filter(modals.DropStation.masterid == dropstation["masterid"]).first()
        s = dropstation["station"] + item.station
        Session.query(modals.DropStation) \
                .filter(modals.DropStation.masterid == dropstation["masterid"]).update({
                                                                                        "station": s,
                                                                                        "time": dropstation["time"]})

    else:
        db_entry = modals.DropStation(pickerid=dropstation["pickerid"], date=dropstation["date"],
                                      time=dropstation["time"], station=dropstation["station"],
                                      masterid=dropstation["masterid"])
        Session.add(db_entry)

    Session.commit()
    Session.close()
    return ""


@app.route("/drop")
def drop_test():
    return render_template("drop_station.html")

@app.route('/')
@app.route('/<variable>')
def get_index(variable=None):
    return render_template("index.html")


@app.route("/display_barcodes")
def display_barcodes():

    return render_template("barcode_viewer.html")


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


@app.route("/locations")
def get_batches_in_dropstation():
    try:
        batch = request.args["batch"]
    except:
        return render_template("locations.html", location=None, picker=None)

    Session = modals.db.get_session()

    try:
        batch_entry = Session.query(modals.Batch).filter(modals.Batch.id == batch).one()
    except:
        Session.close()
        return render_template("locations.html", location=None, picker=None)

    try:
        locations = Session.query(modals.DropStation).filter(modals.DropStation.masterid == batch_entry.MasterBatch)
    except:
        locations = None

    master_entry = Session.query(modals.MasterBatch).filter(modals.MasterBatch.id == batch_entry.MasterBatch).one()
    picker = Session.query(modals.Picker).filter(modals.Picker.id == master_entry.pickerid).one()

    Session.close()
    arr = [loc.__dict__ for loc in locations]

    for item in arr:
        hr, min = gen_utils.float_to_time(item["time"])
        item["time"] = str(hr) + ":" + str(min)

    pd = picker.__dict__
    return render_template("locations.html", locations=arr, picker=pd)


if __name__ == '__main__':
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.run(debug=True, host="0.0.0.0", port=80)
