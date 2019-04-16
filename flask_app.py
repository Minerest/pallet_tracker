from flask import Flask, request, render_template

import modals

app = Flask(__name__)

db = modals.SqlLitedb()


@app.route("/test")
def picker_ui():
    return render_template('picker_interface.html')


@app.route("/test", methods=['POST'])
def get_data():
    picker_name = request.form['picker_name']
    master_batch = request.form['master_batch']

    print(picker_name, master_batch)
    return render_template('picker_interface.html')

if __name__ == '__main__':
    app.run(debug=True)