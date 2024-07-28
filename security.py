import pickle
import re
from typing import Optional
import os
from pathlib import Path
import bcrypt
import mysql
from mysql.connector import Error
import pyodbc

class StreamlitAuthObject():

    def __init__(self) -> None:
        self.authpath = os.path.join(Path(__file__).parent, 'authobjectpickle.pkl')
        if not os.path.exists(self.authpath):
            config = {
                'credentials':{
                    'usernames':{
                        'admin':{
                            'email': 'admin@mail.in',
                            'name': 'admin',
                            'password': 'admin123',
                            'role': 'admin',
                            'state':1
                        },
                        'second_admin':{
                            'email':'secadmin@mail.in',
                            'name': 'secadmin',
                            'password': 'secadmin123',
                            'role':'translator',
                            'state':1
                        }
                    },
                    'cookie':{
                        'expiry_days': 1,
                        'key': 'mycookiekeyisveryrandom',
                        'name': 'authcookieadmin'
                    }
                }
            }
            nameList = [name for name in config['credentials']['usernames'].keys()]
            self.authobject = {
                'config': config,
                'nameList':nameList
            }

            with open('authobjectpickle.pkl', 'wb') as cookie:
                pickle.dump(obj=self.authobject, file=cookie)
        else:
            with open(self.authpath, 'rb') as authobj:
                self.authobject = pickle.load(authobj) 
            print("Default auth object loaded.")
        
    
    def get_auth(self):
        return self.authobject

    def adduser(self, username:str, email: Optional[str] = "", name: Optional[str] = "", password:str = "abc123", role: str = 'translator', status: int = 1):
        try:
            if username not in self.authobject['nameList']:
                if re.match(pattern='[\w*]@[\w*].[\w]', string=email):
                    self.authobject['config']['credentials']['usernames'][username] = {'email':email, 'name':name, 'password':password, 'role':role, 'status':status}
                    self.authobject['nameList'].append(username)
                    with open('authobjectpickle.pkl', 'wb') as cookie:
                        pickle.dump(obj=self.authobject, file=cookie)
                    return {'message':f"User {username} added to auth object"}
                else:
                    return {'message':f"Incorrect email format"}
            else:
                return {'message':f"User {username} already exists"}
        except Exception as e:
            return {"Error": f"{e}"}

    def delete_user(self, username:str):
        try:
            if username in self.authobject['nameList']:
                self.authobject['config']['credentials']['usernames'].pop(username)
                self.authobject['nameList'].pop(username)
                with open('authobjectpickle.pkl', 'wb') as cookie:
                    pickle.dump(obj=self.authobject, file=cookie)
                return {"object": username, 'message': f"{username} removed from auth object"}
            else:
                return {'message': f'User {username} does not exist'}
        except Exception as e:
            return {'Error': f"{e}"}
        
    def persist_auth_object(self):
        with open('authobjectpickle.pkl', 'wb') as cookie:
            pickle.dump(obj=self.authobject, file=cookie)
        return {'message':'Auth object updated'}
    
    def list_users(self):
        return self.authobject['nameList']


