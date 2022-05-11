import sqlite3 as sql
import xlrd


                            #id, year, month, income_s,
                            # income_b, counts, income,
                            # target_i, op_profit, mark_strategies


def getConnect():
    return sql.connect(".\data\database.db")


def init(connect):
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE if not exists data (
                id integer primary key autoincrement,
                year integer,
                month varchar(20),
                income_s varchar(128),
                income_b varchar(128),
                counts integer,
                income integer,
                target_i integer,
                op_profit integer,
                mark_strategies varchar(20) default 'B2B'
        )
    ''')


def add(connect, **data):
    if CountS(connect, **data) > 0:
        # print("[-] this value alredy exists")
        return
    cursor = connect.cursor()
    cursor.execute(f"""
            INSERT INTO data ({', '.join(list(data.keys()))} )
            VALUES({', '.join(['?'] * len(data.keys()))})
        """, [data[i] for i in list(data.keys())])

    connect.commit()


def delete(connect, id):
    cursor = connect.cursor()
    cursor.execute('''
            DELETE FROM data 
            WHERE id = ?
        ''', [id])

    connect.commit()

def select(connect, **data):
    cursor = connect.cursor()
    cursor.execute(f""" SELECT 
                                *
                        FROM data 
                        {"WHERE" if len(data.keys()) > 0 else ""} {' AND '.join(list(f"{i} = ?" for i in data.keys()))} 
            """, [data[i] for i in data.keys()])

    return list(cursor.fetchall())

def selectSum(connect, value, group_by=('year',), **data):
    cursor = connect.cursor()
    cursor.execute(f""" SELECT  
                                sum({value})
                        FROM data 
                        {'WHERE' if len(data.keys()) > 0 else ""} {' AND '.join(list(f"{i} = ?" for i in data.keys()))} 
                        GROUP BY {', '.join(group_by)}
            """, [data[i] for i in data.keys()])
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return -1


def CountS(connect, **data):
    cursor = connect.cursor()
    cursor.execute(f""" SELECT 
                                    count(*)
                            FROM data 
                            WHERE ({' AND '.join(list(f"{i} = ?" for i in data.keys()))} )
                """, [data[i] for i in data.keys()])
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return -1


def Update(connect, file="FSDS.xls"):
    workbook = xlrd.open_workbook(f".\data\{file}")
    worksheet = workbook.sheet_by_index(0)
    i = 1
    while True:
        try:
            add(connect,    year=worksheet.cell_value(i, 0),
                            month=worksheet.cell_value(i, 1),
                            income_s=worksheet.cell_value(i, 2),
                            income_b=worksheet.cell_value(i, 3),
                            counts=worksheet.cell_value(i, 4),
                            income=worksheet.cell_value(i, 5),
                            target_i=worksheet.cell_value(i, 6),
                            op_profit=worksheet.cell_value(i, 7),
                            mark_strategies=worksheet.cell_value(i, 8))
        except IndexError:
            break
        i += 1

def selectAVG(connect, value, group_by=('month',), **data):
    cursor = connect.cursor()
    cursor.execute(f""" SELECT AVG(sm)
                        FROM        (SELECT  
                                        sum({value}) as sm
                                    FROM data 
                                    {'WHERE' if len(data.keys()) > 0 else ""} {' AND '.join(list(f"{i} = ?" for i in data.keys()))} 
                                    GROUP BY {', '.join(group_by)}
                                    )tm1
            """, [data[i] for i in data.keys()])
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return -1




if __name__ == "__main__":
    connect = getConnect()
    init(connect)
    Update(connect)
    print(select(connect))
