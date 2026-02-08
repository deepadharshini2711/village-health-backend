import sqlite3

# Connect to database
conn = sqlite3.connect("village_health.db")
cursor = conn.cursor()

# Check Volunteers
cursor.execute("SELECT * FROM volunteers")
volunteers = cursor.fetchall()
print("Volunteers:", volunteers)

# Check Patients
cursor.execute("SELECT * FROM patients")
patients = cursor.fetchall()
print("Patients:", patients)

# Check Pharmacies
cursor.execute("SELECT * FROM pharmacies")
pharmacies = cursor.fetchall()
print("Pharmacies:", pharmacies)

# Close connection
conn.close()