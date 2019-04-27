from flask import Flask, request, render_template, url_for
from sqlalchemy import exists
import os

# ================ USER LIBRARIES =====================
import modals
import barcode_maker

app = Flask(__name__)
db = modals.SqlLitedb()


@app.route("/manager-ui")
def manager_ui():
    return render_template('manager_interface.html')


@app.route("/manager-ui", methods=['POST'])
def enter_master_batch():
    master_batch = request.form["master_batch"]
    batch = request.form["batch"]
    master_batch = "".join(n for n in master_batch if n.isalnum())
    try:
        master_batch = int(master_batch)
        batch = int(batch)
    except:
        return render_template("manager_interface.html")

    Session = db.get_session()

    # check if there's already an entry for the MasterBatch
    master_batch_exists = Session.query(exists().where(modals.MasterBatch.id == master_batch)).scalar()

    if not master_batch_exists:
        master_batch_entry = modals.MasterBatch(id=master_batch, pickerid=0)
        Session.add(master_batch_entry)
        Session.commit()


    #  Definitely need to refactor this. Some garbage code right here for sure
    if "," in batch:
        batch = batch.split(",")
        for code in batch:
            batch_exists = Session.query(exists().where(modals.Batch.id == batch)).scalar()
            if not batch_exists:
                batch_entry = modals.Batch(id=batch, MasterBatch=master_batch)
                Session.add(batch_entry)
                Session.commit()
            else:
                Session.query().filter(modals.Batch.id == batch).update({"MasterBatch": master_batch})
                Session.commit()
    else:
        batch_exists = Session.query(exists().where(modals.Batch.id == batch)).scalar()
        if not batch_exists:
            batch_entry = modals.Batch(id=batch, MasterBatch=master_batch)
            Session.add(batch_entry)
            Session.commit()
        else:
            Session.query().filter(modals.Batch.id == batch).update({"MasterBatch": master_batch})
            Session.commit()
        Session.close()
    return render_template('manager_interface.html')


@app.route("/picker-ui")
def picker_ui():
    return render_template('picker_interface.html')


@app.route("/picker-ui", methods=['POST'])
def get_data():
    picker_name = request.form['picker_name']
    master_batch = request.form['master_batch']
    try:
        _ = int(master_batch)
    except:
        return render_template('picker_interface.html', status="ERROR")
    Session = db.get_session()
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
    Session = db.get_session()
    #  Get unique pickers
    entries = Session.query(modals.Picker.name).distinct()
    pickers = [entry.name for entry in entries]
    Session.commit()
    Session.close()
    #  Pass that array to the HTML to create a drop down menu of pickers
    return render_template("batch_viewer.html", active_pickers=pickers)


@app.route("/batch-viewer", methods=["POST"])
def see_the_batches():
    picker = request.form["picker"]
    Session = db.get_session()
    if picker == "All":
        entries = Session.query(modals.Picker, modals.Batch, modals.MasterBatch)\
                            .filter(modals.MasterBatch.pickerid == modals.Picker.id)\
                            .filter(modals.Batch.MasterBatch == modals.MasterBatch.id)
    else:
        entries = Session.query(modals.Picker, modals.Batch, modals.MasterBatch)\
                            .filter(modals.Picker.name == picker)\
                            .filter(modals.MasterBatch.pickerid == modals.Picker.id)\
                            .filter(modals.Batch.MasterBatch == modals.MasterBatch.id)

    data_arr = []

    for picker_entry, batch, master in entries:
        item = dict()
        item["name"] = picker_entry.name
        item["batch"] = batch.id
        data_arr.append(item)
    entries = Session.query(modals.Picker.name).distinct()
    pickers = [entry.name for entry in entries]
    Session.commit()
    Session.close()
    return render_template("batch_viewer.html", items=data_arr, active_pickers=pickers)


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
    #n = "".join(c for c in n if c.isalnum())
    barcode_maker.gen(n)
    wd = "./static/barcodes/barcodes/"
    barcodes_to_serve = []
    for file in os.listdir(wd):
        barcodes_to_serve.append(wd + file)
    return render_template("barcode_viewer.html", barcodes=barcodes_to_serve)


if __name__ == '__main__':
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.run(debug=True, host="0.0.0.0", port=80)
