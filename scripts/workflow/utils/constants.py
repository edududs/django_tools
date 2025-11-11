"""Constants used across the workflow module."""

import re

# Regex pattern for extracting version from pyproject.toml
VERSION_PATTERN = re.compile(r'version = "([^"]+)"')

# UI constants
SEPARATOR_WIDTH = 80

