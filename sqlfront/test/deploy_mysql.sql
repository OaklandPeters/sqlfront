-- MySQL
-- Requires you to login as user with database creation and granting permissions. 
-- Call from commandline with: mysql -uUSER -pPASSWORD < deploy_mysql.sql

-- Create database
CREATE DATABASE test_sqlfront;
USE test_sqlfront;

-- Create user
CREATE USER 'sqlfront'@'localhost' IDENTIFIED BY 'default';
GRANT ALL PRIVILEGES ON test_sqlfront.* TO 'sqlfront'@'localhost';

-- Populate database

CREATE TABLE Persons
(
persons_id int NOT NULL AUTO_INCREMENT,
last varchar(255) NOT NULL,
first varchar(255),
address varchar(255),
zip int,
PRIMARY KEY (persons_id)
);

CREATE TABLE Orders
(
order_id int NOT NULL AUTO_INCREMENT,
order_number int NOT NULL,
persons_id int,
PRIMARY KEY (order_id),
FOREIGN KEY (persons_id) REFERENCES Persons(persons_id)
);


-- Insert Data

INSERT INTO Persons (last, first, address, zip) VALUES ('Clark', 'Daniel', '2138 Spring Avenue, Horsham, PA', 19044);
INSERT INTO Persons (last, first, address, zip) VALUES ('Maria', 'Collins', '3921 Walnut Avenue Lyndhurst, NJ', 07071);
INSERT INTO Persons (last, first, address, zip) VALUES ('Michael', 'Martins', '2552 Columbia Boulevard Bel Air, MD', 21014);
INSERT INTO Persons (last, first, address, zip) VALUES ('Melanie', 'Seagle', '1275 Cameron Road Lockport, MD', 21014);

INSERT INTO Orders (order_number, persons_id) VALUES (67492, 2);
INSERT INTO Orders (order_number, persons_id) VALUES (15789, 1);
INSERT INTO Orders (order_number, persons_id) VALUES (27877, 3);
INSERT INTO Orders (order_number, persons_id) VALUES (11256, 1);
INSERT INTO Orders (order_number, persons_id) VALUES (57891, 1);
INSERT INTO Orders (order_number, persons_id) VALUES (33333, 3);
INSERT INTO Orders (order_number, persons_id) VALUES (33334, 4);
