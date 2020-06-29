CREATE OR REPLACE FUNCTION calculate_distance(INTEGER[]) RETURNS FLOAT AS $$
DECLARE
    dist FLOAT := 0;
    curr geography(POINT);
    prev geography(POINT) := NULL;
    curr_node INTEGER;
BEGIN
    FOREACH curr_node IN ARRAY $1
    LOOP
        SELECT location INTO curr FROM nodes WHERE node = curr_node;
        IF prev IS NOT NULL THEN
            dist := dist + ST_Distance(prev, curr);
        END IF;
        prev := curr;
    END LOOP;
    RETURN dist;
END;
$$ LANGUAGE plpgsql;
