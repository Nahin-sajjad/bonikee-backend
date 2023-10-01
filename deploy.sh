#!/bin/sh
git pull
source venv/bin/activate
pip3 install -r requirements/production.txt
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --schema=tenants
python manage.py collectstatic --noinput
deactivate
sudo systemctl restart bonikee-dev
sudo systemctl restart nginx

echo "Deployment completed successfully!"
