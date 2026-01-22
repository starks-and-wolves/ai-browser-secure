"""
Generate demo manifest index.json

Scans the demos directory and combines all metadata.json files
into a single index.json for the frontend to consume.

Usage:
    python browser_use/scripts/generate_manifest.py --demos-dir ./demo-ui/public/demos
"""

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_manifest(demos_dir: Path) -> dict:
	"""
	Generate manifest by scanning demos directory.

	Args:
		demos_dir: Directory containing demo subdirectories

	Returns:
		Manifest dictionary
	"""
	manifest = {"demos": []}

	# Scan for subdirectories with metadata.json
	for demo_path in demos_dir.iterdir():
		if not demo_path.is_dir():
			continue

		metadata_path = demo_path / "metadata.json"
		if not metadata_path.exists():
			logger.warning(f"No metadata.json in {demo_path.name}, skipping")
			continue

		# Load metadata
		with open(metadata_path, 'r') as f:
			metadata = json.load(f)

		# Add to manifest
		manifest["demos"].append(metadata)
		logger.info(f"Added demo: {metadata['id']}")

	# Sort by mode (traditional, permission, awi)
	mode_order = {"traditional": 0, "permission": 1, "awi": 2}
	manifest["demos"].sort(key=lambda d: mode_order.get(d["mode"], 99))

	return manifest


def main():
	parser = argparse.ArgumentParser(description="Generate demo manifest")
	parser.add_argument("--demos-dir", required=True, help="Demos directory")

	args = parser.parse_args()

	demos_dir = Path(args.demos_dir)
	if not demos_dir.exists():
		logger.error(f"Demos directory not found: {demos_dir}")
		return

	# Generate manifest
	manifest = generate_manifest(demos_dir)

	# Save to index.json
	index_path = demos_dir / "index.json"
	with open(index_path, 'w', encoding='utf-8') as f:
		json.dump(manifest, f, indent=2)

	logger.info(f"✅ Manifest saved: {index_path}")
	logger.info(f"📊 Total demos: {len(manifest['demos'])}")


if __name__ == "__main__":
	main()
