import pandas as pd
import os
import time

from tabula import read_pdf
from docx import Document

from config import *

def main():
    for file in os.listdir(folder_path):
        if file.endswith(".xls"):
            xls_parser(file)
        if file.endswith(".docx"):
            docx_parser(file)
        if file.endswith(".pdf"):
            pdf_parser(file)

def xls_parser(filename: str):
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

def docx_parser(filename: str):
    start_time = time.time()
    doc = Document(f"{folder_path}/{filename}")
    
    # Список для хранения данных таблиц
    all_data = []
    
    # Проходим по каждой таблице в документе
    for table in doc.tables:
        table_data = []
        
        # Проходим по каждой строке в таблице
        for row in table.rows:
            # Извлекаем текст из каждой ячейки в строке
            row_data = [cell.text.strip() for cell in row.cells]
            table_data.append(row_data)  # Добавляем строку в таблицу
        # print(table_data[1:])
    # # Добавляем таблицу в общий список
    # filename = filename.replace(".docx","")
    # # Создаем Excel файл
    # with pd.ExcelWriter(f"{filename}_docx.xls", engine='openpyxl') as writer:
    #     for i, table_data in enumerate(all_data):
    #         # Создаем DataFrame из данных таблицы
    #         df = pd.DataFrame(table_data)
    #         # Записываем DataFrame в Excel файл
    #         df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False, header=False)
    # new_filename = filename.replace(".xls", "")
    # file = pd.read_excel(f"{filename}_docx.xls")
    # lst = []
    # for row in file.itertuples(index=False):
    #     rw = []
    #     for r in row:
    #         if str(r) != "nan" and "          " not in str(r):
    #             rw.append(r)
    #     lst.append(rw)
    new_filename = filename.replace(".xls", "")
    with open(f'{new_filename}_docx.txt', "w", encoding="UTF-8") as f:
        f.write(str(table_data[1:]))
    print(f"time - {time.time()-start_time}sec")


def pdf_parser(filename: str):
    start_time = time.time()
    tables = read_pdf(f"{folder_path}/{filename}", pages='all', multiple_tables=True)
    new_filename = filename.replace(".pdf", "")
    # Создаем Excel файл
    with pd.ExcelWriter(f"{new_filename}_pdf.xls", engine='openpyxl') as writer:
        for i, table in enumerate(tables):
            # Записываем каждую таб  лицу в отдельный лист
            table.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
    file = pd.read_excel(f"{new_filename}_pdf.xls")
    lst = []
    for row in file.itertuples(index=False):
        rw = []
        for r in row:
            if str(r) != "nan" and "          " not in str(r):
                rw.append(r)
        lst.append(rw)
    with open(f'{new_filename}_pdf.txt', "w", encoding="UTF-8") as f:
        f.write(str(lst))
    print(f"time - {time.time()-start_time}sec")

if __name__ == "__main__":
    main()