drop table if exists articles;
drop table if exists users;

create table articles (
	id integer primary key autoincrement,
	title text not null,
	body text not null,
	upvotes integer default 0,
	downvotes integer default 0
);

create table users (
	id integer primary key autoincrement,
	username text not null,
	email text not null,
	password text not null
);