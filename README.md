# creating  a  container
# docker run -it --name product-service-con -p 5000:5000 -d product-service /bin/sh
# db_setup -> config -> models -> service -> routes -> main (Calls create_app() from __init__.py)
# Docker Start → Environment Variables → config.py → alembic.ini → Database
                     │
                     └──→ Models → Routes → Services

  my folder structure
  services/
|   |-- product-service/
|   |   |-- app/
|   |   |   |--database
|   |   |   |  |--db_setup.py
|   |   |   |-- __init__.py
|   |   |   |-- config.py
|   |   |   |-- models.py
|   |   |   |-- routes.py
|   |   |   |-- service.py
|   |   |-- main.py
|   |   |-- requirements.txt
|   |   |-- Dockerfile
|   |   |-- alembic.ini
|   |   |-- .env
|--docker-compose.yml

  services/
|   |-- scraping-service/
|   |   |-- app/
|   |   |   |-- scraper.py
|   |   |   |-- routes.py
|   |   |-- main.py
|   |   |-- requirements.txt
|   |   |-- Dockerfile
|--docker-compose.yml

 services/
|   |-- image-recognition-service/
|   |   |-- app/
|   |   |   |-- recognition.py
|   |   |   |-- routes.py
|   |   |-- main.py
|   |   |-- requirements.txt
|   |   |-- Dockerfile
|--gateway/
|   |-- app.py
|   |-- Dockerfile
|   |-- requirement.txt
|   |-- routes.py
|--docker-compose.yml
#scraper
utils -> base -> extractors ->factory -> models - routes -> __init__.py -> main