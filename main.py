import psycopg2
import emoji
# from pprint import pprint


def create_db(cur):
    """
    1. Функция, создающая структуру БД (таблицы)
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
        id SERIAL PRIMARY KEY,
        name VARCHAR(20) NOT NULL,
        lastname VARCHAR(30) NOT NULL,
        email VARCHAR(50) NOT NULL UNIQUE
        );
        """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phones(
        number CHAR(12) PRIMARY KEY,
        client_id INTEGER REFERENCES clients(id)
        );
    """)
    # print("Tables have been created successfully")
    return "Tables have been created successfully"

def delete_db(cur):
    """
    Функция, удаляющая таблицы при запуске
    """
    cur.execute("""
        DROP TABLE clients, phones CASCADE;
    """)
    # print("Tables successfully deleted")
    return "Tables successfully deleted"


def add_phone(cur, client_id, number):
    """
    3. Функция, позволяющая добавить телефон для существующего клиента
    """
    cur.execute("""
        INSERT INTO phones(number, client_id)
        VALUES (%s, %s)
    """, (number, client_id))
    # print(f"A phone number {number} has been added to the client {client_id}")
    return f"A phone number {number} has been added to the client {client_id}"

def add_client(cur, name, lastname, email, number=None):
    """
    2. Функция, позволяющая добавить нового клиента
    """
    cur.execute("""
        INSERT INTO clients(name, lastname, email)
        VALUES (%s, %s, %s)
        """, (name, lastname, email))
    cur.execute("""
        SELECT id from clients
        ORDER BY id DESC
        LIMIT 1
    """)
    client_id = cur.fetchone()[0]
    if number is None:
        # print(f"The client {name, lastname, email, number} was added without a phone number")
        return f"The client {name, lastname, email, number} was added without a phone number"
    else:
        add_phone(cur, client_id, number)
        # print(f"The client {name, lastname, email, number} added with phone number")
        return f"The client {name, lastname, email, number} added with phone number"

def change_client(cur, id, name=None, lastname=None, email=None):
    """
    4. Функция, позволяющая изменить данные о клиенте
    """
    cur.execute("""
        SELECT * FROM clients
        WHERE id = %s
        """, (id, ))
    info = cur.fetchone()
    if name is None:
        name = info[1]
    if lastname is None:
        lastname = info[2]
    if email is None:
        email = info[3]
    cur.execute("""
        UPDATE clients
        SET name = %s, lastname = %s, email = %s
        WHERE id = %s
        """, (name, lastname, email, id))
    return "The clients data changed"

def delete_phone(cur, number):
    """
    5. Функция, позволяющая удалить телефон для существующего клиента
    """
    cur.execute("""
        DELETE FROM phones
        WHERE number = %s
        """, (number, ))
    return f"Phone number {number} deleted"

def delete_clients(cur, id):
    """
    6. Функция, позволяющая удалить существующего клиента
    """
    cur.execute("""
        DELETE FROM phones
        WHERE client_id = %s
        """, (id,))
    cur.execute("""
        DELETE FROM clients
        WHERE id = %s
        """, (id, ))
    return f"Client number {id} has been successfully deleted"

def client_search(cur, name=None, lastname=None, email=None, number=None):
    """
    7. Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
    """
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if lastname is None:
        surname = '%'
    else:
        surname = '%' + lastname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if number is None:
        cur.execute("""
            SELECT cl.id, cl.name, cl.lastname, cl.email, ph.number FROM clients cl
            JOIN phones ph ON cl.id = ph.client_id
            WHERE cl.name LIKE %s AND cl.lastname LIKE %s
            AND cl.email LIKE %s
            """, (name, surname, email))
    else:
        cur.execute("""
             SELECT cl.id, cl.name, cl.lastname, cl.email, ph.number FROM clients cl
             LEFT JOIN phones ph ON cl.id = ph.client_id
             WHERE cl.name LIKE %s AND cl.lastname LIKE %s
             AND cl.email LIKE %s AND ph.number like %s
             """, (name, surname, email, number))
    return cur.fetchall()


with psycopg2.connect(database="psypost_db", user="postgres", password="PASSWORD") as conn:
    with conn.cursor() as curs:

        # Удаляем таблицы при запуске
        print(delete_db(curs))
        print(emoji.emojize(':cross_mark:'))

        # Создаём структуру БД
        print(create_db(curs))
        print(emoji.emojize(':thumbs_up:'))

        # Добавляем новых клиентов:

        print(add_client(curs, "Константин", "Хабеников", "konsthab@mail.ru", 89219212131))
        print(add_client(curs, "Марат", "Башкаров", "martbash@mail.ru", 89998554050))
        print(add_client(curs, "Светлана", "Ходчекова", "svethod@mail.ru"))
        print(add_client(curs, "Павел", "Волен", "pavwol@mail.ru"))

        # Добавляем телефон для существующего клиента:
        print(add_phone(curs, 3, 89554554535))
        print(add_phone(curs, 2, 89453859525))

        # Изменение данных о клиенте:
        print(change_client(curs, 2, "Матвей", "Коротков", "matvcor@mail.ru"))

        # Удаление телефона для существующего клиента:
        print(delete_phone(curs, "89554554535"))

        # Удаление существующего клиента:
        print(delete_clients(curs, 1))

        # Поиск клиента по его данным: имени, фамилии, email или телефону:
        print(client_search(curs, "Павел", "Волен", "pavwol@mail.ru", None))
        print(client_search(curs, "Марат", None, None, None))
        print(client_search(curs, "Константин", "Хабеников", "konsthab@mail.ru", "89219212131"))

conn.close()