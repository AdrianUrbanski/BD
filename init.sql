CREATE TABLE nodes (
    node INTEGER PRIMARY KEY,
    description TEXT,
    location geography(POINT)
);

CRETE TABLE trip_catalog (
    version INTEGER PRIMARY KEY,
    nodes INTEGER [],
    distance INTEGER
);

CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    cyclist INTEGER,
    version INTEGER REFERENCES trip_catalog(version),
    start_date DATE
);

CREATE TABLE guests (
    cyclist INTEGER,
    node INTEGER REFERENCES nodes(node),
    stay_date DATE,
    PRIMARY KEY (cyclist, node, stay_date)
);

