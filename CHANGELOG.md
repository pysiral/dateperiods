# History of changes

## [1.4.0] 2025-09-04

### Added
- Support for python 3.13
- `dateperiod.Dateperiods`: 
  - input data type str ("2024", "2024-09", "2024-09-01")
  - definition level now remembers whether input was year, month or day

### Changed
- Replace legacy setup.py bdist_wheel mechanism by using `pyproject.toml` only. (https://github.com/pypa/pip/issues/6334)
- Python compability tests now from python 3.10 to 3.13 (was 3.7 to 3.11)
- Moved package code to `src` folder
- Duration definition now accepts more keywords (e.g. `daily`, `day`, `P1D` are all equivalent and mean `P1D`)

### Removed
- support for python <= 3.9 (will likely work for python 3.8, 3.9 but not tested nor supported)
- property `type` from `dateperiod.DurationType` (redundant information)

## [1.3.0] 2024-07-22

### Added
- (Monthly) exclusion rules from `PeriodIterator`
- python 3.12 tests

## [1.2.1] 2024-04-09

### Fixed
- pip install now installs packages listed in requirements
- Added required copyright statement for isodate
- supported python versions now correct everywhere

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
