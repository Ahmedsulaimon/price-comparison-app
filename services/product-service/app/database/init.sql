-- -- services/product-service/database/init.sql
CREATE USER postgres WITH PASSWORD 'password';
ALTER ROLE postgres WITH SUPERUSER;
ALTER DATABASE product_db OWNER TO postgres;
