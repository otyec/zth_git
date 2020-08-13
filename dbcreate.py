import psycopg2


def create_db(_dbname, _user, _password, _host):
  conn = psycopg2.connect(
    dbname=_dbname,
    user=_user,
    password=_password,
    host=_host
    )
    
  cur = conn.cursor()

  cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'equipment_type') THEN CREATE TYPE equipment_type AS ENUM('cash register', 'oven'); END IF; END $$;")
  #cur.execute("CREATE TYPE equipment_type AS ENUM('cash register', 'oven');")
  conn.commit()
  cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_type') THEN CREATE TYPE job_type AS ENUM('manager', 'cashier', 'cook'); END IF; END $$;")
  # cur.execute("CREATE TYPE job_type AS ENUM('manager', 'cashier', 'cook');")
  conn.commit()

  cur.execute("DROP TABLE IF EXISTS Location CASCADE")
  cur.execute("DROP TABLE IF EXISTS Equipment CASCADE")
  cur.execute("DROP TABLE IF EXISTS Employee CASCADE")

  cur.execute("CREATE TABLE IF NOT EXISTS Location (Id serial PRIMARY KEY, Name VARCHAR NOT NULL, Address VARCHAR NOT NULL);")
  conn.commit()
  cur.execute("CREATE TABLE IF NOT EXISTS Equipment (Id serial PRIMARY KEY, Name VARCHAR, Type equipment_type NOT NULL, LocatedAt INT REFERENCES Location (Id) ON DELETE RESTRICT NOT NULL);")
  conn.commit()
  cur.execute("CREATE TABLE IF NOT EXISTS Employee (Id serial PRIMARY KEY, Name VARCHAR NOT NULL, Job job_type NOT NULL, WorksAt INT REFERENCES Location (Id) ON DELETE RESTRICT NOT NULL, Operates INT REFERENCES Equipment (Id) ON DELETE RESTRICT NOT NULL);")
  conn.commit()
  cur.execute("ALTER TABLE Employee ADD salary int not null")
  conn.commit()
  cur.close()
  conn.close()
