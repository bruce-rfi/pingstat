import ping, sqlite3, time, msvcrt, sys

DB = 'ping.db'
INTERVAL_SECONDS = 1

# Create the database schema including table and views.
# Return the database connection.
def create_schema():
    db = sqlite3.connect(DB)
    db.isolation_level = None    # Enable auto-commit
    db.execute("DROP TABLE IF EXISTS ping")
    db.execute("""
        CREATE TABLE ping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response INTEGER NOT NULL,
            time_ms INTEGER
            CHECK (response BETWEEN 0 AND 1)
        )
        """)
    db.execute("""
        CREATE VIEW IF NOT EXISTS hourly
        AS SELECT
            SUBSTR(DATETIME(timestamp, 'localtime'), 0, 14) || ":00" AS hour,
            SUM(response) AS rsp_recvd,
            COUNT(id) AS sent
        FROM ping
        GROUP BY hour
        ORDER BY hour
        """)
    db.execute("""
        CREATE VIEW IF NOT EXISTS plr_percent
        AS SELECT
            hour,
            100 * (sent - rsp_recvd) / sent AS plr
        FROM hourly;
        """)
    db.execute("""
        CREATE VIEW IF NOT EXISTS plr_chart
        AS SELECT
            hour,
            SUBSTR("%s", 0, plr)
        FROM plr_percent;
        """ % ("*" * 100))
    return db

# Insert a single log record into the database.
def insert_record(db, rxd, time_ms):
    db.execute('INSERT INTO ping(response, time_ms) VALUES (?, ?)',
        [1 if rxd else 0, time_ms])

# Output the result of a single ping to the console.
def output_result(rxd, time_ms):
    if rxd:
        print 'Reply received in %i milliseconds' % time_ms
    else:
        print 'Request timed out'

# Output a single ping request to the console.
def output_request(host):
    print 'Pinging %s... ' % host ,

# Perform a single ping request.
def one_ping(db, host):
    output_request(host)
    t = ping.do_one(host, INTERVAL_SECONDS, 32)
    rxd = (None != t)
    t_ms = int(t * 1000) if rxd else None
    insert_record(db, rxd, t_ms)
    output_result(rxd, t_ms)
    if rxd:
        t_wait = INTERVAL_SECONDS - t
        if t_wait > 0:
            time.sleep(t_wait)

# Ping specified host until a key is pressed on the console.
def ping_loop(host):
    db = create_schema()
    while not msvcrt.kbhit():
        one_ping(db, host)
    db.close()

# Command line argument processing
if "__main__" == __name__:
    if len(sys.argv) > 1:
        ping_loop(sys.argv[1])
    else:
        print 'Specify a host on the command line'
