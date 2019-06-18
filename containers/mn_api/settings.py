import os

if os.environ.get("DB_LOCATION") == 'DEVELOPMENT':
    DB_DEF = dict(
        host='localhost',
        user='postgres',
        password='postgres',
        database='dash_mns',
            port=5432
    )
else:
    DB_DEF = dict(
    host='localhost',
    user='postgres',
    password='postgres',
    database='dash_mns',
        port=5432
    )