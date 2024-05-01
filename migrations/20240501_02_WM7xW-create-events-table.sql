-- create events table
-- depends: 20240501_01_EPmRJ-create-publishers-table
CREATE TABLE events (
	id		        UUID NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
	location	    GEOGRAPHY NOT NULL,
	address		    TEXT NOT NULL,
	locale		    VARCHAR(10) NOT NULL,
	title		    VARCHAR(50) NOT NULL,
	description	    TEXT NOT NULL,
    slug            VARCHAR(20) NOT NULL,
    tags            JSONB NOT NULL,
	publisher_id	UUID NULL REFERENCES publishers(id) ON DELETE SET NULL ON UPDATE CASCADE,
	created_at	    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at	    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX events_location ON events USING gist(location);