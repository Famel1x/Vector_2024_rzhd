import pandas as pd
import os
import pdfplumber
from docx import Document

folder_path = 'РЖД train/Выгрузка_маркетинговые списки'

def get_file_type():
    files = os.listdir(folder_path)
    #print(files)
    for file in files:
        if file.endswith(".xls"):
            parse_xls(file)
            continue
            # pass
        if file.endswith(".pdf"):
            parse_pdf(file)
            continue
        if file.endswith(".docx"):
            parse_docx(file)
            continue

def parse_xls(filename: str):
    file = pd.read_excel(f"{folder_path}/{filename}")
    rows = file.loc
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            rw.append(r)
        lst.append(rw)
    # print(len(lst))
    with open('file.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))

def parse_pdf(filename: str):
    with pdfplumber.open(f"{folder_path}/{filename}") as pdf:
        pages = pdf.pages
        for page in pages:
            print(page.extract_table())
def parse_docx(filename: str):
    print("docx")

if __name__ == "__main__":
    get_file_type()
    