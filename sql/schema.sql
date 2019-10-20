CREATE TYPE state AS ENUM (
	'Alabama',
	'Alaska',
	'Arkansas',
	'Arizona',
	'Colorado',
	'California',
	'Connecticut',
	'Delaware',
	'Florida',
	'Georgia',
	'Hawaii',
	'Illinois',
	'Indiana',
	'Iowa',
	'Idaho',
	'Kentucky',
	'Kansas',
	'Louisiana',
	'Missouri',
	'Maryland',
	'Maine',
	'Minnesota',
	'Mississippi',
	'Montana',
	'Michigan',
	'Nevada',
	'Oklahoma',
	'Oregon',
	'Massachusetts',
	'Nebraska',
	'New Hampshire',
	'New Mexico',
	'New York',
	'New Jersey',
	'North Dakota',
	'North Carolina',
	'Ohio',
	'Pennsylvania',
	'Rhode Island',
	'South Carolina',
	'South Dakota',
	'Tennessee',
	'Texas',
	'Utah',
	'Vermont',
	'Virginia',
	'Washington',
	'Wisconsin',
	'West Virginia',
	'Wyoming',
	'D.C.'
);

CREATE TABLE users (
	user_email TEXT PRIMARY KEY,
	user_password TEXT NOT NULL,
	user_state state NOT NULL
);

CREATE TABLE categories (
	category TEXT PRIMARY KEY
);

-- each category has associated synonyms which are used as search keywords
-- when the user selects a category, for example "healthcare",
-- left join with this table to find all keywords to search for.
-- DO NOT search for the category itself as it may be too broad
CREATE TABLE keywords (
	category TEXT NOT NULL REFERENCES categories ON DELETE CASCADE,
	keyword TEXT NOT NULL,

	PRIMARY KEY (category, keyword)
);

-- what categories people are interested in
CREATE TABLE preferred_categories (
	user_email TEXT NOT NULL REFERENCES users ON DELETE CASCADE ON UPDATE CASCADE,
	category TEXT NOT NULL REFERENCES categories,

	PRIMARY KEY (user_email, category)
);

CREATE TABLE bills (
	-- stored as-is from the OpenStates API
	bill_id TEXT PRIMARY KEY
);

-- what bills people are tracking
CREATE TABLE preferred_bills (
	user_email TEXT NOT NULL REFERENCES users ON DELETE CASCADE ON UPDATE CASCADE,
	bill_id TEXT NOT NULL REFERENCES bills ON DELETE CASCADE,

	PRIMARY KEY (user_email, bill_id)
);
