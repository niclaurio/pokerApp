CREATE TABLE levels (
    id SERIAL PRIMARY KEY,
    start_from INT NOT NULL UNIQUE,
    end_to INT NOT NULL UNIQUE,
    fee INT NOT NULL UNIQUE,
    players_num INT NOT NULL,
    CONSTRAINT start_lt_end CHECK (start_from < end_to AND start_from >= 0),
    CONSTRAINT fee_players_num_positive CHECK (fee > 0 AND players_num > 0)
);


CREATE TABLE app_configs(
    key text not null unique ,
    value text not null
)

CREATE OR REPLACE FUNCTION check_start_from_end_to()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id > 1 THEN
        IF NEW.start_from != (SELECT end_to FROM level WHERE id = NEW.id - 1) THEN
            RAISE EXCEPTION 'start_from of id % must equal end_to of id %', NEW.id, NEW.id - 1;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER level_start_from_check
BEFORE INSERT ON level
FOR EACH ROW
EXECUTE FUNCTION check_start_from_end_to();


CREATE OR REPLACE FUNCTION check_fee_higher_than_previous()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fee <= (SELECT MAX(fee) FROM level WHERE id < NEW.id) THEN
        RAISE EXCEPTION 'The fee % must be greater than all previous fees', NEW.fee;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER level_fee_check
BEFORE INSERT ON level
FOR EACH ROW
EXECUTE FUNCTION check_fee_higher_than_previous();
