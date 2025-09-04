from neo4j import GraphDatabase
from datetime import date, timedelta
import psycopg2

# PostgreSQL connection parameters
PG_CONFIG = {
    'dbname': "postgres_db",
    'user': "postgres_user",
    'password': "postgres_password",
    'host': "localhost",
    'port': "5430"
}

# Neo4j connection parameters
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "strongpassword"

class SyncService:
    def __init__(self):
        self.pg_conn = psycopg2.connect(**PG_CONFIG)
        self.pg_cur = self.pg_conn.cursor()
        self.neo4j_driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.pg_cur.close()
        self.pg_conn.close()
        self.neo4j_driver.close()

    def sync_universities(self):
        self.pg_cur.execute("SELECT id, name, location FROM University")
        for id, name, location in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MERGE (u:University {id: $id}) "
                    "SET u.name = $name, u.location = $location",
                    id=id, name=name, location=location
                )

    def sync_institutes(self):
        self.pg_cur.execute("SELECT id, name, university_id FROM Institute")
        for id, name, university_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (u:University {id: $uid})"
                    " MERGE (i:Institute {id: $id}) "
                    "SET i.name = $name "
                    "MERGE (u)-[:HAS_INSTITUTE]->(i)",
                    uid=university_id, id=id, name=name
                )

    def sync_departments(self):
        self.pg_cur.execute("SELECT id, name, institute_id FROM Department")
        for id, name, institute_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (i:Institute {id: $iid})"
                    " MERGE (d:Department {id: $id}) "
                    "SET d.name = $name "
                    "MERGE (i)-[:HAS_DEPARTMENT]->(d)",
                    iid=institute_id, id=id, name=name
                )

    def sync_specialties(self):
        self.pg_cur.execute("SELECT id, name, department_id FROM Specialty")
        for id, name, department_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (d:Department {id: $did})"
                    " MERGE (s:Specialty {id: $id}) "
                    "SET s.name = $name "
                    "MERGE (d)-[:HAS_SPECIALTY]->(s)",
                    did=department_id, id=id, name=name
                )

    def sync_groups(self):
        self.pg_cur.execute("SELECT id, name, speciality_id FROM St_group")
        for id, name, speciality_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (s:Specialty {id: $sid})"
                    " MERGE (g:Group {id: $id}) "
                    "SET g.name = $name "
                    "MERGE (s)-[:HAS_GROUP]->(g)",
                    sid=speciality_id, id=id, name=name
                )

    def sync_courses(self):
        self.pg_cur.execute(
            "SELECT id, name, department_id, specialty_id FROM Course_of_lecture"
        )
        for id, name, dept_id, spec_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (d:Department {id: $did}), (s:Specialty {id: $sid})"
                    " MERGE (c:Course {id: $id}) "
                    "SET c.name = $name "
                    "MERGE (d)-[:OFFERS]->(c) "
                    "MERGE (s)-[:INCLUDES_COURSE]->(c)",
                    did=dept_id, sid=spec_id, id=id, name=name
                )

    def sync_lectures(self):
        self.pg_cur.execute("SELECT id, name, course_of_lecture_id FROM Lecture")
        for id, name, course_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (c:Course {id: $cid})"
                    " MERGE (l:Lecture {id: $id}) "
                    "SET l.name = $name "
                    "MERGE (c)-[:HAS_LECTURE]->(l)",
                    cid=course_id, id=id, name=name
                )

    def sync_materials(self):
        self.pg_cur.execute(
            "SELECT id, name, course_of_lecture_id FROM Material_of_lecture"
        )
        for id, name, lecture_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (l:Lecture {id: $lid})"
                    " MERGE (m:Material {id: $id}) "
                    "SET m.name = $name "
                    "MERGE (l)-[:HAS_MATERIAL]->(m)",
                    lid=lecture_id, id=id, name=name
                )

    def sync_schedules(self):
        self.pg_cur.execute(
            "SELECT id, date, lecture_id, group_id FROM Schedule"
        )
        for id, date, lecture_id, group_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (l:Lecture {id: $lid}), (g:Group {id: $gid})"
                    " MERGE (sch:Schedule {id: $id}) "
                    "SET sch.date = $date "
                    "MERGE (l)-[:SCHEDULED_AT]->(sch) "
                    "MERGE (sch)-[:FOR_GROUP]->(g)",
                    lid=lecture_id, gid=group_id,
                    id=id, date=date
                )

    def sync_students(self):
        self.pg_cur.execute(
            "SELECT id, name, age, mail, group_id FROM Students"
        )
        for id, name, age, mail, group_id in self.pg_cur.fetchall():
            with self.neo4j_driver.session() as session:
                session.run(
                    "MATCH (g:Group {id: $gid})"
                    " MERGE (s:Student {id: $id}) "
                    "SET s.name = $name, s.age = $age, s.mail = $mail "
                    "MERGE (g)-[:HAS_STUDENT]->(s)",
                    gid=group_id, id=id, name=name, age=age, mail=mail
                )

    def sync_all(self):
        self.sync_universities()
        self.sync_institutes()
        self.sync_departments()
        self.sync_specialties()
        self.sync_groups()
        self.sync_courses()
        self.sync_lectures()
        self.sync_materials()
        self.sync_schedules()
        self.sync_students()
        print("Successfully synchronized all tables and relations in Neo4j")