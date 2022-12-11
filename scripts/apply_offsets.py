import argparse
import logging
from tado.offsets import TadoOffsetsManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="If set, will not make any permanent changes",
    )
    parser.add_argument(
        "-f",
        "--offsets-file",
        dest="offsets_file",
        action="store",
        help="YAML file containing target offsets to set",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level="INFO", format="%(asctime)s [%(name)s] %(levelname)s - %(message)s"
    )

    om = TadoOffsetsManager(offsets_file=args.offsets_file)
    om.apply_offset_changes(dry_run=args.dry_run)
