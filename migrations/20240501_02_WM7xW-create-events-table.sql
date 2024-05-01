-- create events table
-- depends: 20240501_01_EPmRJ-create-publishers-table
CREATE TABLE events (
	id		        uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
	location	    point NOT NULL,
	address		    TEXT NOT NULL,
	locale		    VARCHAR(10) NOT NULL,
	title		    VARCHAR(50) NOT NULL,
	description	    TEXT NOT NULL,
	publisher_id	uuid NULL REFERENCES publishers(id) ON DELETE SET NULL ON UPDATE CASCADE,
	created_at	    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at	    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_location ON events USING gist(location);