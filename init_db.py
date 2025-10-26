
import sqlite3, os, datetime
def init_db(path='database.db'):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    # vehicles table
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY,
        name TEXT,
        driver TEXT,
        status TEXT,
        lat REAL,
        lon REAL,
        last_update TEXT
    )''')
    # bins table
    c.execute('''CREATE TABLE IF NOT EXISTS bins (
        id INTEGER PRIMARY KEY,
        location TEXT,
        lat REAL,
        lon REAL,
        level TEXT,
        last_update TEXT
    )''')
    # photos table with plants_watered field
    c.execute('''CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY,
        vehicle_id INTEGER,
        bin_id INTEGER,
        caption TEXT,
        filename TEXT,
        timestamp TEXT,
        lat REAL,
        lon REAL,
        plants_watered INTEGER DEFAULT 0,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
        FOREIGN KEY(bin_id) REFERENCES bins(id)
    )''')
    # seed sample vehicles and data
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO vehicles (name, driver, status, lat, lon, last_update) VALUES (?,?,?,?,?,?)",
              ('Truck-01','Siva','Cleaning',17.4667,78.5800, now))
    c.execute("INSERT INTO vehicles (name, driver, status, lat, lon, last_update) VALUES (?,?,?,?,?,?)",
              ('Truck-02','Lakshmi','Idle',17.4700,78.5860, now))
    c.execute("INSERT INTO bins (location,lat,lon,level,last_update) VALUES (?,?,?,?,?)",
              ('Near Main Gate - GCET',17.4765,78.5610,'Half', now))
    c.execute("INSERT INTO bins (location,lat,lon,level,last_update) VALUES (?,?,?,?,?)",
              ('ECIL Roadside - Sector 5',17.4800,78.5870,'Full', now))
    c.execute("INSERT INTO bins (location,lat,lon,level,last_update) VALUES (?,?,?,?,?)",
              ('Bus Stop - Near GCET',17.4750,78.5630,'Empty', now))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db(os.path.join(os.path.dirname(__file__), 'database.db'))
    print('Initialized database at database.db')
