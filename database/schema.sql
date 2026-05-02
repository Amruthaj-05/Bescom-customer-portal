IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
CREATE TABLE users (
  id INT IDENTITY(1,1) PRIMARY KEY,
  customer_id NVARCHAR(100) UNIQUE NOT NULL
);
ALTER TABLE Meter ADD  meter_id TEXT;
ALTER TABLE PowerConsumption ADD  Consumption_id TEXT;
ALTER TABLE bills ADD  Bill_Id TEXT;
ALTER TABLE Payment ADD  Payment_id TEXT;

