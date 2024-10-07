CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER,
	"tg_user_id"	INTEGER UNIQUE,
	"username"	VARCHAR(255),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "mission" (
	"id"	INTEGER,
	"user_id"	INTEGER,
	"goal"	VARCHAR(255),
	"total_amount"	INTEGER,
	"income"	INTEGER,
	"income_frequency"	INTEGER,
	"period_payments"	INTEGER,
	"date_created"	DATE,
	"saved_amount"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	CONSTRAINT "user_id" FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "payment" (
	"id"	INTEGER,
	"mission_id"	INTEGER,
	"amount"	INTEGER,
	"date"	DATE,
	"is_done "	BOOLEAN DEFAULT FALSE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
