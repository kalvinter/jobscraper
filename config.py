import os

ROOT_DIR = os.getcwd()  # This is your Project Root
CONFIG_PATH = os.path.join(ROOT_DIR, 'configuration.conf')

TITLE_FILTER = {
    "negative": [
        "consultant",
        "senior",
        "praktikant",
        "internship",
        "werkstudent",
        "lead",
        " sap ",
        "praktikant",
        "praktikum",
        " php ",
        "studentenjob"
    ]
}