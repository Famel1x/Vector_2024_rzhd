import pandas as pd
import os
import tabula
import time
import csv

from docx import Document
from pdf2docx import Converter

folder_path = 'РЖД train/Выгрузка_маркетинговые списки'

def get_file_type():
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith(".xls"):
            parse_xls(file)
            continue
            #pass
        if file.endswith(".pdf"):
            parse_pdf(file)
            continue
            #pass
        if file.endswith(".docx"):
            parse_docx(file)
            continue
            #pass

def parse_xls(filename: str):
    start_time = time.time()
    new_filename = filename.replace(".xls", "")
    file = pd.read_excel(f"{folder_path}/{filename}")
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            if str(r) != "nan" and "          " not in str(r):
                rw.append(r)
        lst.append(rw)
    with open(f'{new_filename}_xls.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))
    print(f"time - {time.time()-start_time}sec")

def parse_pdf(filename: str):
    new_filename = filename.replace(".pdf", "")
    start_time = time.time()
    tabula.convert_into(f"{folder_path}/{filename}", f"{new_filename}_pdf.csv", output_format="csv", pages='all')
    file = pd.read_csv(f"{new_filename}_pdf.csv")
    lst = parse_csv(filename=f"{new_filename}_pdf")
    with open(f'{new_filename}_pdf.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))
    if os.path.exists(f"{new_filename}_pdf.csv"):
        os.remove(f"{new_filename}_pdf.csv")
    print(f"time - {time.time()-start_time}sec")

def parse_docx(filename: str):
    start_time = time.time()
    new_filename = filename.replace(".docx", "")
    doc = Document(f"{folder_path}/{filename}")
    with open(f"{new_filename}_docx.csv", mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                csv_writer.writerow(row_data)
    file = pd.read_csv(f"{new_filename}_docx.csv")
    lst = parse_csv(filename=f"{new_filename}_docx")
    with open(f'{new_filename}_docx.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))
    if os.path.exists(f"{new_filename}_docx.csv"):
        os.remove(f"{new_filename}_docx.csv")
    print(f"time - {time.time()-start_time}sec")

def parse_csv(filename: str):
    file = pd.read_csv(f"{filename}.csv")
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            if str(r) != "nan":
                try:
                    rw.append(int(r))
                except Exception:
                    rw.append(r)
        lst.append(rw)
    return lst

if __name__ == "__main__":
    get_file_type()