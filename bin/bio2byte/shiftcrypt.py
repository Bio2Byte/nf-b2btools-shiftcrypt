#!/usr/bin/env python

import argparse
import json
import logging
import os
from logging.handlers import RotatingFileHandler

from b2bTools.nmr.shiftCrypt.shiftCrypt import Standalone as ShiftCrypt


def format_floats(obj, precision=3):
    """
    Recursively format float values in a dictionary or list to the specified decimal precision.
    Handles float values that are stored as strings.

    :param obj: The dictionary or list to format.
    :param precision: Number of decimal places to format float values to.
    :return: The same structure with formatted float values.
    """
    if isinstance(obj, dict):
        return {k: format_floats(v, precision) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [format_floats(elem, precision) for elem in obj]
    elif isinstance(obj, str):
        try:
            # Try converting string to a float
            float_value = float(obj)
            # If successful, format it and return the string representation
            return f"{round(float_value, precision):.{precision}f}"
        except ValueError:
            # If conversion fails, return the original string
            return obj
    elif isinstance(obj, float):
        # Handle float values directly
        return round(obj, precision)
    else:
        return obj


# Set up logging
def setup_logging(log_file: str):
    """
    Configure logging to output to both standard output and a log file.
    """
    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set default level to debug for detailed tracking

    # Create handlers for standard output and file
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(log_file, maxBytes=2000, backupCount=5)

    # Set log level for handlers
    console_handler.setLevel(logging.DEBUG)  # Info level for console
    file_handler.setLevel(logging.DEBUG)  # Debug level for file

    # Create formatters and add them to the handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def run_shiftcrypt(
    logger,
    file_path: str,
    model: str = "1",
    is_star_file: bool = False,
    original_numbering: bool = True,
    output_file: str = None,
):
    """
    Run ShiftCrypt on the provided file and save results to a JSON file.

    :param file_path: Path to the NEF or NMR-STAR file
    :param model: Model type (1, 2, 3) based on atom set
    :param is_star_file: Whether the input file is NMR-STAR (True) or NEF (False)
    :param original_numbering: Whether to use original sequence numbering
    :param output_file: Path to save the output JSON. If None, uses the input file's base name.
    :raises FileNotFoundError: If the file_path does not exist
    :raises ValueError: If an invalid model is provided
    """
    valid_models = {"1", "2", "3"}

    logger.info(
        f"Starting ShiftCrypt with model: {model}, is_star_file: {is_star_file}, original_numbering: {original_numbering}"
    )

    # Check file existence and model validity
    if not os.path.isfile(file_path):
        logger.error(f"Input file '{file_path}' does not exist.")
        raise FileNotFoundError(f"Input file '{file_path}' does not exist.")

    if model not in valid_models:
        logger.error(f"Invalid model '{model}'. Choose from {valid_models}.")
        raise ValueError(f"Invalid model '{model}'. Choose from {valid_models}.")

    # Initialize ShiftCrypt and run the API
    sc = ShiftCrypt()

    try:
        logger.debug(f"Running ShiftCrypt on file: {file_path}")
        results_dict = sc.api_shiftcrypt(
            file_path, model, is_star_file, original_numbering
        )
        if not results_dict["results"]:
            raise RuntimeError("ShiftCrypt failed: no results found")

    except Exception as e:
        logger.error("ShiftCrypt failed", exc_info=True)
        raise RuntimeError(f"ShiftCrypt failed: {e}")

    # Set output file name if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = f"{base_name}_shiftcrypt_results.json"

    # Write the results to a JSON file
    try:
        # Format floats with 3 decimal places
        logger.info(f"Format {output_file} to use floats with 3 decimal places")
        formatted_results_dict = format_floats(results_dict, precision=3)

        with open(output_file, "w") as fp:
            json.dump(formatted_results_dict, fp, indent=4)
        logger.info(f"Results saved to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write output file '{output_file}': {e}", exc_info=True)
        raise IOError(f"Failed to write output file '{output_file}': {e}")


def parse_arguments():
    """
    Parse command-line arguments using argparse.
    """
    parser = argparse.ArgumentParser(
        description="Run ShiftCrypt on a NEF or NMR-STAR file and output results as a JSON file."
    )

    # Required argument: file_path
    parser.add_argument("file_path", type=str, help="Path to the NEF or NMR-STAR file")

    # Optional arguments
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        choices=["1", "2", "3"],
        default="1",
        help="Model type: '1' (Full atom set), '2' (H, HA, CA, N, CB, C atoms), '3' (CA, N, H atoms). Default is '1'.",
    )
    parser.add_argument(
        "-s",
        "--is_star_file",
        action="store_true",
        dest="is_star_file",
        default=False,
        help="Specify if the input file is an NMR-STAR file. Default is False (NEF file).",
    )
    parser.add_argument(
        "-o",
        "--original_numbering",
        action="store_true",
        help="Use original sequence numbering, if available. Default is True.",
    )
    parser.add_argument(
        "-f",
        "--output_file",
        type=str,
        default=None,
        help="Path to the output JSON file. If not provided, the script will generate one based on the input file name.",
    )
    parser.add_argument(
        "-l",
        "--log_file",
        type=str,
        dest="log_file",
        default="shiftcrypt.log",
        help="Path to the log file. Default is 'shiftcrypt.log'.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Log the start of execution
    print(
        f"Starting ShiftCrypt script execution for {args.file_path} writing logs in {args.log_file}"
    )

    # Set up logging
    logger = setup_logging(args.log_file)

    # Call the main function with parsed arguments
    try:
        run_shiftcrypt(
            logger=logger,
            file_path=args.file_path,
            model=args.model,
            is_star_file=args.is_star_file,
            original_numbering=args.original_numbering,
            output_file=args.output_file,
        )

        logger.info("ShiftCrypt script execution completed")

    except Exception:
        logger.critical("An unrecoverable error occurred", exc_info=True)
        logger.info("ShiftCrypt script execution failed")

        raise
