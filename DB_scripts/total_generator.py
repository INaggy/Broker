import attendance_generator as attendance_generator
import mongo_sync as mongo_sync
import neo4j_sync as neo4j_sync
import redis_sync as redis_sync
import elastic_gen_sync as elastic_gen_sync

import psycopg2


DB_NAME = "postgres_db"
DB_USER = "postgres_user"
DB_PASSWORD = "postgres_password"
DB_HOST = "localhost"
DB_PORT = "5430"

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()


PG_CONFIG = {
    'dbname': "postgres_db",
    'user': "postgres_user",
    'password': "postgres_password",
    'host': 'localhost',
    'port': 5430,
}

NEO4J_URI = 'bolt://localhost:7687'
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'strongpassword'




if __name__ == "__main__":
    attendance_generator.generate_students_and_attendance(cur, students_per_group=20)
    conn.commit()
    service = neo4j_sync.SyncService()
    service.sync_all()
    mongo_sync.sync_postgres_to_mongo()
    redis_sync.sync_students_to_redis()
    elastic_gen_sync.generate_and_sync_lecture_materials()
