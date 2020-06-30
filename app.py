import psycopg2
import sys
import json
from datetime import datetime
from datetime import timedelta
from psycopg2.extras import execute_values


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


def delegate(cursor, query):
    # Why is there no pattern matching in Python? ;_;
    body = query["body"]
    if query["function"] == "node":
        node(cursor, body["node"], body["lon"], body["lat"], body["description"])
    elif query["function"] == "catalog":
        catalog(cursor, body["version"], body["nodes"])
    elif query["function"] == "trip":
        trip(cursor, body["cyclist"], body["date"], body["version"])
    elif query["function"] == "closest_nodes":
        closest_nodes(cursor, body["ilon"], body["ilat"])
    elif query["function"] == "guests":
        guests(cursor, body["node"], body["date"])
    elif query["function"] == "party":
        party(cursor, body["icyclist"], body["date"])
    elif query["function"] == "cyclists":
        cyclists(cursor, body["limit"])


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
        VALUES (%s, %s, calculate_distance(%s));
        """,
        (version, nodes, nodes))
    print({"status": "OK"})


def trip(cursor, cyclist, date, version):
    cursor.execute(
        """
        INSERT INTO trips (cyclist, version, start_date)
        VALUES (%s, %s, %s);
        """,
        (cyclist, version, date))
    cursor.execute(
        """
        SELECT nodes FROM trip_catalog
        WHERE version = %s
        """,
        (version,)
    )
    nodes = cursor.fetchone()[0]
    date = datetime.strptime(date, "%Y-%m-%d")
    accommodations = []
    for place in nodes[1:-1]:
        accommodations.append((cyclist, place, date.strftime("%Y-%m-%d")))
        date += timedelta(days=1)
    execute_values(
        cursor,
        """
        INSERT INTO guests(cyclist, node, stay_date)
        VALUES %s
        """,
        accommodations
    )
    print({"status": "OK"})


def closest_nodes(cursor, lon, lat):
    cursor.execute(
        """
        SELECT node, ST_Y(location::geometry), ST_X(location::geometry), 
            ST_Distance(location, ST_MakePoint(%s, %s)::geography)
        FROM nodes
        ORDER BY location <-> (ST_MakePoint(%s, %s)::geography), 1 ASC 
        LIMIT 3;
        """,
        (lon, lat, lon, lat))
    data = []
    for record in cursor:
        data.append({
            "node": record[0],
            "olat": record[1],
            "olon": record[2],
            "distance": round(record[3])
        })
    print({"status": "OK", "data": data})


def party(cursor, cyclist, date):
    cursor.execute(
        """
        SELECT ST_X(location::geometry), ST_Y(location::geometry)
        FROM guests JOIN nodes USING (node)
        WHERE cyclist = %s AND stay_date = %s;
        """,
        (cyclist, date)
    )
    if cursor.rowcount == 0:
        print({"status": "OK", "data": []})
        return
    location = cursor.fetchone()
    cursor.execute(
        """
        SELECT cyclist, node, ST_Distance(location, ST_MakePoint(%s, %s)::geography)
        FROM guests JOIN nodes USING (node)
        WHERE ST_DWithin(location, ST_MakePoint(%s, %s)::geography, 20000)
        AND stay_date = %s
        AND cyclist <> %s
        ORDER BY 3 ASC, 1 ASC;
        """,
        (location[0], location[1], location[0], location[1], date, cyclist)
    )
    data = []
    for record in cursor:
        data.append({
            "ocyclist": record[0],
            "node": record[1],
            "distance": round(record[2])
        })
    print({"status": "OK", "data": data})


def guests(cursor, node, date):
    cursor.execute(
        """
        SELECT cyclist FROM guests
        WHERE stay_date = %s AND node = %s
        ORDER BY 1 ASC;
        """,
        (date, node))
    data = []
    for record in cursor:
        data.append({
            "cyclist": record[0]
        })
    print({"status": "OK", "data": data})


def cyclists(cursor, limit):
    cursor.execute(
        """
        SELECT cyclist, COUNT(distance), SUM(distance)
        FROM trips JOIN trip_catalog USING (version)
        GROUP BY cyclist
        ORDER BY 3 ASC, 1 ASC
        LIMIT %s;
        """,
        (limit,)
    )
    data = []
    for record in cursor:
        data.append({
            "cyclist": record[0],
            "no_trips": record[1],
            "distance": round(record[2])
        })
    print({"status": "OK", "data": data})


if __name__ == "__main__":
    main(sys.argv[1:])
