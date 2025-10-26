
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import sqlite3, os, datetime, uuid
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXT = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'sampoorn-secret-key-v4'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    photos = conn.execute('SELECT p.id, p.caption, p.filename, p.timestamp, p.lat, p.lon, p.plants_watered, b.location as bin_location, v.name as vehicle_name FROM photos p LEFT JOIN bins b ON p.bin_id=b.id LEFT JOIN vehicles v ON p.vehicle_id=v.id ORDER BY p.timestamp DESC').fetchall()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    # count today's watered areas
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    watered_count = conn.execute("SELECT COUNT(*) as cnt FROM photos WHERE plants_watered=1 AND DATE(timestamp)=?", (today,)).fetchone()['cnt']
    conn.close()
    return render_template('index.html', photos=photos, bins=bins, watered_count=watered_count,
                           college_name='Geethanjali College of Engineering and Technology', area_name='ECIL Area, Hyderabad')

@app.route('/upload', methods=['GET','POST'])
def upload():
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    conn.close()
    if request.method == 'POST':
        vehicle_id = request.form.get('vehicle_id') or None
        bin_id = request.form.get('bin_id') or None
        caption = request.form.get('caption','').strip()
        lat = request.form.get('lat') or None
        lon = request.form.get('lon') or None
        plants_watered = 1 if request.form.get('plants_watered')=='on' else 0
        file = request.files.get('photo')
        if not file or file.filename == '':
            flash('Please select a photo to upload.', 'danger')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXT:
            flash('Unsupported file type. Use png/jpg/jpeg/gif', 'danger')
            return redirect(request.url)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)
        # store in DB
        conn = get_db_connection()
        conn.execute('INSERT INTO photos (vehicle_id, bin_id, caption, filename, timestamp, lat, lon, plants_watered) VALUES (?,?,?,?,?,?,?,?)',
                     (vehicle_id, bin_id, caption, unique_name, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), lat, lon, plants_watered))
        conn.commit()
        conn.close()
        flash('Photo uploaded successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('upload.html', vehicles=vehicles, bins=bins,
                           college_name='Geethanjali College of Engineering and Technology', area_name='ECIL Area, Hyderabad')

@app.route('/bins')
def bins_list():
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    conn.close()
    return render_template('bins.html', bins=bins,
                           college_name='Geethanjali College of Engineering and Technology', area_name='ECIL Area, Hyderabad')

@app.route('/bins/update', methods=['POST'])
def bins_update():
    bin_id = request.form.get('bin_id')
    level = request.form.get('level')
    conn = get_db_connection()
    conn.execute('UPDATE bins SET level=?, last_update=? WHERE id=?', (level, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), bin_id))
    conn.commit()
    conn.close()
    flash('Bin status updated.', 'info')
    return redirect(url_for('bins_list'))

@app.route('/map')
def map_view():
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    photos = conn.execute('SELECT * FROM photos').fetchall()
    conn.close()
    return render_template('map.html', vehicles=vehicles, bins=bins, photos=photos,
                           college_name='Geethanjali College of Engineering and Technology', area_name='ECIL Area, Hyderabad')

@app.route('/api/markers')
def api_markers():
    conn = get_db_connection()
    bins = conn.execute('SELECT id, location, lat, lon, level FROM bins').fetchall()
    photos = conn.execute('SELECT id, caption, filename, lat, lon, plants_watered FROM photos WHERE lat IS NOT NULL AND lon IS NOT NULL').fetchall()
    conn.close()
    data = {'bins':[dict(b) for b in bins], 'photos':[dict(p) for p in photos]}
    return jsonify(data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        from init_db import init_db
        init_db(DB_PATH)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
