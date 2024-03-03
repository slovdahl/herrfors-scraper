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
$ python3 -m herrfors_scraper <username> <password> <days> consumption
```

### Scrape production

```shell
$ python3 -m herrfors_scraper <username> <password> <days> production
```

### Writing to InfluxDB

```shell
$ python3 -m herrfors_scraper <username> <password> <days> production | python3 write-production-to-influxdb.py
```
