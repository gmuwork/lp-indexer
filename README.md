# SETUP 
In order to setup and build docker container please execute following commands:
```python
docker-comppse build 
docker-compose up -d 
```

After the container is run in order to use importing script please issue following inside of docker container:
```python
python manage.py import_continous_liquidity_provider_data  --chain=PULSE --dex=PULSEX
```