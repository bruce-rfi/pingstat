import ping, sqlite3, time, msvcrt, sys

DB = 'ping.db'
INTERVAL_SECONDS = 1

def create_schema():
	db = sqlite3.connect(DB)
	db.isolation_level = None	# Enable auto-commit
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
	return db

def insert_record(db, rxd, time_ms):
	db.execute('INSERT INTO ping(response, time_ms) VALUES (?, ?)',
		[1 if rxd else 0, time_ms])
	
def output_result(rxd, time_ms):
	if rxd:
		print 'Reply received in %i milliseconds' % time_ms
	else:
		print 'Request timed out'

def output_request(host):
	print 'Pinging %s... ' % host ,

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
	
def ping_loop(host):
	db = create_schema()
	while not msvcrt.kbhit():
		one_ping(db, host)
	db.close()
		
if "__main__" == __name__:
	if len(sys.argv) > 1:
		ping_loop(sys.argv[1])
	else:
		print 'Specify a host on the command line'
