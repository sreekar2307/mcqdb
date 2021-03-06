from pathlib import Path
import os
import glob
from typing import Tuple
import argparse

parser = argparse.ArgumentParser(description="Filter log files using from and to dates")
parser.add_argument('-f', '--from_date', metavar="", required=True, help="filter logs from")
parser.add_argument('-t', '--to_date', metavar="", required=True, help="filter logs till")
parser.add_argument('-i', "--inventory", metavar="", required=True,
                    help="logs file directory relative or absolute path")
parser.add_argument('-o', "--output_file", metavar="", required=True, help="output file")
args = parser.parse_args()

LOG_FILES_DIRECTORY = args.inventory
META_DATA_FILE = ".metadata"
DELIMITER = ","
FROM_DATE = args.from_date
TO_DATE = args.to_date
OUT_PUT_FILE = args.output_file + ".txt"


# for a file to get first and last rows used while meta data preparation
def get_first_and_last_dates(files: list, delimiter: str) -> list:
    first_n_last_row = []
    for file_name in sorted(files):
        with open(file_name, "rb") as f:
            first_line = f.readline().decode().split(delimiter)[0]

            seek_offset = 0
            f.seek(seek_offset, os.SEEK_END)
            temp = f.read(1)
            while temp != b'\n':
                seek_offset -= 1
                f.seek(seek_offset, os.SEEK_END)
                temp = f.read(1)
            last_line = f.readline().decode().split(delimiter)[0]
            first_n_last_row.append((first_line, last_line, file_name))

    return first_n_last_row


# if logs_dir is modified then new .metadata file will be created
def prepare_meta_data(meta_file_name: str, logs_dir: str) -> list:
    meta_file_path = Path(META_DATA_FILE)
    files_name = get_file_names(logs_dir)
    if not meta_file_path.is_file() or should_modify(files_name, meta_file_name):
        with open(meta_file_name, "w") as meta_file:
            first_n_last_rows = get_first_and_last_dates(
                files_name, DELIMITER)
            for data in first_n_last_rows:
                meta_file.write(f"{data[0]},{data[1]},{data[2]}\r")
        return first_n_last_rows
    else:
        meta_info = []
        with open(meta_file_name, "r") as meta_file:
            for line in meta_file.readlines():
                line = line.splitlines()[0]
                meta_info.append(tuple(line.split(",")))
            return meta_info


# should the meta data be modified


def should_modify(files_path: list, meta_file):
    in_there = max([os.path.getmtime(f) for f in files_path])
    return in_there > os.path.getmtime(meta_file)


# in which files the mentioned FROM and TO will exist


def search_for_files(files: list, from_date: str, to_date: str) -> Tuple[str, str]:
    FROM = find_position(files, from_date, 0, len(files) - 1, "L")
    TO = find_position(files, to_date, 0, len(files) - 1, "R")
    return FROM, TO


def extract_rows_in_file(file_content: list, date, l, r, direction) -> list:
    if l < r:
        mid = (l + r) // 2
        current_date = file_content[mid]
        if current_date > date:
            return extract_rows_in_file(file_content, date, l, mid - 1, direction)
        elif current_date < date:
            return extract_rows_in_file(file_content, date, mid + 1, r, direction)
        elif current_date == date:
            # go to left most
            if mid - 1 >= 0 and file_content[mid - 1] == date and direction == "L":
                return extract_rows_in_file(file_content, date, l, mid - 1, direction)

            # go to right most
            elif mid + 1 < len(file_content) and file_content[mid + 1] == date and direction == "R":
                return extract_rows_in_file(file_content, date, mid + 1, r, direction)
            return mid + 1
    else:
        return l + 1


def get_file_names(dir_name) -> list:
    return [f for f in glob.glob(f"{dir_name}/*.log")]


def find_position(files: list, date: str, l: int, r: int, direction: str) -> str:
    if l < r:
        mid = (l + r) // 2
        if files[mid][0] > date:
            return find_position(files, date, l, mid - 1, direction)
        elif files[mid][1] < date:
            return find_position(files, date, mid + 1, r, direction)
        elif files[mid][0] <= date <= files[mid][1]:
            # go to left most
            if mid - 1 >= 0 and files[mid - 1][1] == date and direction == "L":
                return find_position(files, date, l, mid - 1, direction)

            # go to right most
            elif mid + 1 < len(files) and files[mid + 1][0] == date and direction == "R":
                return find_position(files, date, mid + 1, r, direction)

            return files[mid][2]
    else:
        return files[l][2]


def read_lines(file_name: str):
    file_dates = []
    with open(file_name, "r") as f:
        file_dates.append(f.read(20))
        while f.readline() != "":
            # in ISO format first 20 chars are dates
            temp = f.read(20)
            if temp != "":
                file_dates.append(temp)
    return file_dates


def print_output(from_file: str, to_file: str, from_start: str, to_end: str, file_directory: str):
    files_to_be_printed = [f for f in glob.glob(f"{file_directory}/*.log") if from_file < Path(f).stem < to_file]
    with open(OUT_PUT_FILE, "w") as output:
        with open(Path(f"{file_directory}/{from_file}.log").absolute(), "r") as f:
            output.writelines(f.readlines()[from_start - 1:])
        for f in files_to_be_printed:
            with open(Path(f).absolute(), "r") as f:
                output.writelines(f.readlines())
        with open(Path(f"{file_directory}/{to_file}.log").absolute(), "r") as f:
            output.writelines(f.readlines()[:to_end])


if __name__ == "__main__":
    meta_info = prepare_meta_data(META_DATA_FILE, LOG_FILES_DIRECTORY)
    FROM, TO = search_for_files(meta_info, FROM_DATE, TO_DATE)
    file_content_FROM = read_lines(FROM)  # this might be a bottleneck
    file_content_TO = read_lines(TO)
    if file_content_TO[-1] < FROM_DATE or file_content_FROM[0] > TO_DATE:
        print("No logs found")
    else:
        FROM_ROW_NUMBER = extract_rows_in_file(file_content_FROM, FROM_DATE, 0, len(file_content_FROM) - 1, "L")
        TO_ROW_NUMBER = extract_rows_in_file(file_content_TO, TO_DATE, 0, len(file_content_TO) - 1, "R")
        print_output(Path(FROM).stem, Path(TO).stem, FROM_ROW_NUMBER, TO_ROW_NUMBER, LOG_FILES_DIRECTORY)

