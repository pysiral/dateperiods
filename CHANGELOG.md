# History of changes

## [1.2.0] - 2024-04-09

### Added
- code style
- python 3.10 and 3.11 tests

## [1.1.0] - 2022-07-02

### Added
- type hints for all methods
- python 3.8 and 3.9 tests
- representation for all classes

### Changed
- `DateDefinition` and `DurationDefinition` are now public classes

### Fixed
- incorrect assertion in tests prevented successful completion of pipeline
- duration isoformat was non-standard for custom period (but correct), e.g. P6M30D what should be P7M. 