import psycopg2

def get_conn():
    return psycopg2.connect(
        host="localhost",
        database="newbacktest",
        user="postgres",
        password="300812"
    )

def save_strategy(name, config):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            name TEXT PRIMARY KEY,
            config TEXT
        )
    """)
    cur.execute("""
        INSERT INTO strategies (name, config)
        VALUES (%s, %s)
        ON CONFLICT (name) DO UPDATE SET config = EXCLUDED.config
    """, (name, config))
    conn.commit()
    cur.close()
    conn.close()

def get_strategy(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT config FROM strategies WHERE name = %s", (name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None 