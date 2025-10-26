# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Workflow Automation System**
  - Modular workflow package for code quality automation
  - Configuration system with persistent settings (`~/.workflow_config.json`)
  - Environment root configuration (separate environment from validation target)
  - Target path configuration (validate code anywhere with any environment)
  - Dynamic argument support in Makefile commands
  - Detailed error output with specific failure information
  - CLI commands: `check`, `full`, `push`, `release`, `tag`, `version`, `deploy`, `config`
  
- **Quality Check Commands**
  - `check`: Ruff linting and formatting validation
  - `full`: Complete validation (Ruff + Pyright + Tests)
  - Support for `--fix` flag to auto-fix issues
  - Support for `--path` flag to specify custom project root
  - Configurable validation targets

- **Git Operations**
  - `push`: Push commits and tags with automatic validation
  - `release`: Create release tags with full validation
  - `tag`: Manage git tags (create, list, delete)
  - `version`: Show current and next version information
  - `deploy`: Complete deployment workflow

- **Configuration Management**
  - `config show`: Display current configuration
  - `config set-env`: Set environment root for consistent validation
  - `config set-target`: Set target path for validation
  - `config clear`: Clear all configuration
  - Persistent configuration across sessions

### Changed

- **CI/CD Simplification**
  - Removed automatic release job from GitHub Actions
  - CI/CD now only runs validation (tests and linting)
  - Releases are now manual via local workflow commands
  
- **Makefile Enhancement**
  - Dynamic argument passing using `$(filter-out $@,$(MAKECMDGOALS))`
  - Catch-all target `%:` to allow flexible argument passing
  - Simplified command structure with shortcuts
  - Better help documentation with examples

- **Code Quality**
  - Modular architecture with clear separation of concerns
  - Core components: `models.py`, `runner.py`, `config.py`
  - Command modules: `check.py`, `push.py`, `tag.py`, `version.py`
  - Utility functions for Git operations

### Removed

- `workflow_dryrun.py` (replaced by modular `workflow` package)
- Automatic version bumping in CI/CD
- Automatic tag creation in CI/CD

### Fixed

- Ruff linting complexity issues (refactored `check_command`)
- Error output now shows specific failed commands
- Better error messages with helpful tips

## [0.2.0] - 2024-12-19

### Added in 0.2.0

- **Settings Management**
  - `DjangoSettingsBaseModel`: Core Django configuration with Pydantic validation
  - `DatabaseSettings`: Database configuration with URL parsing
  - `CelerySettings`: Celery configuration with JSON field support
  - `RedisSettings`: Redis configuration with bidirectional URL conversion
  - `RabbitMQSettings`: RabbitMQ configuration with bidirectional URL conversion
  - `Settings`: Main container class for all settings

- **Queue Management**
  - `kiwi` module with Celery singleton factory
  - Dependency injection container integration
  - Automatic configuration from settings

- **Configuration Features**
  - Multi-environment support (.env files)
  - Automatic database type detection (PostgreSQL, MySQL, SQLite)
  - Automatic broker detection (RabbitMQ, Redis)
  - Flexible configuration (URL-based or field-based)
  - Environment variable priority system

- **Testing Infrastructure**
  - Comprehensive pytest test suite
  - Fixture-based temporary .env file creation
  - Test coverage for all settings components
  - Bidirectional conversion testing

- **Documentation**
  - Feature-based README organization
  - Detailed configuration examples
  - Migration guide for version upgrades
  - Internal settings documentation

### Technical Details

- Built with Pydantic v2 and pydantic-settings
- Support for complex field types (lists, JSON, URLs)
- Custom validators for field parsing and conversion
- Environment variable aliases and validation
- Clean architecture with separation of concerns

## [0.1.0] - 2024-12-18

### Added in 0.1.0

- Initial project structure
- Basic Django settings utilities
- Core configuration management
- Development environment setup

---

## Version History

- **0.3.x**: Workflow automation system, modular architecture, configuration management
- **0.2.x**: Core functionality stable, production-ready settings system
- **0.1.x**: Initial development and prototyping

## Migration Notes

### From 0.2.x to 0.3.x

1. **Workflow System Changes**
   - `workflow_dryrun.py` has been replaced by modular `workflow` package
   - Use `make check` instead of `make workflow-check`
   - Use `make full` instead of `make workflow-run`
   - Use `make version` instead of `make workflow-version`
   - CI/CD no longer creates releases automatically
   - Releases must be done manually via `make release-push`

2. **New Configuration System**
   - Configure environment root: `make config set-env -- --path /path/to/env`
   - Configure target path: `make config set-target -- --path /path/to/target`
   - Configuration persists in `~/.workflow_config.json`
   - View configuration: `make config show`

3. **Makefile Changes**
   - Commands now support dynamic arguments
   - Use pattern: `make command [args...]`
   - Use `--` to separate Make options: `make command -- --flag value`
   - New shortcuts: `check-fix`, `full-fix`, `push-force`, `release-push`

4. **CLI Changes**
   - All commands now support `--path` flag
   - New `config` command for configuration management
   - Better error output with detailed failure information
   - Helpful tips in error messages

### From 0.1.x to 0.2.x

1. **Settings API Changes**
   - Settings classes now use public fields instead of computed fields
   - Field names changed from `_field` to `field` format
   - Improved validation and error handling

2. **Configuration Loading**
   - Enhanced .env file loading with `_env_file` parameter
   - Better environment variable priority handling
   - Improved bidirectional URL conversion

3. **New Features**
   - Automatic service detection capabilities
   - Enhanced Celery integration
   - Comprehensive test coverage

## Contributing

When adding new features or making breaking changes:

1. Update this changelog with clear descriptions
2. Follow semantic versioning principles
3. Include migration notes for breaking changes
4. Update documentation and examples
5. Ensure comprehensive test coverage

## Future Roadmap

### Settings System

- [ ] Additional database backends support
- [ ] Enhanced monitoring and logging configuration
- [ ] Kubernetes and Docker integration
- [ ] Performance optimization features
- [ ] Additional message broker support

### Workflow System

- [ ] Pyright type checking integration improvements
- [ ] Custom validation rules support
- [ ] Pre-commit hooks integration
- [ ] GitHub Actions workflow templates
- [ ] Multi-project validation dashboard
- [ ] Configuration profiles (dev, staging, prod)
- [ ] Plugin system for custom validators
