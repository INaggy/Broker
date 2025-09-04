**University Data Management System**
A comprehensive, polyglot persistence system for managing university data with real-time synchronization across multiple databases using Kafka Connect, featuring a microservices architecture with API Gateway.

🏗️ **System Architecture**
This project implements a robust microservices architecture:

**Core Components**
• **API Gateway** (gateway/) - JWT authentication and request routing

• **Lab1 Service** - Attendance reporting with Elasticsearch integration

• **Lab2 Service** - Audience reporting with Neo4j analytics

• **Lab3 Service** - Group reporting with Redis caching

**Database Ecosystem**
• PostgreSQL - Primary transactional database with partitioned attendance data

• MongoDB - Document storage for hierarchical university structure

• Neo4j - Graph database for relationship analysis

• Redis - High-performance cache and search index for students

• Elasticsearch - Full-text search engine for lecture materials

• Kafka Connect - Real-time data synchronization between systems

📊 **Data Model**
**PostgreSQL Schema**
• University → Institute → Department → Specialty → Group → Students

• Course_of_lecture → Lecture → Material_of_lecture

• Schedule with automated semester partitioning

• Attendance with dynamic table partitioning by semester

🚀 **Quick Start**
**Prerequisites**

Docker and Docker Compose
Python 3.8+

**Installation**
1.Clone the repository

```
git clone <https://github.com/INaggy/Project-with-Kafka-connect>
cd Project-with-Kafka-connect
```

2.Start all services

```docker-compose up -d```

3.Initialize the database schema

```python postgres.py```

4.Generate sample data

```python attendance_generator.py```

5.Synchronize data to all systems

```python total_generator.py```

6.Configure Kafka Connect connectors
```
# Debezium PostgreSQL connector
curl -X POST -H "Content-Type: application/json" --data @debezium.json http://localhost:8083/connectors

# Elasticsearch sink connector
curl -X POST -H "Content-Type: application/json" --data @elastic_sink.json http://localhost:8083/connectors

# Neo4j sink connector  
curl -X POST -H "Content-Type: application/json" --data @neo4j_sink.json http://localhost:8083/connectors

# Redis sink connector
curl -X POST -H "Content-Type: application/json" --data @redis_sink.json http://localhost:8083/connectors
```
7.Start the microservices
```
# Each service runs in its own container via docker-compose
docker-compose up gateway lab1 lab2 lab3
```
🔌 **API Endpoints**
**Authentication**
```
curl -X POST http://localhost:1337/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user"}'
```
**Lab1 - Attendance Report**
```
curl -X POST http://localhost:1337/api/lab1/report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"term": "physics", "start_date": "2025-09-01", "end_date": "2025-12-31"}'
```
**Lab2 - Audience Report**
```
curl -X POST http://localhost:1337/api/lab2/audience_report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"year": 2025, "semester": 1}'
```
**Lab3 - Group Report**
```
curl -X POST http://localhost:1337/api/lab3/group_report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"group_id": 1}'
```
🔧 **Kafka Connect Configuration**
The project includes four main connectors:

**1. Debezium PostgreSQL Connector**
• Monitors PostgreSQL changes via logical replication

• Captures CDC (Change Data Capture) events

• Publishes to Kafka topics with table names

**2. Elasticsearch Sink Connector**
• Syncs lecture materials to Elasticsearch

• Enables full-text search capabilities

• Maintains document versioning

**3. Neo4j Sink Connector**
• Creates graph nodes and relationships in Neo4j

• Handles complex relationship mappings

• Uses APOC procedures for advanced operations

**4. Redis Sink Connector**
• Stores student data in Redis for fast access

• Creates hash structures for student records

• Enables quick student lookup and search

🎯 **Sample Data**
The system includes comprehensive sample data for Russian universities:

• 28 Universities - Major Russian educational institutions

• 29 Institutes - Various academic departments

• 28 Departments - Specialized academic units

• 28 Specialties - Academic disciplines and fields

• 28 Student Groups - Organized student cohorts

• 10 Courses - Academic course offerings

• 10 Lectures - Individual lecture sessions

• 10 Materials - Educational resources and materials

🔧 **Configuration**
**Environment Variables**

Gateway Service:

• JWT_SECRET_KEY - Secret for JWT token signing

• LAB1_URL - URL to Lab1 service (default: http://lab1:5001)

• LAB2_URL - URL to Lab2 service (default: http://lab2:5002)

• LAB3_URL - URL to Lab3 service (default: http://lab3:5003)

Database Connections:

• PostgreSQL: localhost:5430 (external), postgres:5432 (internal)

• MongoDB: localhost:27017

• Neo4j: bolt://localhost:7687

• Redis: localhost:6379

• Elasticsearch: localhost:9200

📊 **Report Types**
**1. Attendance Report (Lab1)**
• Finds students with worst attendance for specific lectures
• Combines Elasticsearch search with PostgreSQL attendance data
• Enriches with Redis student information

**2. Audience Report (Lab2)**
• Shows course requirements and student counts per lecture
• Uses Neo4j for relationship traversal
• Filters by academic year and semester

**3. Group Report (Lab3)**
• Tracks planned vs actual attendance hours per student
• Uses PostgreSQL partitioning for performance
• Redis caching for student data

🎯 **Usage Examples**
**Search Students**
```
from redis_module import StudentSearch

searcher = StudentSearch()
students = searcher.search_by_name("Ivanov")
students = searcher.search_by_group("CS-101")
```
**Query Lecture Materials**
```
from Lab1 import LectureMaterialSearcher

searcher = LectureMaterialSearcher()
results = searcher.search("quantum physics")
```
**Generate Reports**
```
from Lab1 import AttendanceFinder

finder = AttendanceFinder()
report = finder.find_worst_attendees(lecture_ids, top_n=10)
```
🐛 **Troubleshooting**
**Common Issues**
1.Connection refused errors
Check all containers are running: docker-compose ps
Verify network connectivity between services
2.Kafka Connect issues
Check connector status: curl http://localhost:8083/connectors
View logs: docker logs kafka-connect
3.Data synchronization problems
Reset databases: python ClearDB_data.py
Repopulate data: python total_generator.py

**Monitoring URLs**
• Kafka UI: http://localhost:8082

• Control Center: http://localhost:9021

• Neo4j Browser: http://localhost:7474 (neo4j/strongpassword)

• Elasticsearch: http://localhost:9200 (elastic/secret)

• Kafka Connect: http://localhost:8083

🔮 **Future Enhancements**
•Real-time attendance monitoring dashboard
•Machine learning for student performance prediction
•Mobile application interface
•Advanced graph analytics
•API rate limiting and monitoring
•Automated testing suite
•Enhanced security features
•Performance optimization

📝 **License**
This project is for educational purposes. Ensure proper licensing for production use.

📧 **Support**
For questions and support, please open an issue in the GitHub repository.

