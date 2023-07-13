CREATE TABLE budget(
    codename VARCHAR(255) primary key,
    daily_limit INTEGER
);

CREATE TABLE category(
    codename VARCHAR(255) primary key,
    name VARCHAR(255),
    is_base_expense boolean,
    aliases text
);

CREATE TABLE expense(
    id INTEGER primary key,
    amount REAL,
    created datetime,
    category_codename INTEGER,
    raw_text text,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

INSERT INTO category (codename, name, is_base_expense, aliases)
VALUES
    ("products", "продукты", true, "еда, zhar, liga, solnechnyj, materik, magazin, karpaty"),
    ("coffee", "кофе", true, ""),
    ("dinner", "обед", true, "столовая, ланч, бизнес-ланч, бизнес ланч"),
    ("cafe", "кафе", true, "ресторан, рест, мак, макдональдс, макдак, kfc, ilpatio, il patio"),
    ("transport", "общ. транспорт", false, "метро, автобус, metro"),
    ("taxi", "такси", false, "яндекс такси, yandex.taxi"),
    ("phone", "телефон", false, "теле2, связь, mts, мтс"),
    ("books", "книги", false, "литература, литра, лит-ра"),
    ("internet", "интернет", false, "инет, inet, norcom"),
    ("subscriptions", "подписки", false, "подписка, ivi, yandex*5815*plus"),
    ("veiping", "вейп", false, "жидкость, вейп, картридж, devays"),
    ("credit", "кредит", true, "кредит"),
    ("aliments", "оплата_Катюше_Вовчику", true, "катя, вовчик"),
    ("learn", "обучение", true, "stepik"),
    ("aviation", "перелет", false, "s7_1, s7"),
    ("vps_vsd", "удаленный_сервер", false, "timeweb"),
    ("games", "игры", false, "game, игры"),
    ("other", "прочее", true, "");

INSERT INTO budget(codename, daily_limit)
VALUES ('base', 1500);
