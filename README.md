# Kafka with connectors project
Для начала нужно создать окружение :
python -m venv base
Затем установить зависимости:
pip install -r requirements.txt
После чего переходя в дирректории сервисов прописывать для каждого:
cd project_services
cd lab1_service
docker build -t lab1_app .
cd ..
cd lab2_service
docker build -t lab2_app .
cd ..
cd lab3_service
docker build -t lab3_app .
cd ..
cd gateway
docker build -t gateway_app .
Затем делаем докер компоуз:
docker compose up -d
И запускаем создание базы данных в PostgreSQL

