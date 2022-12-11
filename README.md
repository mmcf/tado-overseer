# tado-overseer
Light automation and management for Tado systems

## Documentation

Full documentation can be found on [Read the Docs](https://tado-overseer.readthedocs.io/en/latest/).


## Development

### Pre-commit hooks
This repo uses [pre-commit](https://pre-commit.com/#intro) to ensure that all code checked in follows proper Python styling guidelines.  The configuration used can be found [here](https://github.com/mmcf/tado-overseer/blob/main/.pre-commit-config.yaml).

### Testing
This repo uses [pytest](https://pytest.org/) to define and execute unit tests.  Tests can run using the `tests` Docker Compose service:

```
docker-compose run tests
```
