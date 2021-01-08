drop schema blog;
create schema if not exists blog;
use blog;

create table if not exists user(
id varchar(20) primary key,
username varchar(70) not null,
fName varchar(50),
mName varchar(50),
lName varchar(59),
email varchar(70) not null unique,
photo varchar(75),
password_plain varchar(50) not null,
password_hash varchar(50) not null,
registerDate datetime default CURRENT_TIMESTAMP(),
lastLogin datetime default CURRENT_TIMESTAMP(),
`intro` text,
`profile` text
);

create table if not exists posts(
post_id bigint auto_increment primary key,
author_id varchar(20) not null,
title varchar(100) not null,
post_date datetime not null default CURRENT_TIMESTAMP(),
content text,
view_times int default 0,
thumbs_up bigint default 0,
foreign key(author_id) references user(id)
);

create table if not exists post_comments(
comment_id bigint auto_increment primary key,
post_id bigint,
comment_author_id varchar(20),
content text not null,
published_date datetime not null default CURRENT_TIMESTAMP(),
comment_title varchar(100),
thumbs_up int default 0,
foreign key(post_id) references posts(post_id),
foreign key(comment_author_id) references user(id)
);

create table if not exists category(
category_id int primary key,
category_name varchar(75) not null
);

create table if not exists post_category(
category_id int,
post_id bigint,
primary key(category_id, post_id),
foreign key(category_id) references category(category_id),
foreign key(post_id) references posts(post_id)
);

create table if not exists oauth(
social_id varchar(100) primary key,
email varchar(70) not null,
id varchar(20),
register_date datetime default CURRENT_TIMESTAMP(),
foreign key(id) references user(id)
);

create table if not exists follow(
follower_id varchar(20),
following_id varchar(20),
primary key(follower_id, following_id),
foreign key(follower_id) references User(id),
foreign key(following_id) references User(id)
);

alter table user drop index email;

