import sqlite3

# Συνδέσου στη βάση
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Έλεγχος αν υπάρχει ήδη η στήλη
cursor.execute("PRAGMA table_info(checklist);")
columns = [col[1] for col in cursor.fetchall()]

if "pdf_url" not in columns:
    cursor.execute("ALTER TABLE checklist ADD COLUMN pdf_url TEXT;")
    print("✅ Η στήλη 'pdf_url' προστέθηκε επιτυχώς.")
else:
    print("ℹ️ Η στήλη 'pdf_url' υπάρχει ήδη.")

conn.commit()
conn.close()