class StandardAuth():

    db_list = {
            'MySQL':'mysql',
            'MS-SQL':'msql'
        }
    
    def __init__(self, username: str, email: Optional[str], password: str, role: Optional[str], status: Optional[bool], new_user:bool=False):
        self.username = username
        self.email = email if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) else (lambda: (_ for _ in ()).throw(Exception("Incorrect email format")))()
        self.password = password if password else (lambda: (_ for _ in ()).throw(Exception("Passsord cannot be empty")))()
        self.role = role
        self.status = status if status in [0, 1] else (lambda: (_ for _ in ()).throw(TypeError("Status has to be boolean. Incorrect type passed.")))()
        self.new_user = new_user
        
        # Encrypt password
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt)

        if not self.new_user:
            self.user_params = {
            'user_name':self.username,
            'email':self.email,
            'password':self.hashed_password,
            'role':self.role,
            'status':self.status
            }

    def _connect_DB (self, db_type: str, host_name: str, user_name: str, user_password: str, db_name: str):
        
        if db_type in self.db_list.values():
            if db_type == 'mysql':
                connection = None
                try:
                    connection = mysql.connector.connect(
                        host = host_name,
                        user = user_name,
                        passwd = user_password,
                        database = db_name
                    )
                    return {'con_object':connection, 'conn_args':{'db_type':db_type, 'host_name':host_name, 'user_name':user_name, 'user_password':user_password, 'db_name':db_name}, 'status':f"Connected to {db_name} as {user_name} on host {host_name}"}
                except Error as e:
                    return {'status': e}
            
            elif db_type == 'msql':
                connection = None
                try:
                    connection = pyodbc.connect(
                        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                        f"SERVER={host_name};"
                        f"DATABASE={db_name};"
                        f"UID={user_name};"
                        f"PWD={user_password}"
                    )
                    return {'con_object':connection, 'conn_args':{'db_type':db_type, 'host_name':host_name, 'user_name':user_name, 'user_password':user_password, 'db_name':db_name}, 'status':f"Connected to {db_name} as {user_name} on host {host_name}"}
                except Exception as e:
                    return {'status': e}
        else:
            return {'status':f"{db_type} Database not supported"}

    def register_user(self, users_tbl_name:str, user_tbl_exists: bool=False, **connection):
        
        con_object = connection['con_object']
        db_type = connection['conn_args']['db_type']
        if db_type in self.db_list.values():
            if db_type == 'mysql':
                cursor = con_object.cursor()
                if not user_tbl_exists:
                    try:
                        cursor.execute(
                            f"""
                            CREATE TABLE IF NOT EXISTS {users_tbl_name} (
                                id INT AUTO_INCREMENT,
                                username TEXT NOT NULL,
                                email TEXT,
                                password TEXT,
                                role TEXT,
                                status INT,
                                PRIMARY KEY (id)
                            )
                            """
                        )
                        cursor.commit()
                        return {'status': f'{users_tbl_name} table created.'}
                    except Exception as e:
                        return {'status': e}
                else:
                    check_user = None
                    try:
                        cursor.execute(
                            f"""
                            SELECT username FROM {users_tbl_name} WHERE username = {self.user_params['user_name']}
                            """
                        )
                        check_user = cursor.fetchone()
                        if check_user is None:
                            cursor.execute(
                                f"""
                                INSERT INTO {users_tbl_name} (username, email, password, role, status)
                                VALUES
                                    ({self.user_params['user_name']}, {self.user_params['email']}, {self.user_params['password']}, {self.user_params['role']}, {self.user_params['status']})
                                """
                            )
                            connection.commit()
                        else:
                            return {'status': f'{self.user_params["user_name"]} already exists.'}
                    except Exception as e:
                        return {'status': e}
            
            elif db_type == "msql":
                cursor = con_object.cursor()
                if not user_tbl_exists:
                    try:
                        cursor.execute(
                            f"""
                            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{users_tbl_name}' AND xtype='U')
                            CREATE TABLE {users_tbl_name} (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                username NVARCHAR(100) NOT NULL,
                                email NVARCHAR(100),
                                password NVARCHAR(100),
                                role NVARCHAR(50),
                                status INT
                            )
                            """
                        )
                        con_object.commit()
                        return {'status': f'{users_tbl_name} table created.'}
                    except Exception as e:
                        return {'status': str(e)}
                else:
                    check_user = None
                    try:
                        cursor.execute(
                            f"""
                            SELECT username FROM {users_tbl_name} WHERE username = ?
                            """, (self.user_params['user_name'])
                        )
                        check_user = cursor.fetchone()
                        if check_user is None:
                            cursor.execute(
                                f"""
                                INSERT INTO {users_tbl_name} (username, email, password, role, status)
                                VALUES (?, ?, ?, ?, ?)
                                """, 
                                (self.user_params['user_name'], self.user_params['email'], self.user_params['password'], self.user_params['role'], self.user_params['status'])
                            )
                            con_object.commit()
                            return {'status': f'{self.user_params["user_name"]} added to {users_tbl_name}.'}
                        else:
                            return {'status': f'{self.user_params["user_name"]} already exists.'}
                    except Exception as e:
                        return {'status': str(e)}
        else:
            return {'status':f"{db_type} Database not supported"}

        return self.user_params
    
    def login_user(self, users_tbl_name: str, **connection):
        con_object = connection['con_object']
        db_type = connection['conn_args']['db_type']

        if db_type in self.db_list.values():
            if db_type == 'mysql':
                cursor = con_object.cursor()
                try:
                    cursor.execute(
                        f"""
                        SELECT password FROM {users_tbl_name} WHERE username = %s
                        """, (self.username,)
                    )
                    result = cursor.fetchone()
                    if result and self.hashed_password == result[0]:
                        return {'status': 'Login successful'}
                    else:
                        return {'status': 'Incorrect username or password'}
                except Exception as e:
                    return {'status': str(e)}
            
            elif db_type == 'mssql':
                cursor = con_object.cursor()
                try:
                    cursor.execute(
                        f"""
                        SELECT password FROM {users_tbl_name} WHERE username = ?
                        """, (self.username,)
                    )
                    result = cursor.fetchone()
                    if result and self.hashed_password == result[0]:
                        return {'status': 'Login successful'}
                    else:
                        return {'status': 'Incorrect username or password'}
                except Exception as e:
                    return {'status': str(e)}
        else:
            return {'status': f"{db_type} Database not supported"}