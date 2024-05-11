-- create publishers table
-- depends: 
CREATE TABLE publishers (
	id		        uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
	display_name	VARCHAR(50) NOT NULL,
	display_image 	VARCHAR(250) NULL,
	created_at 	    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at 	    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
