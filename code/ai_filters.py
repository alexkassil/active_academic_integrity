import click
import os
import mmap
from tqdm import tqdm

def isolate_function(ext, function, data):
    search_starts = []
    search_ends = []
    if ext == "py": # functions and classes
        search_starts = ["def " + function, "class " + function]
        search_ends = [["\ndef", "# def", "\nclass"], ["\nclass", "# class"]]
    elif ext == "scm": # procedures, macros, and streams
        search_starts = ["(define (" + function, "(define-macro (" + function, "(define " + function]
        search_ends = [["\n(define", "; (define"]] * 3
    elif ext == "sql":
        raise NotImplementedError
    for s_start, s_ends in zip(search_starts, search_ends):
        i_start = data.find(s_start)
        if i_start != -1:
            i_end = -1
            for s_end in s_ends:
                i_end = data.find(s_end, i_start + 1)
                if i_end != -1:
                    return data[:data.find("\n")+1] + data[i_start:i_end]
            return data[:data.find("\n")+1] + data[i_start:]

@click.command()
@click.option('--assignment', prompt="Course assignment (example: lab00)")
@click.option('--file', prompt="Assignment filename (example: lab00.py)")
@click.option('--function', prompt="Problem to isolate, comma separated if multiple (example: twenty_twenty)")

# (4) FILTER FUNCTIONS
# Input: "{assignment}_{file}" directory
# Outputs "{assignment}_{file}_{function}" directory
def main(assignment, file, function):
    functions = [f.strip() for f in function.split(",")]
    read_dir = assignment + "_" + file
    write_dirs = [read_dir + "_" + function for function in functions]
    students = os.listdir(read_dir)
    py_files = []
    for write_dir in write_dirs:
        if not os.path.exists(write_dir):
            os.mkdir(write_dir)
    for s in students:
        student_files = os.listdir(read_dir + "/" + s)
        if student_files:
            py_files += [s + "/" + f for f in student_files]
            for write_dir in write_dirs:
                if not os.path.exists(write_dir + "/" + s):
                    os.mkdir(write_dir + "/" + s)
    ext = file[file.rfind(".")+1:]
    for f in tqdm(py_files):
        in_data = ""
        with open(read_dir + "/" + f, 'r', encoding="utf-8") as in_file:
            in_data = in_file.read()
        for function, write_dir in zip(functions, write_dirs):
            filtered_data = isolate_function(ext, function, in_data)
            if filtered_data:
                with open(write_dir + "/" + f, 'w', encoding="utf-8") as out_file:
                    out_file.write(filtered_data)

if __name__ == '__main__':
    main()