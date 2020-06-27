import psycopg2
import sys
import json


def main(argv):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(user="app",
                                      password="qwerty",
                                      host="localhost",
                                      database="student")

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
        node(cursor, querry["body"]["node"], querry["body"]["lon"], querry["body"]["lat"],
             querry["body"]["description"])
    elif querry["function"] == "catalog":
        catalog(cursor, querry["body"]["version"], querry["body"]["nodes"])
    elif querry["function"] == "trip":
        trip(cursor, querry["body"]["cyclist"], querry["body"]["date"], querry["body"]["version"])
    elif querry["function"] == "closest_nodes":
        closest_nodes(cursor, querry["body"]["ilon"], querry["body"]["ilat"])


def node(cursor, node_id, lon, lat, description):
    cursor.execute(
        """
        INSERT INTO nodes (node, description, location)
        VALUES (%s, %s, ST_MakePoint(%s, %s)::geography);
        """,
        (node_id, description, lon, lat))
    print({"status": "OK"})


def catalog(cursor, version, nodes):
    cursor.execute(
        """
        INSERT INTO trip_catalog (version, nodes, distance)
        VALUES (%s, %s, %s);
        """,
        (version, nodes, None))
    print({"status": "OK"})


def trip(cursor, cyclist, date, version):
    cursor.execute(
        """
        INSERT INTO trips (cyclist, version, start_date)
        VALUES (%s, %s, %s);
        """,
        (cyclist, version, date))
    print({"status": "OK"})


def closest_nodes(cursor, lon, lat):
    cursor.execute(
        """
        SELECT node, ST_Y(location::geometry), ST_X(location::geometry), 
            ST_Distance(location, ST_MakePoint(%s, %s)::geography)
        FROM nodes
        ORDER BY 4 ASC, 1 ASC 
        LIMIT 3;
        """,
        (lon, lat))
    data = []
    for record in cursor:
        data.append({
            "node": record[0],
            "olat": record[1],
            "olon": record[2],
            "distance": round(record[3])
        })
    print({"status": "OK", "data": data})


if __name__ == "__main__":
    main(sys.argv[1:])
