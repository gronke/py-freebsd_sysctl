def read_first_line(relative_filename: str) -> str:
    absolute_path = os.path.join(os.getcwd(), relative_filename)
    with open(absolute_path, "r", encoding="UTF-8") as f:
        return f.readline().strip()


try:
    VERSION = read_first_line("VERSION")
except:
    # last git commit SHA is the version
    line = read_first_line(".git/HEAD")
    if line.startswith("ref: ") is False:
        VERSION = line
    else:
        ref = line[5:]
        VERSION = read_first_line(f".git/{ref}")

__version__ = VERSION
