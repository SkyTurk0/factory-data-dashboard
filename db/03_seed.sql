USE FactoryDB;
GO

INSERT INTO dbo.Machines (Name, Line, Status)
VALUES 
('Packaging Unit','LineA','RUNNING'),
('CNC Machine','LineA','IDLE'),
('Assembly Robot','LineB','RUNNING');

-- Quick events
INSERT INTO dbo.Events (MachineId, Type, Code, Message)
VALUES
(1,'START',NULL,'Line started'),
(1,'ERROR','E42','Motor vibration detected'),
(2,'STOP',NULL,'Awaiting material'),
(3,'MAINT','M10','Scheduled maintenance');

-- Simple telemetry (3 snapshots per machine)
DECLARE @i INT = 0;
WHILE @i < 3
BEGIN
  INSERT INTO dbo.Telemetry (MachineId, Temperature, Vibration, Throughput)
  SELECT Id,
         25 + (ABS(CHECKSUM(NEWID())) % 50),
         0.1 + (ABS(CHECKSUM(NEWID())) % 80)/10.0,
         50 + (ABS(CHECKSUM(NEWID())) % 200)
  FROM dbo.Machines;
  SET @i += 1;
END
GO
