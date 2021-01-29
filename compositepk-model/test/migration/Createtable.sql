
#################################
# For SQLite3

CREATE TABLE "Company" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "established_date" date NOT NULL, "company_code" varchar(100) NOT NULL);

CREATE TABLE "Musician" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "first_name" varchar(50) NOT NULL, "last_name" varchar(50) NOT NULL, "profile" varchar(100) NOT NULL);

CREATE TABLE "CompanyBranch" ("company_id" integer NOT NULL REFERENCES "Company" ("id") DEFERRABLE INITIALLY DEFERRED, "country_code" varchar(100) NOT NULL, "name" varchar(100) NOT NULL, "established_date" date NOT NULL);
CREATE INDEX "CompanyBranch_company_id" ON "CompanyBranch" ("company_id");
CREATE UNIQUE INDEX "CompanyBranch_company_id_country_code_uniq" ON "CompanyBranch" ("company_id", "country_code");

CREATE TABLE "Album" ("artist_id" integer NOT NULL REFERENCES "Musician" ("id") DEFERRABLE INITIALLY DEFERRED, "album_no" integer NOT NULL, "name" varchar(100) NOT NULL, "release_date" date NOT NULL, "num_stars" integer NOT NULL, "item_code" varchar(100) NOT NULL, "company_id" integer NOT NULL REFERENCES "Company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "Album_artist_id_album_no_uniq" ON "Album" ("artist_id", "album_no");
CREATE INDEX "Album_artist_id" ON "Album" ("artist_id");
CREATE INDEX "Album_company_id" ON "Album" ("company_id");


#################################
# For PsotgreSQL

CREATE TABLE "Company" ("id" SERIAL NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL, "established_date" date NOT NULL, "company_code" varchar(100) NOT NULL);

CREATE TABLE "Musician" ("id" SERIAL NOT NULL PRIMARY KEY, "first_name" varchar(50) NOT NULL, "last_name" varchar(50) NOT NULL, "profile" varchar(100) NOT NULL);

CREATE TABLE "CompanyBranch" ("company_id" integer NOT NULL REFERENCES "Company" ("id") DEFERRABLE INITIALLY DEFERRED, "country_code" varchar(100) NOT NULL, "name" varchar(100) NOT NULL, "established_date" date NOT NULL);
CREATE INDEX "CompanyBranch_company_id" ON "CompanyBranch" ("company_id");
CREATE UNIQUE INDEX "CompanyBranch_company_id_country_code_uniq" ON "CompanyBranch" ("company_id", "country_code");

CREATE TABLE "Album" ("artist_id" integer NOT NULL REFERENCES "Musician" ("id") DEFERRABLE INITIALLY DEFERRED, "album_no" integer NOT NULL, "name" varchar(100) NOT NULL, "release_date" date NOT NULL, "num_stars" integer NOT NULL, "item_code" varchar(100) NOT NULL, "company_id" integer NOT NULL REFERENCES "Company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "Album_artist_id_album_no_uniq" ON "Album" ("artist_id", "album_no");
CREATE INDEX "Album_artist_id" ON "Album" ("artist_id");
CREATE INDEX "Album_company_id" ON "Album" ("company_id");
