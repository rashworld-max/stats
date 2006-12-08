create table simple (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	license_uri VARCHAR(255)  NOT NULL,
	search_engine VARCHAR(255) NOT NULL,
	count INT NOT NULL,
	timestamp DATETIME NOT NULL,
	country VARCHAR(255),
	language VARCHAR(255)
);

create table complex (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	license_specifier VARCHAR(255) NOT NULL,
	search_engine VARCHAR(255) NOT NULL,
	count INT NOT NULL,
	query VARCHAR(255),
	timestamp DATETIME NOT NULL,
	country VARCHAR(255),
	language VARCHAR(255)
);

create index simple_timestamp_index on simple (timestamp);
create index complex_timestamp_index on complex (timestamp);
