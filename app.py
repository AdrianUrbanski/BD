import psycopg2
import sys
import json
from postgis import Point
from postgis.psycopg import register


def main(argv):
    try:
        connection = psycopg2.connect(user="app",
                                      password="qwerty",
                                      host="localhost",
                                      database="student")
        register(connection)

        cursor = connection.cursor()

        if len(argv):
            if len(argv) > 1 or argv[0] != "--init":
                raise Exception('Invalid arguments. Usage: app.py [--init]')
            cursor.execute(open("init.sql", "r").read())
            print("{\"status\": \"OK\"}")

        for line in sys.stdin:
            delegate(cursor, json.loads(line))

        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("There's been a problem: ", error)

    finally:
        if connection:
            cursor.close()
            connection.close()


def delegate(cursor, querry):
    # Why is there no pattern matching in Python? ;_;
    if querry["function"] == "node":
        node(cursor, querry["body"]["node"], querry["body"]["lat"], querry["body"]["lon"], querry["body"]["description"])
    elif querry["function"] == "catalog":
        catalog(cursor, querry["body"]["version"], querry["body"]["nodes"])
    elif querry["function"] == "trip":
        trip(cursor, querry["body"]["cyclist"], querry["body"]["date"], querry["body"]["version"])


def node(cursor, node_id, lat, lon, description):
    cursor.execute("""
        INSERT INTO nodes (node, description, location)
        VALUES (%s, %s, %s);
        """,
        (node_id, description, Point(lat, lon)))
    print("{\"status\": \"OK\"}")


def catalog(cursor, version, nodes):
    cursor.execute("""
        INSERT INTO trip_catalog (version, nodes, distance)
        VALUES (%s, %s, %s);
        """,
        (version, nodes, None))
    print("{\"status\": \"OK\"}")


def trip(cursor, cyclist, date, version):
    cursor.execute("""
        INSERT INTO trips (cyclist, version, start_date)
        VALUES (%s, %s, %s);
        """,
        (cyclist, version, date))
    print("{\"status\": \"OK\"}")


if __name__ == "__main__":
    main(sys.argv[1:])