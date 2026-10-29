import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()
c.execute("SELECT id, email, role FROM users")
print("Users:", c.fetchall())

c.execute("SELECT * FROM athlete_profiles")
print("Athlete Profiles:", c.fetchall())

c.execute("SELECT COUNT(*) FROM physical_assessments")
print("Physical assessments count:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM performance_records")
print("Performance records count:", c.fetchone()[0])

conn.close()
