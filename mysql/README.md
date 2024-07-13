### To use this script:

Save it as a .sql file (e.g., create_database.sql).
Run it using a MySQL/MariaDB client or command line tool. For example:


```
mysql -u root -p < create_database.sql
```

You'll be prompted to enter the MySQL root password.
Update the config.py file in your application with the correct database name, username, and password:

```
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "your_app_username",
    "password": "your_app_password",
    "port": 3306,
    "database": "students1"
}
```

Remember to replace 'your_app_username' and 'your_app_password' with secure credentials in both the SQL script and the `config.py` file.
This script sets up the necessary database structure for your Certificate Generator Web Application, ensuring that it can store and retrieve student information effectively.