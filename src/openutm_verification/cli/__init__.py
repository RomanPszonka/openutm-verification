"""
Command Line Interface for OpenUTM Verification Tool.
"""

import argparse
from pathlib import Path

import yaml

from openutm_verification.cli.parser import create_parser
from openutm_verification.config_models import AppConfig
from openutm_verification.core import run_verification_scenarios
from openutm_verification.utils.logging import setup_logging


def main():
    """
    Main entry point for the verification script.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Load configuration
    with open(args.config, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    config = AppConfig(**config_data)

    # Setup logging
    logs_dir = Path(config.reporting.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime, timezone

    run_timestamp = datetime.now(timezone.utc)
    base_filename = f"report_{run_timestamp.strftime('%Y-%m-%dT%H-%M-%SZ')}"
    log_file = setup_logging(logs_dir, base_filename, config.reporting.formats, args.debug)

    # Run verification scenarios
    run_verification_scenarios(config, args.config)

    if log_file:
        from loguru import logger

        logger.info(f"Log file saved to: {log_file}")


if __name__ == "__main__":
    main()
