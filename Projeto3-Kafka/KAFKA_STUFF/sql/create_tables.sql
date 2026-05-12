CREATE TABLE suppliers(
   supplier_id SERIAL PRIMARY KEY,
   supplier_name VARCHAR(40) NOT NULL
);

INSERT INTO suppliers (supplier_name) VALUES ('SMTUC');
INSERT INTO suppliers (supplier_name) VALUES ('Metro Mondego');
INSERT INTO suppliers (supplier_name) VALUES ('Coimbra Taxis');
INSERT INTO suppliers (supplier_name) VALUES ('Bolt');
INSERT INTO suppliers (supplier_name) VALUES ('Scooters Assassinas');

-- Analytics Metadata Tables
CREATE TABLE countries(
   id SERIAL PRIMARY KEY,
   name VARCHAR(100) NOT NULL UNIQUE,
   region VARCHAR(100) NOT NULL
);

INSERT INTO countries (name, region) VALUES ('Portugal', 'Europe');
INSERT INTO countries (name, region) VALUES ('Spain', 'Europe');
INSERT INTO countries (name, region) VALUES ('France', 'Europe');
INSERT INTO countries (name, region) VALUES ('Germany', 'Europe');
INSERT INTO countries (name, region) VALUES ('Brazil', 'South America');

CREATE TABLE books(
   id SERIAL PRIMARY KEY,
   title VARCHAR(100) NOT NULL UNIQUE,
   year INT NOT NULL,
   available BOOLEAN,
   cost_price DECIMAL(10,2) NOT NULL,
   sale_price DECIMAL(10,2) NOT NULL
);

INSERT INTO books (title, year, available, cost_price, sale_price) VALUES ('The Great Gatsby', 1925, true, 10.00, 15.00);
INSERT INTO books (title, year, available, cost_price, sale_price) VALUES ('1984', 1948, true, 12.00, 18.00);
INSERT INTO books (title, year, available, cost_price, sale_price) VALUES ('To Kill a Mockingbird', 1960, false, 15.00, 22.00);
INSERT INTO books (title, year, available, cost_price, sale_price) VALUES ('The Catcher in the Rye', 1951, true, 13.00, 19.00);
INSERT INTO books (title, year, available, cost_price, sale_price) VALUES ('Lord of the Flies', 1954, true, 14.00, 20.00);

-- Analytics Results Tables

CREATE TABLE analytics_results(
   id SERIAL PRIMARY KEY,
   metric_name VARCHAR(100) NOT NULL,
   metric_key VARCHAR(100),
   metric_value DECIMAL(15,2),
   computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE revenue_by_book(
   book_id INT NOT NULL,
   revenue DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (book_id),
   FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE expenses_by_book(
   book_id INT NOT NULL,
   expenses DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (book_id),
   FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE profit_by_book(
   book_id INT NOT NULL,
   profit DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (book_id),
   FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE total_metrics(
   metric_name VARCHAR(50) PRIMARY KEY,
   metric_value DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE average_purchase_by_book(
   book_id INT NOT NULL,
   average_amount DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (book_id),
   FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE time_window_metrics(
   window_start TIMESTAMP NOT NULL,
   window_end TIMESTAMP NOT NULL,
   metric_type VARCHAR(50) NOT NULL,
   metric_value DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (window_start, window_end, metric_type)
);

CREATE TABLE best_performing_by_country(
   book_id INT NOT NULL,
   country_id INT NOT NULL,
   sales_volume INT,
   revenue DECIMAL(15,2),
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (book_id, country_id),
   FOREIGN KEY (book_id) REFERENCES books(id),
   FOREIGN KEY (country_id) REFERENCES countries(id)
);
