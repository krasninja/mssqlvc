/*
 *  Create test table.
 */

CREATE TABLE dbo.Peoples
(
	Id int NOT NULL IDENTITY (1, 1),
	FirstName nvarchar(50) NOT NULL,
	LastName nvarchar(50) NOT NULL,
	BirthDate date NOT NULL
);
GO

ALTER TABLE dbo.Peoples ADD CONSTRAINT PK_Peoples PRIMARY KEY CLUSTERED(Id);
GO
