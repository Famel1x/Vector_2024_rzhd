import flet as ft
import flet_utils
import pandas as pd
import datetime
import asyncio

agent = flet_utils.ML_AGEENT()
agent2 = flet_utils.ML_AGEENT2()

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
                            content = ft.Column(controls=[ft.Text("Выгрузка", size = 24)]),
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
        try:
            response_text = agent2.research(client_id)

            id_cell = ft.DataCell(ft.Text(str(client_id), size = 20))
            percentage_cell = ft.DataCell(ft.Text(response_text["churn_probability"], size = 20))
            comment_cell = ft.DataCell(ft.Text(response_text["justification"], size = 20))

            table.rows.append(ft.DataRow(cells=[id_cell, percentage_cell, comment_cell]))
            table.rows.sort(key=lambda row: int(row.cells[1].content.value.strip('%')), reverse=True)
            page.update()
        except:
            pass

    import_btn.disabled = False
    export_btn.disabled = False
    home_button.disabled = False
    pg.visible = False
    page.update()

def export_to_excel(page, table):
    data = {
        "Id": [row.cells[0].content.value for row in table.rows],
        "Процент": [row.cells[1].content.value for row in table.rows],
        "Комментарий": [row.cells[2].content.value for row in table.rows]
    }

    df = pd.DataFrame(data)

    now = datetime.datetime.now()
    time_string = now.strftime("%d_%m_%Y_%H_%M_%S")

    export_path = f"table_data_{time_string}.xlsx"
    df.to_excel(export_path, index=False)

    page.snack_bar = ft.SnackBar(ft.Text(f"Данные успешно сохранены в {export_path}"), open=True)
    page.update()

def main(page: ft.Page):
    page.title = "Flet app"

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Id", size = 24)),
            ft.DataColumn(ft.Text("Процент", size = 24)),
            ft.DataColumn(ft.Text("Комментарий", size = 24))
        ],
        rows=[],
        data_row_min_height = 170,
        data_row_max_height= 170,
        
    )

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

    load_button = ft.ElevatedButton("Загрузить", on_click=lambda e: file_picker.pick_files(),
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
    export_button = ft.ElevatedButton("Выгрузить файл", on_click=lambda e: export_to_excel(page, table), disabled = True,
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
                        height = page.window.height,
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
                            height = page.window.height - 25,
                            auto_scroll=False
                        )
                    ],
                )
            )
        page.update()

    page.on_route_change = route_change
    page.go(page.route)


ft.app(target=main)