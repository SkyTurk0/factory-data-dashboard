USE FactoryDB;
GO

-- Optional: wipe old demo data (keep Machines if you want stable IDs)
DELETE FROM dbo.Telemetry;
DELETE FROM dbo.Events;
-- If you want to recreate machines too, uncomment below:
DELETE FROM dbo.Machines;

-- (Re)create machines if table is empty
IF NOT EXISTS (SELECT 1 FROM dbo.Machines)
BEGIN
    INSERT INTO dbo.Machines (Name, Line, Status)
    VALUES 
    ('Packaging Unit','LineA','RUNNING'),
    ('CNC Machine','LineA','IDLE'),
    ('Assembly Robot','LineB','RUNNING');
END
GO

/* -------------------------------
   Seed EVENTS (richer + varied)
   ------------------------------- */

-- Machine 1: Packaging Unit → more incidents
INSERT INTO dbo.Events (MachineId, Type, Code, Message, Ts) VALUES
(1,'START',NULL,'Line started',                   DATEADD(HOUR,-120,SYSUTCDATETIME())),
(1,'ERROR','E42','Motor vibration detected',      DATEADD(HOUR,-98, SYSUTCDATETIME())),
(1,'ERROR','E77','Sensor misalignment',           DATEADD(HOUR,-74, SYSUTCDATETIME())),
(1,'STOP', NULL,'Operator stop for inspection',   DATEADD(HOUR,-73, SYSUTCDATETIME())),
(1,'START',NULL,'Resume after inspection',        DATEADD(HOUR,-72, SYSUTCDATETIME())),
(1,'ERROR','E55','Jammed carton detected',        DATEADD(HOUR,-26, SYSUTCDATETIME()));

-- Machine 2: CNC Machine → moderate errors
INSERT INTO dbo.Events (MachineId, Type, Code, Message, Ts) VALUES
(2,'START',NULL,'Shift start',                    DATEADD(HOUR,-120,SYSUTCDATETIME())),
(2,'STOP', NULL,'Awaiting material',              DATEADD(HOUR,-96, SYSUTCDATETIME())),
(2,'ERROR','E99','Overheating detected',          DATEADD(HOUR,-95, SYSUTCDATETIME())),
(2,'START',NULL,'Material refilled',              DATEADD(HOUR,-94, SYSUTCDATETIME())),
(2,'ERROR','E88','Coolant low',                   DATEADD(HOUR,-20, SYSUTCDATETIME()));

-- Machine 3: Assembly Robot → fewer errors + maintenance
INSERT INTO dbo.Events (MachineId, Type, Code, Message, Ts) VALUES
(3,'START',NULL,'Robot online',                   DATEADD(HOUR,-120,SYSUTCDATETIME())),
(3,'MAINT','M10','Scheduled maintenance',         DATEADD(HOUR,-100,SYSUTCDATETIME())),
(3,'START',NULL,'Maintenance complete',           DATEADD(HOUR,-98, SYSUTCDATETIME())),
(3,'ERROR','E12','Hydraulic pressure fault',      DATEADD(HOUR,-48, SYSUTCDATETIME()));
GO

/* -------------------------------------------
   Seed TELEMETRY (hourly for last 7 days)
   - temperature 25–85°C, vibration 0.1–6.0
   - throughput 40–240 units/hour
   ------------------------------------------- */

DECLARE @from DATETIME2 = DATEADD(DAY,-7,SYSUTCDATETIME());
DECLARE @to   DATETIME2 = SYSUTCDATETIME();

;WITH Hours AS (
    SELECT @from AS Ts
    UNION ALL
    SELECT DATEADD(HOUR,1,Ts) FROM Hours WHERE DATEADD(HOUR,1,Ts) <= @to
),
Base AS (
    SELECT m.Id AS MachineId, h.Ts
    FROM dbo.Machines m
    CROSS JOIN Hours h
)
INSERT INTO dbo.Telemetry (MachineId, Ts, Temperature, Vibration, Throughput)
SELECT
    MachineId,
    Ts,
    -- Random but stable-ish values derived from MachineId + hour
    25 + (ABS(CHECKSUM(NEWID(), MachineId, CONVERT(INT, DATEDIFF(HOUR,'2001-01-01',Ts)))) % 61),                -- 25..85
    0.1 + (ABS(CHECKSUM(NEWID(), MachineId*7, CONVERT(INT, DATEDIFF(HOUR,'2001-01-01',Ts)))) % 60) / 10.0,     -- 0.1..6.0
    40 + (ABS(CHECKSUM(NEWID(), MachineId*11, CONVERT(INT, DATEDIFF(HOUR,'2001-01-01',Ts)))) % 201)            -- 40..240
FROM Base
OPTION (MAXRECURSION 0);
GO

/* -------------------------------------------
   Throughput dip around error windows (optional realism)
   Reduce throughput by ~40% within 2 hours after an ERROR.
   ------------------------------------------- */
UPDATE t
SET Throughput = CAST(Throughput * 0.6 AS INT)
FROM dbo.Telemetry t
JOIN dbo.Events e
  ON e.MachineId = t.MachineId
 AND e.Type = 'ERROR'
 AND t.Ts BETWEEN DATEADD(HOUR,0,e.Ts) AND DATEADD(HOUR,2,e.Ts);
GO

-- Quick counts to display after seeding
SELECT 'Machines' AS Entity, COUNT(*) AS Cnt FROM dbo.Machines
UNION ALL SELECT 'Events', COUNT(*) FROM dbo.Events
UNION ALL SELECT 'Telemetry (last 7d)', COUNT(*) FROM dbo.Telemetry;
GO
