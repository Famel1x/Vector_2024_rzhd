import flet as ft
import flet_utils
import pandas as pd
import time
import asyncio
import random

agent = flet_utils.ML_AGEENT()

ch_title = ["Интересы", "Обращения", "Объемы перевозок"]
checkbox_list = [ft.Checkbox(f"Таблица {lb}") for lb in ch_title]
pg = ft.ProgressRing(visible = False)
inp = ft.TextField(expand = True, 
                   border_color=ft.colors.GREY,
                   focused_border_color=ft.colors.WHITE,
                   border_width=2,
                   focused_border_width=3
    )
result = ft.Text("", size = 20)
button = ft.OutlinedButton(on_click = lambda e: click(e, inp, result),
                            content = ft.Column(controls=[ft.Text("Ввод", size = 24)]),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
buttonToGoIE = ft.OutlinedButton(on_click = lambda e: e.page.go("/table"),
                            content = ft.Column(controls=[ft.Text("Таблица", size = 24)]),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
home_button = ft.ElevatedButton("Назад", on_click=lambda e: e.page.go("/"),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))

def click(e, inp, text):
    pg.visible = True
    buttonToGoIE.disabled = True
    text.value = ""
    e.page.update()
    text.value = agent.research(inp.value)
    pg.visible = False
    buttonToGoIE.disabled = False
    e.page.update()

# Функция для имитации запроса на сервер
def fetch_data(client_id):
    # Эмуляция текста ответа от сервера (JSON-строка или текстовый формат)
    response_text = f'{{"id": {client_id}, "percentage": {random.randint(0, 100)}, "comment": "Комментарий для клиента {client_id}"}}'
    return response_text

# Функция для обработки ответа и извлечения данных
def parse_response(response_text):
    # Пример парсинга данных из текстового ответа
    data = eval(response_text)  # Используем eval для преобразования строки в словарь
    client_id = data["id"]
    percentage = data["percentage"]
    comment = data["comment"]
    return client_id, percentage, comment

async def process_file(file_path, table, page, import_btn, export_btn):
    df = pd.read_excel(file_path)

    if 'id' not in df.columns:
        page.snack_bar = ft.SnackBar(ft.Text("Файл должен содержать столбец 'id'"), open=True)
        page.update()
        return

    import_btn.disabled = True
    home_button.disabled = True
    pg.visible = True
    page.update()

    table.rows.clear()

    for client_id in df["id"]:
        response_text = fetch_data(client_id)

        id_value, percentage, comment = parse_response(response_text)

        id_cell = ft.DataCell(ft.Text(str(id_value), size = 20))
        percentage_cell = ft.DataCell(ft.Text(f"{percentage}%", size = 20))
        comment_cell = ft.DataCell(ft.Text(comment, size = 20))

        table.rows.append(ft.DataRow(cells=[id_cell, percentage_cell, comment_cell]))
        table.rows.sort(key=lambda row: int(row.cells[1].content.value.strip('%')), reverse=True)
        page.update()

    import_btn.disabled = False
    export_btn.disabled = False
    home_button.disabled = False
    pg.visible = False
    page.update()

def export_to_excel(table):
    data = {
        "Id": [row.cells[0].content.value for row in table.rows],
        "Процент": [row.cells[1].content.value for row in table.rows],
        "Комментарий": [row.cells[2].content.value for row in table.rows]
    }

    df = pd.DataFrame(data)

    time_string = time.current_time.strftime("%d-%m-%Y %H:%M:%S")
    export_path = f"table_data_{time_string}.xlsx"
    df.to_excel(export_path, index=False)
    print(f"Данные успешно сохранены в {export_path}")

def main(page: ft.Page):
    page.title = "Flet app"

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Id", size = 24)),
            ft.DataColumn(ft.Text("Процент", size = 24)),
            ft.DataColumn(ft.Text("Комментарий", size = 24))
        ],
        rows=[],
    )

        # Обработчик загрузки файла
    def process_upload(event):
        if event.files:
            file_path = event.files[0].path
            if not file_path.endswith(('.xlsx', '.xls')):
                page.snack_bar = ft.SnackBar(ft.Text("Пожалуйста, выберите Excel-файл (.xlsx или .xls)"), open=True)
                page.update()
                return
            
            asyncio.run(process_file(file_path, table, page, load_button, export_button))

    file_picker = ft.FilePicker(on_result=process_upload)

    page.overlay.append(file_picker)

    load_button = ft.ElevatedButton("Загрузить Excel-файл", on_click=lambda e: file_picker.pick_files(),
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
    export_button = ft.ElevatedButton("Выгрузить файл", on_click=lambda e: export_to_excel(table), disabled = True,
                                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))


    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Row(
                        controls = [ft.Text("Введите ID клиента", size = 20), ft.Container(expand = True),
                                    buttonToGoIE, ft.Container(width=25)]
                    ),
                    ft.Row(
                        controls = [inp, pg, ft.Container(width=25), button, ft.Container(width=25)]
                    ),
                    ft.ListView(
                        controls=[
                            result
                        ],
                        height = page.window.height - 20,
                        auto_scroll=False
                    )
                ],
            )
        )
        if page.route == "/table":
            page.views.append(
                ft.View(
                    "/table",
                    [
                        ft.Row(controls=[
                            home_button,
                            ft.Container(expand = True),
                            load_button,
                            export_button,
                            ft.Container(expand = True), pg
                        ]),
                        ft.ListView(
                            controls=[
                                table
                            ],
                            height = page.window.height,
                            auto_scroll=False
                        )
                    ],
                )
            )
        page.update()

    page.on_route_change = route_change
    page.go(page.route)


ft.app(target=main)