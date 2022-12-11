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
    args = parser.parse_args()

    logging.basicConfig(
        level="INFO", format="%(asctime)s [%(name)s] %(levelname)s - %(message)s"
    )

    om = TadoOffsetsManager()
    om.apply_offset_changes(dry_run=args.dry_run)
