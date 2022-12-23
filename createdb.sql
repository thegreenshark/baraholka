DROP TABLE IF EXISTS category;
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
    "price" MONEY NOT NULL,
    "category" VARCHAR(256) NOT NULL,
    "address" VARCHAR(512) NOT NULL,
    "datetime" TIMESTAMPTZ NOT NULL DEFAULT LOCALTIMESTAMP NOT NULL,
    "state" SMALLINT NOT NULL
);

CREATE TABLE advert_picture (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "advert_id" UUID REFERENCES advert("id"),
    "file_path" VARCHAR(512) NOT NULL UNIQUE,
    "main" BOOL NOT NULL
);


CREATE TABLE category (
    "name" VARCHAR(256) PRIMARY KEY
);


insert into category values ('Автомобили');
insert into category values ('Мотоциклы');
insert into category values ('Недвижимость');
insert into category values ('Бытовая техника');
insert into category values ('Электроника');
insert into category values ('Прочее');

insert into appuser (email, password, firstname, lastname, phone, ismoderator) values ('moder@a.b', 'e3dd41df22833108b1d6d5b265f1c07b79f8614cf04117687f0765da3ede4c80', 'Модератор', 'Тестовый', '+79214561235', 'TRUE');
insert into appuser (email, password, firstname, lastname, phone) values ('user@a.b', 'ac812756790777d89bcc6b065726bee6de99c136ab53e27d17a1d8b3943a19fa', 'Юзер', 'Дефолтный', '+79211593567');