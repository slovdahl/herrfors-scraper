# Herrfors scraper

## Create InfluxDB databases

```shell
$ influx
> CREATE DATABASE power_consumption;
> CREATE DATABASE power_production;
```

## Usage

### Scrape consumption

```shell
$ poetry shell
$ python -m herrfors_scraper <username> <password> <days> consumption
```

### Scrape production

```shell
$ poetry shell
$ python -m herrfors_scraper <username> <password> <days> production
```

### Writing to InfluxDB

```shell
$ poetry shell
$ python -m herrfors_scraper <username> <password> <days> production | python write-production-to-influxdb.py
```

## Development environment setup

1. Install Poetry
2. `poetry install`
3. `poetry self add poetry-auto-export`

## Manually exporting requirements to requirements.txt

```shell
$ poetry export --format=requirements.txt --without-hashes > requirements.txt
```
