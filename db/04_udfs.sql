USE FactoryDB;
GO

-- Normalize severity string -> int (for sorting/analytics)
IF OBJECT_ID('dbo.NormalizeSeverity','FN') IS NOT NULL DROP FUNCTION dbo.NormalizeSeverity;
GO
CREATE FUNCTION dbo.NormalizeSeverity (@level NVARCHAR(16))
RETURNS INT
AS
BEGIN
    -- Map common event severities to a rank
    RETURN CASE UPPER(@level)
        WHEN 'ERROR' THEN 3
        WHEN 'MAINT' THEN 2
        WHEN 'STOP'  THEN 1
        WHEN 'START' THEN 0
        ELSE 0
    END;
END;
GO

-- Convert UTC to a local offset in minutes (simple dev utility)
IF OBJECT_ID('dbo.ToLocalTime','FN') IS NOT NULL DROP FUNCTION dbo.ToLocalTime;
GO
CREATE FUNCTION dbo.ToLocalTime (@ts DATETIME2, @offsetMinutes INT)
RETURNS DATETIME2
AS
BEGIN
    RETURN DATEADD(MINUTE, @offsetMinutes, @ts);
END;
GO
