DROP TABLE IF EXISTS advert_picture;
DROP TABLE IF EXISTS advert;
DROP TABLE IF EXISTS appuser;




CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SET lc_monetary TO "ru-RU";

CREATE TABLE appuser (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" VARCHAR(256) NOT NULL UNIQUE,
    "password" VARCHAR(256) NOT NULL,
    "firstname" VARCHAR(256) NOT NULL,
    "lastname" VARCHAR(256),
    "phone" VARCHAR(256) NOT NULL UNIQUE,
    "ismoderator" BOOL NOT NULL DEFAULT(FALSE)
);


CREATE TABLE advert (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" UUID REFERENCES appuser("id")NOT NULL,
    "name" VARCHAR(256) NOT NULL,
    "description" VARCHAR(2048),
    "price" MONEY,
    "category" VARCHAR(256) NOT NULL,
    "address" VARCHAR(512) NOT NULL,
    "creation_time" TIMESTAMPTZ NOT NULL DEFAULT LOCALTIMESTAMP(0) NOT NULL,
    "status" VARCHAR(256) NOT NULL
);

CREATE TABLE advert_picture (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "advert_id" UUID REFERENCES advert("id"),
    "file_path" VARCHAR(512) NOT NULL UNIQUE
);
