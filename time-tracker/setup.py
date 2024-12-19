from setuptools import setup, find_packages

setup(
    name="timetracker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0",
        "psutil>=5.9.0",
        "pyobjc-framework-Quartz>=9.0;platform_system=='Darwin'",  # macOS only
        "pyobjc-framework-AppKit>=9.0;platform_system=='Darwin'",  # macOS only
    ],
    entry_points={
        "console_scripts": [
            "timetracker=src.__main__:main",
            "timetracker-setup=scripts.setup_config:main",
        ],
    },
    package_data={
        "": ["config/*.yaml"],  # Include all YAML files in config directory
    },
    include_package_data=True,
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A productivity time tracking application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="productivity, time tracking, activity monitor",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Time Tracking",
    ],
)
