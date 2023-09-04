# INTRODUCTION
This project encompasses the indexing and pulling data from blockchain decentralized exchanges liquidity pools.
In the current version we support indexing of PULSEX DEX on Pulse blockchain.

The project exposes two django management commands as the main entry points to the application:
- `import_continous_liquidity_provider_data` - imports new events and transactions for all liquidity pools set for specific dex.
- `query_pickle` - generates pickle file with the data from database for specific liquidity pool.

# SETUP 
In order to setup project, the code is wrapped inside docker image.
Before building the image and starting containers please create sqlite database file in the root directory.
```python
touch evm_lp_db.sqlite3
```
To build the image and start containers please issue following commands:
```python
docker-comppse build 
docker-compose up -d 
```

If you want to run the commands directly without Docker, run the setup script:
```bash
bash ./setup.sh # use --force to force re-creation of the virtual environment
```

# DATA EXPORT/IMPORT
## DESCRIPTION 
In order to import liquidity pool data we expose `import_continous_liquidity_provider_data` django management command.
The command loops through all liquidity pools set in `CHAIN_DEX_LP_CONFIG` settings and imports data from the last
reference block set in database table `lp_pool_block_reference`.

## GUIDES
### ADD NEW LIQUIDITY POOL
In order to add new liquidity pool in the project for the supported DEXes and chains the following has to be done:
- Add new liquidity pool information in `CHAIN_DEX_LP_CONFIG` map located in settings file in [`conf/settings_base.py`](conf/settings_base.py). The liquidity pool information should be added in following format inside the desired DEX config:
```python
"WPLS_DAI": {
    "is_active": True,
    "contract_address": "0xe56043671df55de5cdf8459710433c10324de0ae",
}
```
- After the liquidity pool setting is added new enum for Liquidity pool has to be added in `LiquidityPool` enum located in [`src/enums.py`](src/enums.py). Example enum structure:
```python
class LiquidityPool(enum.Enum):
    WPLS_DAI = 1
```
*NOTE:* After the aforementioned setup is finished please rerun steps to build and start containers.

### IMPORTING DATA FOR LIQUIDITY POOLS
Before importing data we should create initial block reference from which we want to import pool data. It can be done with simple django script inside docker container:
```python
docker exec -it <container_name> bash 
python 
# Inside repl issue following
from src import models
models.LiquidityPoolImporterBlockReference.objects.create(
    chain=1,
    chain_name='PULSE',
    dex=1,   
    dex_name='PULSEX',
    liquidity_pool=1,  # Enum number for liqudity pool
    liquidity_pool_name='WPLS_DAI',
    block_number=17240384,
    block_hash='123',
)
```
In order to import data for all liquidity pools supported on some DEX for specific chain please issue following docker command:
```python
docker exec <container_name> python manage.py import_continous_liquidity_provider_data  --chain=PULSE --dex=PULSEX
```

### EXPORTING DATA TO PICKLE FILES
In order to export data from the database to the desired pickle file please issue following docker command:
```bash
docker exec <container_name> python manage.py query_pickle --chain=PULSE --dex=PULSEX --pool=WPLS_DAI --output-file=my_file.pkl
```


## DATA EXPLORATION
For convenience, we have generated pickle files for each initial liquidity pool in the folder [`liquidity_provider_data`](liquidity_provider_data) with file name format `<POOL_NAME>.pkl`.
In order to explore data please refer to jupyter notebooks located in [`exploration_notebooks`](exploration_notebooks). For each pool there is separate jupyter notebook in format `explore_<POOL_NAME>.ipynb`.
