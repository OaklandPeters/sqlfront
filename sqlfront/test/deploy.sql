-- MySQL
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

#-- SQL Server / Oracle / MS Access
CREATE TABLE Persons
(
persons_id int NOT NULL PRIMARY KEY,
last varchar(255) NOT NULL,
first varchar(255),
address varchar(255),
zip INT,
)

CREATE TABLE Orders
(
order_id int NOT NULL PRIMARY KEY,
order_number int NOT NULL,
persons_id int FOREIGN KEY REFERENCES Persons(persons_id)
)


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
