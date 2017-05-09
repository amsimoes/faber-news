drop table if exists articles;
drop table if exists users;

create table articles (
	id integer primary key autoincrement,
	title text not null,
	body text not null,
	upvotes int,
	downvotes int
);

create table users (
	id integer primary key autoincrement,
	name text not null,
	email text not null,
	password text not null
);