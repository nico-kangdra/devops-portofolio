export PGPASSWORD="password"
pg_restore -h test.postgres.database.azure.com -p 5432 -U postgres -d test -v $1