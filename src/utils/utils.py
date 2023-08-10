from pathlib import Path
import numpy as np
import logging


def check_inputpath(input_path):
    if not isinstance(input_path, Path):
        input_path = Path(input_path)
    if not input_path.exists():
        raise Exception(f"File {input_path} not found. ")
    return input_path


def check_outputpath(output_path):
    if not isinstance(output_path, Path):
        output_path = Path(output_path)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def logging_setup(verbosity, if_write_log, output_path, filename="make_histogram"):
    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARN,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    if if_write_log:
        check_outputpath(output_path)
        logging.basicConfig(
            filename=output_path / f"log.{filename}.txt",
            filemode="w",
            level=log_levels[verbosity],
            format="%(asctime)s  %(levelname)s  %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )
    else:
        logging.basicConfig(
            level=log_levels[verbosity],
            format="%(asctime)s  %(levelname)s  %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )


def calculate_significance(S, B):
    return np.sqrt(2 * ((S + B) * np.log(1 + S / B) - S))


def save_fig(fig, output_folder, output_name):
    output_folder = check_outputpath(output_folder)
    fig.savefig(output_folder / output_name, bbox_inches="tight")
