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
    # отдельно для некоторых столбцов
    # убрать None
    for file in files:
        if file.endswith(".xls"):
            parse_xls(file)
            continue
            pass
        if file.endswith(".pdf"):
            parse_pdf(file)
            continue
            pass
        if file.endswith(".docx"):
            parse_docx(file)
            continue
            pass

def parse_xls(filename: str):
    file = pd.read_excel(f"{folder_path}/{filename}")
    rows = file.loc
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            rw.append(r)
        lst.append(rw)
    with open('data_from_xlsx.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))

def parse_pdf(filename: str):
    if os.path.exists("conv_from_pdf.csv"):
        os.remove("conv_from_pdf.csv")
    start_time = time.time()
    print("started")
    tabula.convert_into(f"{folder_path}/{filename}", "conv_from_pdf.csv", output_format="csv", pages='all')
    file = pd.read_csv("conv_from_pdf.csv")
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            rw.append(r)
        lst.append(rw)
    print(len(lst))
    with open('data_from_pdf.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))
    print(f"time - {time.time()-start_time}sec")

def parse_docx(filename: str):
    start_time = time.time()
    doc = Document(f"{folder_path}/{filename}")
    if os.path.exists("conv_from_docx.csv"):
        os.remove("conv_from_docx.csv")
    with open("conv_from_docx.csv", mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                csv_writer.writerow(row_data)
    file = pd.read_csv("conv_from_pdf.csv")
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            rw.append(r)
        lst.append(rw)
    print(len(lst))
    with open('data_from_docx.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))
    print(f"time - {time.time()-start_time}sec")

if __name__ == "__main__":
    get_file_type()