#!/usr/bin/env python3

"""CLI argument parsing for probe targets."""

from __future__ import annotations

import argparse
import ipaddress
from urllib.parse import urlparse


def _is_valid_ip(value: str) -> bool:
	try:
		ipaddress.ip_address(value)
		return True
	except ValueError:
		return False


def _is_valid_url(value: str) -> bool:
	parsed = urlparse(value)
	return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def target_arg(value: str) -> str:
	"""Validate a target argument as either URL (http/https) or IP."""
	if _is_valid_ip(value) or _is_valid_url(value):
		return value
	raise argparse.ArgumentTypeError(
		"Target must be a valid IP address or an http/https URL"
	)


def build_parser() -> argparse.ArgumentParser:
	"""Build the argument parser for the probe CLI."""
	parser = argparse.ArgumentParser(description="Probe a website URL or IP")
	parser.add_argument(
		"target",
		type=target_arg,
		help="Website URL (http/https) or IP address",
	)
	return parser


def parse_args() -> argparse.Namespace:
	return build_parser().parse_args()


if __name__ == "__main__":
	args = parse_args()
	print(args.target)
