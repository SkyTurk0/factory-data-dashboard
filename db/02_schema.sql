USE FactoryDB;
GO

IF OBJECT_ID('dbo.Telemetry','U') IS NOT NULL DROP TABLE dbo.Telemetry;
IF OBJECT_ID('dbo.Events','U')    IS NOT NULL DROP TABLE dbo.Events;
IF OBJECT_ID('dbo.Machines','U')  IS NOT NULL DROP TABLE dbo.Machines;
GO

CREATE TABLE dbo.Machines (
  Id INT IDENTITY(1,1) PRIMARY KEY,
  Name NVARCHAR(100) NOT NULL,
  Line NVARCHAR(50) NOT NULL DEFAULT 'LineA',
  Status NVARCHAR(20) NOT NULL CHECK (Status IN ('RUNNING','IDLE','DOWN')),
  InstalledAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Events (
  Id INT IDENTITY(1,1) PRIMARY KEY,
  MachineId INT NOT NULL,
  Ts DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
  Type NVARCHAR(16) NOT NULL,         -- START, STOP, ERROR, MAINT
  Code NVARCHAR(32) NULL,
  Message NVARCHAR(200) NULL,
  CONSTRAINT FK_Events_Machines FOREIGN KEY (MachineId) REFERENCES dbo.Machines(Id)
);

CREATE TABLE dbo.Telemetry (
  Id INT IDENTITY(1,1) PRIMARY KEY,
  MachineId INT NOT NULL,
  Ts DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
  Temperature FLOAT NULL,
  Vibration FLOAT NULL,
  Throughput INT NULL,                -- units/hour snapshot
  CONSTRAINT FK_Tel_Machines FOREIGN KEY (MachineId) REFERENCES dbo.Machines(Id)
);
GO

-- Indexes you’ll show in README (perf)
CREATE INDEX IX_Events_Machine_Ts ON dbo.Events(MachineId, Ts);
CREATE INDEX IX_Telemetry_Machine_Ts ON dbo.Telemetry(MachineId, Ts);
GO
