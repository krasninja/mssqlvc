/*
 * Unicode test. Test statement: exec [dbo].[UnicodeTest];
 * https://github.com/krasninja/mssqlvc/issues/1
 */

if exists(select * from sys.procedures where name = N'UnicodeTest')
    drop procedure [dbo].[UnicodeTest]
GO

create procedure dbo.UnicodeTest
as
begin
    select N'✔';
end
