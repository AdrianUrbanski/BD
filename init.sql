CREATE TABLE nodes (
    node INTEGER PRIMARY KEY,
    description TEXT,
    location geography(POINT)
);

CREATE TABLE trip_catalog (
    version INTEGER PRIMARY KEY,
    nodes INTEGER[],
    distance FLOAT
);

CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    cyclist TEXT,
    version INTEGER REFERENCES trip_catalog(version),
    start_date DATE
);

CREATE TABLE guests (
    cyclist TEXT,
    node INTEGER REFERENCES nodes(node),
    stay_date DATE,
    PRIMARY KEY (cyclist, stay_date)
);

CREATE INDEX nodes_btree_node ON nodes USING btree(node);
CREATE INDEX nodes_gist_location ON nodes USING GIST(location);

CREATE INDEX catalog_btree_version ON trip_catalog USING btree(version);

CREATE INDEX trip_btree_cyclist ON trips USING btree(cyclist);
CREATE INDEX trip_btree_version ON trips USING btree(version);

CREATE INDEX guests_btree_date_node ON guests USING btree(stay_date, node);
