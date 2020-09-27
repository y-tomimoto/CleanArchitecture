set client_encoding = 'UTF8';

create table test_table (
  memo_id serial primary key,
  memo varchar not null,
  memo_author varchar not null
);