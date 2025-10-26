# Pyright Configuration

This project uses Pyright for static type checking with a dedicated configuration file.

## Configuration File

The Pyright configuration is defined in `pyrightconfig.json` at the project root, separate from the `pyproject.toml` file.

## Key Settings

### Paths
- **Include**: `src/` directory
- **Exclude**: Common build artifacts, caches, and test directories
- **Extra Paths**: `src/` for proper module resolution

### Type Checking
- **Mode**: `standard` (balanced strictness)
- **Python Version**: 3.12
- **Platform**: Linux

### Warnings Enabled
- Missing imports and type stubs
- Unused imports, classes, functions, variables
- Optional member access and calls
- Incompatible method/variable overrides
- Missing parameter types
- Unnecessary type checks and casts

### Django-Specific Settings
- **Ignore**: `migrations/`, `settings/`, `static/`, `media/` directories
- **Define Constant**: `DEBUG = true` for Django development

## Usage

### VS Code Integration
If using VS Code with the Pylance extension, Pyright will automatically use this configuration.

### Command Line
```bash
# Install Pyright globally
npm install -g pyright

# Run type checking
pyright

# Run with specific configuration
pyright --config pyrightconfig.json
```

### CI/CD Integration
Add to your CI pipeline:
```yaml
- name: Type Check
  run: |
    npm install -g pyright
    pyright
```

## Configuration Benefits

1. **Separation of Concerns**: Type checking config separate from build config
2. **Django Optimized**: Ignores Django-specific directories that don't need type checking
3. **Comprehensive Warnings**: Catches common Python type issues
4. **Version Specific**: Configured for Python 3.12 features
5. **CI/CD Ready**: Can be easily integrated into automated workflows

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in `extraPaths`
2. **Django Settings**: Use `defineConstant` for Django-specific constants
3. **Missing Stubs**: Install type stubs for external libraries:
   ```bash
   pip install types-redis types-requests
   ```

### VS Code Settings
Add to your VS Code `settings.json`:
```json
{
  "python.analysis.typeCheckingMode": "standard",
  "python.analysis.autoSearchPaths": true,
  "python.analysis.extraPaths": ["src"]
}
```
