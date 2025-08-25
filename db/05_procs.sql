USE FactoryDB;
GO

-- Latest N logs across the factory (optionally filter by machine)
IF OBJECT_ID('dbo.sp_GetLatestLogs','P') IS NOT NULL DROP PROCEDURE dbo.sp_GetLatestLogs;
GO
CREATE PROCEDURE dbo.sp_GetLatestLogs
    @Top INT = 50,
    @MachineId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@Top)
        e.Id,
        e.MachineId,
        e.Ts,
        e.Type,
        e.Code,
        e.Message,
        m.Name AS MachineName,
        m.Line  AS Line,
        dbo.NormalizeSeverity(e.Type) AS SeverityRank
    FROM dbo.Events e
    INNER JOIN dbo.Machines m ON m.Id = e.MachineId
    WHERE (@MachineId IS NULL OR e.MachineId = @MachineId)
    ORDER BY e.Ts DESC;
END;
GO

-- KPI summary: throughput & error counts per machine over a time window
IF OBJECT_ID('dbo.sp_MachineKpiSummary','P') IS NOT NULL DROP PROCEDURE dbo.sp_MachineKpiSummary;
GO
CREATE PROCEDURE dbo.sp_MachineKpiSummary
    @From DATETIME2,
    @To   DATETIME2
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH ThroughputAgg AS (
        SELECT MachineId, SUM(Throughput) AS TotalThroughput
        FROM dbo.Telemetry
        WHERE Ts BETWEEN @From AND @To
        GROUP BY MachineId
    ),
    ErrorAgg AS (
        SELECT MachineId, COUNT(*) AS ErrorCount
        FROM dbo.Events
        WHERE Type = 'ERROR' AND Ts BETWEEN @From AND @To
        GROUP BY MachineId
    )
    SELECT
        m.Id AS MachineId,
        m.Name,
        m.Line,
        ISNULL(t.TotalThroughput, 0) AS TotalThroughput,
        ISNULL(e.ErrorCount, 0)      AS ErrorCount
    FROM dbo.Machines m
    LEFT JOIN ThroughputAgg t ON t.MachineId = m.Id
    LEFT JOIN ErrorAgg e      ON e.MachineId = m.Id
    ORDER BY m.Id;
END;
GO
