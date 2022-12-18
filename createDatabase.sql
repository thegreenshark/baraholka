DROP TABLE IF EXISTS appuser;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE appuser (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "firstname" VARCHAR(255) NOT NULL,
    "lastname" VARCHAR(255),
    "phone" VARCHAR(255) NOT NULL UNIQUE,
    "ismoderator" BOOL NOT NULL DEFAULT(FALSE)
);

--insert into appuser (email, password, firstname, lastname, phone) values ('test@a.b', '12345', 'First', 'Last', '+79211111111');