import sqlite3

# Connect to database (or create if not exists)
conn = sqlite3.connect("factory.db")
cursor = conn.cursor()

# Run schema
with open("schema.sql", "r") as f:
    cursor.executescript(f.read())

# Insert some demo machines
machines = [
    ("Packaging Unit", "Running"),
    ("CNC Machine", "Idle"),
    ("Assembly Robot", "Running")
]

cursor.executemany("INSERT INTO machines (name, status) VALUES (?, ?)", machines)

# Insert some demo logs
logs = [
    (1, "Temperature stable at 70°C"),
    (1, "Motor vibration detected"),
    (2, "Idle - awaiting input"),
    (3, "Completed assembly cycle")
]

cursor.executemany("INSERT INTO logs (machine_id, message) VALUES (?, ?)", logs)

conn.commit()
conn.close()

print("Database initialized with sample data ✅")
