-- Suppliers
CREATE TABLE suppliers(
   supplier_id SERIAL PRIMARY KEY,
   supplier_name VARCHAR(40) NOT NULL
);

INSERT INTO suppliers (supplier_name) VALUES ('Bertrand Livreiros');
INSERT INTO suppliers (supplier_name) VALUES ('FNAC');
INSERT INTO suppliers (supplier_name) VALUES ('Wook');
INSERT INTO suppliers (supplier_name) VALUES ('Amazon');
INSERT INTO suppliers (supplier_name) VALUES ('El Corte Inglés');

-- Countries (table name must match SQLModel: lowercase class name "country")
CREATE TABLE country(
   id SERIAL PRIMARY KEY,
   name VARCHAR(100) NOT NULL UNIQUE,
   region VARCHAR(100) NOT NULL
);

INSERT INTO country (name, region) VALUES ('Portugal', 'Europe');
INSERT INTO country (name, region) VALUES ('Spain', 'Europe');
INSERT INTO country (name, region) VALUES ('France', 'Europe');
INSERT INTO country (name, region) VALUES ('Germany', 'Europe');
INSERT INTO country (name, region) VALUES ('Brazil', 'South America');

-- Authors
CREATE TABLE author(
   id SERIAL PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   age INT NOT NULL,
   country VARCHAR(100) NOT NULL
);

INSERT INTO author (name, age, country) VALUES ('José Saramago', 87, 'Portugal');
INSERT INTO author (name, age, country) VALUES ('Fernando Pessoa', 47, 'Portugal');
INSERT INTO author (name, age, country) VALUES ('Gabriel García Márquez', 87, 'Colombia');
INSERT INTO author (name, age, country) VALUES ('George Orwell', 46, 'United Kingdom');
INSERT INTO author (name, age, country) VALUES ('William Golding', 81, 'United Kingdom');

-- Books (with author FK)
CREATE TABLE book(
   id SERIAL PRIMARY KEY,
   title VARCHAR(100) NOT NULL UNIQUE,
   year INT NOT NULL,
   available BOOLEAN DEFAULT TRUE,
   cost_price DECIMAL(10,2) NOT NULL,
   sale_price DECIMAL(10,2) NOT NULL,
   author VARCHAR(100) NOT NULL,
   author_id INT REFERENCES author(id)
);

INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('O Evangelho segundo Jesus Cristo', 1991, true, 10.00, 15.00, 'José Saramago', 1);
INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('Ensaio sobre a Cegueira', 1995, true, 12.00, 18.00, 'José Saramago', 1);
INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('Mensagem', 1934, true, 8.00, 12.00, 'Fernando Pessoa', 2);
INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('Cem Anos de Solidão', 1967, true, 15.00, 22.00, 'Gabriel García Márquez', 3);
INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('Amor em Tempos de Cólera', 1985, true, 13.00, 20.00, 'Gabriel García Márquez', 3);
INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('1984', 1949, true, 11.00, 17.00, 'George Orwell', 4);
INSERT INTO book (title, year, available, cost_price, sale_price, author, author_id) VALUES ('O Senhor das Moscas', 1954, true, 10.00, 16.00, 'William Golding', 5);

-- Analytics Results Tables

CREATE TABLE analytics_results(
   id SERIAL PRIMARY KEY,
   metric_name VARCHAR(100) NOT NULL,
   metric_key VARCHAR(100),
   metric_value DECIMAL(15,2),
   computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE revenue_by_book(
   book_id INT NOT NULL PRIMARY KEY,
   revenue DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expenses_by_book(
   book_id INT NOT NULL PRIMARY KEY,
   expenses DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profit_by_book(
   book_id INT NOT NULL PRIMARY KEY,
   profit DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Totals and scalar metrics (total_revenue, total_expenses, total_profit, top_profit_book, average_purchase)
CREATE TABLE total_metrics(
   metric_name VARCHAR(50) PRIMARY KEY,
   metric_value DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE average_purchase_by_book(
   book_id INT NOT NULL PRIMARY KEY,
   average_amount DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time-windowed metrics (revenue_last_hour, expenses_last_hour, profit_last_hour)
CREATE TABLE time_window_metrics(
   metric_type VARCHAR(50) NOT NULL PRIMARY KEY,
   metric_value DECIMAL(15,2),
   window_start TIMESTAMP,
   window_end TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Top sales by country per book (Req #17)
CREATE TABLE best_performing_by_country(
   book_id INT NOT NULL,
   country_id INT NOT NULL,
   sales_volume DECIMAL(15,2),
   revenue DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (book_id, country_id)
);
