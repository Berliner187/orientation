from flask import Flask, render_template, Blueprint, request


app = Flask(__name__)
admin_bp = Blueprint('admin', __name__)


@app.route('/')
def index():
    return render_template('index.html')


@admin_bp.route('/admin')
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        event_name = request.form['event_name']
        discipline = request.form['discipline']
        date = request.form['date']
        protocol_link = request.form['protocol_link']
        print("Received event data:")
        print("Event Name:", event_name)
        print("Discipline:", discipline)
        print("Date:", date)
        print("Protocol Link:", protocol_link)
        return "Event data received successfully!"
    return render_template('admin.html')


app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True)
