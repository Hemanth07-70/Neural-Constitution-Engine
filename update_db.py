import psycopg2

with open("examples/constitution.yaml") as f:
    content = f.read()

conn = psycopg2.connect("postgresql://nce_user:nce_password@localhost:5434/nce_db")
cur = conn.cursor()
cur.execute("UPDATE constitutions SET yaml_content = %s WHERE active = true;", (content,))
conn.commit()
conn.close()
print("Database updated!")
