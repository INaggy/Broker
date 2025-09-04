import json
import psycopg2
import psycopg2.errors
from datetime import datetime, timedelta
import random
import logging
from faker import Faker

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация group_to_lecture_mapping
group_to_lecture_mapping = {}

# Инициализация Faker
fake = Faker("ru_RU")
Faker.seed(42)

# Загрузка конфигурации
try:
    logger.info("Попытка открыть config/data_config.json")
    with open('config/data_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Ошибка загрузки конфигурации: {e}")
    raise

universities = config['universities']
institutes = config['institutes']
departments = config['departments']
courses = config['courses']
specialties = config['specialties']
lectures = config['lectures']
groups = config['groups']
materials = config['materials']
logger.info(f"Количество университетов: {len(universities)}")
for u in universities:
    logger.debug(f"Университет: name={u['name']}, location={u['location']}")

# Параметры подключения к PostgreSQL
DB_NAME = "postgres_db"
DB_USER = "postgres_user"
DB_PASSWORD = "postgres_password"
DB_HOST = "localhost"
DB_PORT = "5430"

def generate_students_and_attendance(cur, students_per_group=20):
    logger.info("Начало генерации студентов и посещаемости")
    cur.execute("SELECT id FROM St_group;")
    group_ids = [row[0] for row in cur.fetchall()][:32]
    logger.info(f"Найдено {len(group_ids)} групп")

    for group_id in group_ids:
        cur.execute("""
            SELECT id, date, lecture_id, CASE
                WHEN EXTRACT(MONTH FROM date) BETWEEN 1 AND 6
                    THEN (EXTRACT(YEAR FROM date)::INT || '_spring')
                ELSE (EXTRACT(YEAR FROM date)::INT || '_fall')
            END AS semester
            FROM Schedule
            WHERE group_id = %s
            ORDER BY date
        """, (group_id,))
        sessions = cur.fetchall()
        logger.info(f"Группа {group_id}: найдено {len(sessions)} сессий")
        if not sessions:
            logger.warning(f"Пропускаем группу {group_id}: нет записей в Schedule")
            continue

        if len(sessions) < students_per_group + 1:
            needed = students_per_group + 1 - len(sessions)
            last_date = sessions[-1][1]
            existing_lects = [s[2] for s in sessions]
            for i in range(needed):
                new_date = last_date + timedelta(days=i+1)
                lec_id = random.choice(existing_lects)
                cur.execute(
                    """
                    INSERT INTO Schedule (date, lecture_id, group_id)
                    VALUES (%s, %s, %s)
                    RETURNING id,
                              CASE
                                WHEN EXTRACT(MONTH FROM date) BETWEEN 1 AND 6
                                  THEN (EXTRACT(YEAR FROM date)::INT || '_spring')
                                ELSE (EXTRACT(YEAR FROM date)::INT || '_fall')
                              END
                    """,
                    (new_date, lec_id, group_id)
                )
                try:
                    new_id, new_sem = cur.fetchone()
                    sessions.append((new_id, new_date, lec_id, new_sem))
                    logger.info(f"Добавлена сессия для группы {group_id}: ID {new_id}")
                except psycopg2.ProgrammingError as e:
                    logger.error(f"Ошибка при добавлении сессии для группы {group_id}: {e}")
                    raise

        sid_to_sem = {sid: sem for sid, _, _, sem in sessions}
        for sem in set(sid_to_sem.values()):
            cur.execute("SELECT ensure_attendance_partition(%s);", (sem,))

        total = len(sessions)
        sched_ids = [s[0] for s in sessions]
        attend_counts = random.sample(range(1, total), students_per_group)

        for count in attend_counts:
            name = f"stud{random.randint(10000, 99999)}"
            age = random.randint(17, 24)
            mail = f"{name}@university.example"
            cur.execute(
                """
                INSERT INTO Students (name, age, mail, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (name, age, mail, group_id)
            )
            student_id = cur.fetchone()[0]
            logger.info(f"Создан студент ID {student_id} для группы {group_id}")

            visited = set(random.sample(sched_ids, k=count))
            for sid in sched_ids:
                attended = sid in visited
                sem = sid_to_sem[sid]
                cur.execute(
                    """
                    INSERT INTO Attendance (student_id, schedule_id, attended, semester)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (student_id, sid, attended, sem)
                )

    logger.info("Генерация студентов и посещаемости завершена")

def main(cur):
    try:
        logger.info("Начало вставки данных")
        # Вставка университетов
        logger.info("Вставка университетов")
        if not universities:
            logger.error("Список университетов пуст!")
            raise ValueError("Конфигурация не содержит университетов")
        # Проверяем существующие университеты
        cur.execute("SELECT name FROM University")
        existing_names = {row[0] for row in cur.fetchall()}
        logger.info(f"Найдено {len(existing_names)} существующих университетов")
        new_universities = [(u['name'], u['location']) for u in universities if u['name'] not in existing_names]
        logger.info(f"Подготовлено {len(new_universities)} новых университетов для вставки")
        if not new_universities:
            logger.info("Все университеты уже существуют, используем существующие ID")
            cur.execute("SELECT id, name FROM University")
            university_ids = [row[0] for row in cur.fetchall() if row[1] in {u['name'] for u in universities}]
            logger.info(f"Используется {len(university_ids)} существующих ID университетов")
        else:
            try:
                cur.executemany(
                    "INSERT INTO University (name, location) VALUES (%s, %s) RETURNING id",
                    new_universities
                )
                rows = cur.fetchall()
                if not rows:
                    logger.error("Вставка университетов не вернула строк!")
                    raise RuntimeError("Не удалось вставить университеты")
                university_ids = [row[0] for row in rows]
                logger.info(f"Вставлено {len(university_ids)} новых университетов")
            except psycopg2.Error as e:
                logger.error(f"Ошибка PostgreSQL при вставке университетов: {e}")
                raise

        # Вставка институтов
        cur.executemany(
            "INSERT INTO Institute (name, university_id) VALUES (%s, %s) RETURNING id",
            [(i['name'], i['university_id']) for i in institutes]
        )
        institute_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(institute_ids)} институтов")

        # Вставка кафедр
        cur.executemany(
            "INSERT INTO Department (name, institute_id) VALUES (%s, %s) RETURNING id",
            [(d['name'], d['institute_id']) for d in departments]
        )
        department_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(department_ids)} кафедр")

        # Вставка специальностей
        cur.executemany(
            "INSERT INTO Specialty (name, department_id) VALUES (%s, %s) RETURNING id",
            [(s['name'], s['department_id']) for s in specialties]
        )
        specialty_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(specialty_ids)} специальностей")

        # Вставка групп
        cur.executemany(
            "INSERT INTO St_group (name, speciality_id) VALUES (%s, %s) RETURNING id",
            [(g['name'], g['specialty_id']) for g in groups]
        )
        group_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(group_ids)} групп")

        # Вставка курсов лекций
        cur.executemany(
            "INSERT INTO Course_of_lecture (name, department_id, specialty_id) VALUES (%s, %s, %s) RETURNING id",
            [(c['name'], c['department_id'], c['specialty_id']) for c in courses]
        )
        course_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(course_ids)} курсов")

        # Вставка лекций
        cur.executemany(
            "INSERT INTO Lecture (name, course_of_lecture_id) VALUES (%s, %s) RETURNING id",
            [(l['name'], l['course_id']) for l in lectures]
        )
        lecture_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(lecture_ids)} лекций")

        # Вставка материалов лекций
        cur.executemany(
            "INSERT INTO Material_of_lecture (name, course_of_lecture_id) VALUES (%s, %s) RETURNING id",
            [(m['name'], m['lecture_id']) for m in materials]
        )
        material_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(material_ids)} материалов")

        # Генерация расписания
        schedules = []
        start_date = datetime(2023, 9, 1)
        for _ in range(200):
            lecture_id = random.choice(lecture_ids)
            group_id = random.choice(group_ids)
            date = start_date + timedelta(days=random.randint(0, 180))
            schedules.append((date, lecture_id, group_id))
        cur.executemany(
            "INSERT INTO Schedule (date, lecture_id, group_id) VALUES (%s, %s, %s) RETURNING id",
            schedules
        )
        schedule_ids = [row[0] for row in cur.fetchall()]
        logger.info(f"Вставлено {len(schedule_ids)} записей расписания")

        # Генерация студентов и посещаемости
        generate_students_and_attendance(cur, students_per_group=20)

        # Создание словаря group_to_lecture_mapping
        global group_to_lecture_mapping
        group_to_lecture_mapping = {}
        for group_id in group_ids:
            cur.execute(
                "SELECT lecture_id FROM Schedule WHERE group_id = %s",
                (group_id,)
            )
            lecture_ids = [row[0] for row in cur.fetchall()]
            group_to_lecture_mapping[group_id] = lecture_ids
        logger.info("Создан group_to_lecture_mapping")

        logger.info("Тестовые данные успешно сгенерированы")
    except Exception as e:
        logger.error(f"Ошибка при генерации данных: {e}")
        raise

if __name__ == "__main__":
    logger.info("Запуск генерации тестовых данных")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = False
    cur = conn.cursor()
    try:
        main(cur)
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    print("group_to_lecture_mapping:", group_to_lecture_mapping)