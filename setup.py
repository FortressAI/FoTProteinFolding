#!/usr/bin/env python3
"""
FoT Protein Folding Setup Script

Setup script for the Field of Truth protein folding project.
Ensures deterministic installation and dependency management.
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure Python 3.9+
if sys.version_info < (3, 9):
    raise RuntimeError("FoT Protein Folding requires Python 3.9 or higher")

# Read long description from README
def read_file(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    requirements = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

# Package metadata
NAME = "fot-protein-folding"
VERSION = "1.0.0"
DESCRIPTION = "Field of Truth methodology for quantum-inspired protein folding"
LONG_DESCRIPTION = read_file("README.md") if os.path.exists("README.md") else DESCRIPTION
AUTHOR = "FoT Research Team"
AUTHOR_EMAIL = "research@fieldoftruth.org"
URL = "https://github.com/fot-research/protein-folding"
LICENSE = "MIT"

# Package requirements
INSTALL_REQUIRES = read_requirements("requirements.txt")

# Development requirements
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=7.4.3',
        'pytest-cov>=4.1.0',
        'pytest-benchmark>=4.0.0',
        'black>=23.11.0',
        'flake8>=6.1.0',
        'mypy>=1.7.1',
        'pre-commit>=3.5.0',
    ],
    'docs': [
        'sphinx>=7.2.6',
        'sphinx-rtd-theme>=1.3.0',
        'myst-parser>=2.0.0',
    ],
    'jupyter': [
        'jupyter>=1.0.0',
        'jupyterlab>=4.0.8',
        'ipywidgets>=8.1.1',
    ],
    'visualization': [
        'matplotlib>=3.8.1',
        'seaborn>=0.13.0',
        'plotly>=5.17.0',
        'pymol-open-source>=3.0.0',
        'nglview>=3.0.8',
        'py3dmol>=2.0.4',
    ]
}

# All optional dependencies
EXTRAS_REQUIRE['all'] = [
    item for sublist in EXTRAS_REQUIRE.values() 
    for item in sublist
]

# Package classifiers
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Chemistry",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
]

# Keywords
KEYWORDS = [
    "protein folding",
    "quantum computing", 
    "field of truth",
    "computational biology",
    "molecular dynamics",
    "virtue ethics",
    "deterministic computing",
    "ontology",
    "knowledge graphs",
    "neo4j"
]

# Python requirements
PYTHON_REQUIRES = ">=3.9"

# Package data
PACKAGE_DATA = {
    'fot': [
        'ontology/*.ttl',
        'data/*.json',
        'data/*.csv',
        'configs/*.yaml',
    ]
}

# Data files
DATA_FILES = [
    ('ontology', ['ontology/fot_protein_ontology.ttl']),
]

# Entry points for command line tools
ENTRY_POINTS = {
    'console_scripts': [
        'fot-fold=fot.cli:main',
        'fot-setup-neo4j=fot.setup:setup_neo4j',
        'fot-validate=fot.validate:main',
        'fot-benchmark=fot.benchmark:main',
    ],
}

# Custom commands
class DeterministicInstallCommand:
    """Custom installation command that ensures deterministic setup"""
    
    def run(self):
        import subprocess
        import sys
        
        # Verify PyTorch MPS support on Mac M4
        try:
            import torch
            if torch.backends.mps.is_available():
                print("✓ PyTorch Metal Performance Shaders (MPS) support detected")
            else:
                print("⚠ Warning: MPS support not available, falling back to CPU")
        except ImportError:
            print("⚠ Warning: PyTorch not yet installed")
        
        # Set deterministic environment variables
        os.environ['PYTHONHASHSEED'] = '1337'
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'
        
        print("✓ Deterministic environment configured")
        
        # Verify Neo4j connectivity (optional)
        try:
            from neo4j import GraphDatabase
            print("✓ Neo4j driver available")
        except ImportError:
            print("⚠ Warning: Neo4j driver not available")
        
        print("✓ FoT Protein Folding installation completed")

def setup_package():
    """Main setup function"""
    
    # Verify system requirements
    print("Setting up FoT Protein Folding...")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Mac M4 specific checks
    if sys.platform == "darwin":
        import platform
        machine = platform.machine()
        if machine == "arm64":
            print("✓ Apple Silicon (M-series) detected")
        else:
            print(f"⚠ Warning: Expected arm64, got {machine}")
    
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        include_package_data=True,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        python_requires=PYTHON_REQUIRES,
        classifiers=CLASSIFIERS,
        keywords=' '.join(KEYWORDS),
        entry_points=ENTRY_POINTS,
        zip_safe=False,  # Required for package data access
        
        # Custom metadata
        project_urls={
            "Bug Reports": f"{URL}/issues",
            "Source": URL,
            "Documentation": f"{URL}/docs",
            "Funding": "https://github.com/sponsors/fot-research",
        },
        
        # Setuptools options
        options={
            'build_py': {
                'compile': True,
                'optimize': 2,
            },
        },
        
        # Additional metadata for PyPI
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,
        platforms=["macOS", "Linux", "Windows"],
    )

if __name__ == "__main__":
    setup_package()
