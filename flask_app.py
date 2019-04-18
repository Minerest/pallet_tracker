from flask import Flask, request, render_template
from sqlalchemy import exists, update

import modals

app = Flask(__name__)

db = modals.SqlLitedb()



@app.route("/manager-ui")
def manager_ui():
    return render_template('manager_interface.html')

@app.route("/manager-ui", methods=['POST'])
def enter_master_batch():
    master_batch = request.form["master_batch"]
    batch = request.form["batch"]
    Session = db.get_session()

    # check if there's already an entry for the MasterBatch
    master_batch_exists = Session.query(exists().where(modals.MasterBatch.id == master_batch)).scalar()

    if not master_batch_exists:
        master_batch_entry = modals.MasterBatch(id=master_batch, pickerid=0)
        Session.add(master_batch_entry)
        Session.commit()

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
    Session = db.get_session()
    master_batch_exists = Session.query(exists().where(modals.MasterBatch.id == master_batch)).scalar()

    if not master_batch_exists:
        return render_template('picker_interface.html', error='manager')

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
    Session.flush()
    Session.close()
    return render_template('picker_interface.html', status="OK")


@app.route("/batch-viewer")
def get_active_pickers():
    Session = db.get_session()
    entries = Session.query(modals.Picker.name).distinct()
    pickers = []

    for entry in entries:
        pickers.append(entry.name)
    Session.commit()
    Session.close()
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
    pickers = []
    for entry in entries:
        pickers.append(entry.name)
    Session.commit()
    Session.close()
    return render_template("batch_viewer.html", items=data_arr, active_pickers=pickers)

@app.route('/')
@app.route('/<variable>')
def get_index(variable=None):
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
