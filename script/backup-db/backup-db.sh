export PGPASSWORD="password"
pg_dump -U postgres -h test.postgres.database.azure.com -d test -F c -b -v -f /home/backup/backup-prod-$(date +\%Y-\%m-\%d).dump