/*
 *  Transaction test. The first record should not be in table.
 */

insert into dbo.Peoples (FirstName, LastName, BirthDate)
values ('Vladmimir', 'Lenin', '1870-04-22');

insert into dbo.People (FirstName, LastName, BirthDate) -- mistake
values ('Iosif', 'Stalin', '1878-12-17');
