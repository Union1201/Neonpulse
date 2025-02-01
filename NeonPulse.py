import os
import subprocess
import json
import flet as ft
from datetime import datetime
import shutil

DATA_FILE = "app_data.json"
LOG_FILE = "app_log.txt"
BACKUP_FOLDER = "backup"
app_list = []
selected_indices = []

def main(page: ft.Page):
    global app_list, selected_indices

    # Настройки страницы
    page.title = "Neon Pulse"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1280
    page.window_height = 800
    page.padding = 0  # фон занимает всё окно
    page.bgcolor = "#0A0A0A"
    page.fonts = {
        "RobotoSlab": "https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600&display=swap"
    }

    # Стили
    theme = {
        "primary": "#00FF88",
        "secondary": "#1A1A1A",
        "accent": "#212121",
        "text": "#FFFFFF",
        "error": "#FF5555"
    }

    # Переменные для выбранной категории и поиска
    current_category = "Все"
    search_query = ""

    # Функция обновления списка с учётом категории и поиска
    def update_app_list():
        filtered_apps = [
            app for app in app_list
            if (current_category == "Все" or app["category"] == current_category)
            and (search_query.lower() in app["name"].lower())
        ]
        app_grid.controls = [
            create_app_card(app, idx)
            for idx, app in enumerate(filtered_apps)
        ]
        page.update()

    # Функция загрузки данных
    def load_data():
        global app_list
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                app_list = json.load(f)
        else:
            app_list = []
        for app in app_list:
            app.setdefault("category", "Depin")
            app["is_running"] = False
        save_data()
        update_app_list()
        page.update()

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(app_list, f, ensure_ascii=False, indent=4)

    # Шапка: логотип по центру
    def create_header():
        logo = ft.Image(
            src=r"E:\Программы DX\StartBatSoft\logo.png",
            width=80,
            height=80,
            fit=ft.ImageFit.CONTAIN
        )
        return ft.Container(
            content=ft.Row(
                controls=[logo],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=ft.Padding(top=10, bottom=10, left=0, right=0)
        )

    def create_app_card(app, index):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Checkbox(
                                value=index in selected_indices,
                                on_change=lambda e, idx=index: toggle_select(idx),
                                fill_color=theme["primary"]
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=theme["primary"],
                                tooltip="Редактировать",
                                on_click=lambda e, idx=index: open_edit_dialog(idx)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.ListTile(
                        title=ft.Text(app["name"], color=theme["text"], size=14, weight="bold"),
                        subtitle=ft.Text(app["category"], color=theme["primary"], size=12),
                        trailing=ft.Icon(
                            name=ft.Icons.CIRCLE,
                            color=ft.Colors.GREEN_300 if app["is_running"] else ft.Colors.RED_300,
                            size=12
                        ),
                        dense=True
                    ),
                    ft.Divider(color=ft.Colors.GREY_800, height=1)
                ],
                spacing=5
            ),
            width=150,
            padding=10,
            border=ft.border.all(1, theme["primary"] if index in selected_indices else ft.Colors.GREY_800),
            border_radius=10,
            bgcolor=theme["accent"],
            on_hover=lambda e: on_card_hover(e, index),
            animate=ft.Animation(300, "easeOut")
        )

    def on_card_hover(e, index):
        e.control.bgcolor = theme["secondary"] if e.data == "true" else theme["accent"]
        e.control.update()

    def create_add_form():
        app_name_input = ft.TextField(label="Название", border_color=theme["primary"], dense=True)
        folder_input = ft.TextField(label="Путь к папке", border_color=theme["primary"], dense=True)
        command_input = ft.TextField(label="Команда", border_color=theme["primary"], dense=True)
        category_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Depin"),
                ft.dropdown.Option("Testnet"),
                ft.dropdown.Option("Node"),
                ft.dropdown.Option("Airdrop")
            ],
            border_color=theme["primary"],
            dense=True,
            value="Depin"
        )

        def add_app(e):
            if all([app_name_input.value, folder_input.value, command_input.value]):
                app_list.append({
                    "name": app_name_input.value,
                    "path": folder_input.value,
                    "command": command_input.value,
                    "category": category_dropdown.value,
                    "is_running": False
                })
                save_data()
                update_app_list()
                app_name_input.value = ""
                folder_input.value = ""
                command_input.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("Приложение добавлено!", color="white"), bgcolor=ft.Colors.GREEN)
                page.snack_bar.open = True
                page.update()

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Добавить приложение", color=theme["primary"], size=16),
                    app_name_input,
                    folder_input,
                    command_input,
                    category_dropdown,
                    ft.FilledButton(
                        "Добавить приложение",
                        icon=ft.Icons.ADD,
                        on_click=add_app,
                        style=ft.ButtonStyle(bgcolor=theme["primary"], color=ft.Colors.BLACK)
                    )
                ],
                spacing=12
            ),
            padding=20,
            bgcolor=theme["accent"],
            border_radius=15,
            width=300
        )

    def open_edit_dialog(index):
        app = app_list[index]
        edit_name = ft.TextField(label="Название", value=app["name"], border_color=theme["primary"], dense=True)
        edit_folder = ft.TextField(label="Путь к папке", value=app["path"], border_color=theme["primary"], dense=True)
        edit_command = ft.TextField(label="Команда", value=app["command"], border_color=theme["primary"], dense=True)
        edit_category = ft.Dropdown(
            options=[
                ft.dropdown.Option("Depin"),
                ft.dropdown.Option("Testnet"),
                ft.dropdown.Option("Node"),
                ft.dropdown.Option("Airdrop")
            ],
            border_color=theme["primary"],
            dense=True,
            value=app["category"]
        )

        def save_edit(e):
            app["name"] = edit_name.value
            app["path"] = edit_folder.value
            app["command"] = edit_command.value
            app["category"] = edit_category.value
            save_data()
            update_app_list()
            dlg.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Изменения сохранены!", color="white"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Редактировать приложение", color=theme["primary"]),
            content=ft.Column(
                controls=[edit_name, edit_folder, edit_command, edit_category],
                spacing=10
            ),
            actions=[
                ft.TextButton("Сохранить", on_click=save_edit),
                ft.TextButton("Отмена", on_click=lambda e: close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dialog():
            dlg.open = False
            page.update()

        page.dialog = dlg
        dlg.open = True
        page.update()

    def update_search(e):
        nonlocal search_query
        search_query = e.control.value or ""
        update_app_list()

    search_field = ft.TextField(
        label="Поиск по приложениям",
        dense=True,
        on_change=update_search
    )

    def toggle_select(index):
        if index in selected_indices:
            selected_indices.remove(index)
        else:
            selected_indices.append(index)
        update_app_list()

    def select_all(e):
        filtered_indices = [idx for idx, app in enumerate(app_list)
                            if current_category == "Все" or app["category"] == current_category]
        selected_indices.clear()
        selected_indices.extend(filtered_indices)
        update_app_list()

    def delete_apps(e):
        global selected_indices
        for index in sorted(selected_indices, reverse=True):
            del app_list[index]
        selected_indices.clear()
        save_data()
        update_app_list()

    def run_apps(e):
        for index in selected_indices:
            app = app_list[index]
            try:
                os.chdir(app["path"])
                subprocess.Popen(f'start cmd /k "{app["command"]}"', shell=True)
                app["is_running"] = True
            except Exception as ex:
                print(f"Ошибка: {str(ex)}")
        save_data()
        update_app_list()

    def backup_data(e):
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
        backup_file = os.path.join(BACKUP_FOLDER, f"backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        shutil.copy(DATA_FILE, backup_file)
        page.snack_bar = ft.SnackBar(ft.Text("Резервная копия создана!", color="white"), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
        page.update()

    def update_category(selected_set):
        nonlocal current_category
        if selected_set:
            current_category = list(selected_set)[0]
        else:
            current_category = "Все"
        update_app_list()

    category_filter = ft.SegmentedButton(
        selected={"Все"},
        segments=[
            ft.Segment(value="Все", label=ft.Text("Все"), icon=ft.Icon(ft.Icons.APPS)),
            ft.Segment(value="Depin", label=ft.Text("Depin"), icon=ft.Icon(ft.Icons.STORAGE)),
            ft.Segment(value="Testnet", label=ft.Text("Testnet"), icon=ft.Icon(ft.Icons.SCIENCE)),
            ft.Segment(value="Node", label=ft.Text("Node"), icon=ft.Icon(ft.Icons.DNS)),
            ft.Segment(value="Airdrop", label=ft.Text("Airdrop"), icon=ft.Icon(ft.Icons.AIR)),
        ],
        on_change=lambda e: update_category(e.control.selected)
    )

    app_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=200,
        spacing=15,
        run_spacing=15
    )

    # Фиксированная левая панель: верхний ряд с поиском, фильтром и кнопками
    left_panel_fixed = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[search_field], spacing=10),
                ft.Row(
                    controls=[
                        category_filter,
                        ft.IconButton(icon=ft.Icons.SELECT_ALL, icon_color=theme["primary"], tooltip="Выбрать все", on_click=select_all),
                        ft.FilledButton("Запуск", icon=ft.Icons.PLAY_ARROW, on_click=run_apps, style=ft.ButtonStyle(bgcolor=theme["primary"], color=ft.Colors.BLACK)),
                        ft.FilledButton("Удалить", icon=ft.Icons.DELETE, on_click=delete_apps, style=ft.ButtonStyle(bgcolor=theme["error"], color=ft.Colors.WHITE)),
                        ft.IconButton(icon=ft.Icons.BACKUP, icon_color=theme["primary"], tooltip="Создать резервную копию", on_click=backup_data)
                    ],
                    spacing=20
                )
            ],
            spacing=15
        ),
        padding=10,
        expand=False
    )

    # Область со списком программ (GridView) с прокруткой
    left_panel_scroll = ft.Column(
        controls=[app_grid],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    left_panel = ft.Container(
        content=ft.Column(
            controls=[left_panel_fixed, left_panel_scroll],
            spacing=10
        ),
        width=800,
        height=page.window_height,  # фиксированная высота панели
        padding=10
    )

    # Правая панель – форма добавления, закреплённая по высоте
    right_panel = ft.Container(
        content=create_add_form(),
        height=page.window_height,
        padding=10
    )

    main_content = ft.Column(
        controls=[
            create_header(),
            ft.Row(
                controls=[
                    ft.Container(content=left_panel, expand=True),
                    ft.VerticalDivider(width=20, color=ft.Colors.GREY_800),
                    right_panel
                ],
                expand=True,
                spacing=20
            )
        ],
        expand=True,
        spacing=10
    )

    # Фоновое изображение с параллакс-эффектом: используем Container с динамическим margin
    bg_container = ft.Container(
        expand=True,
        padding=0,
        margin=ft.Margin(top=0, left=0, right=0, bottom=0),
        content=ft.Image(src=r"E:\Программы DX\StartBatSoft\background.jpg", fit=ft.ImageFit.COVER)
    )

    def on_scroll(e):
        bg_container.margin = ft.Margin(top=-e.offsetY * 0.5, left=0, right=0, bottom=0)
        bg_container.update()

    # Оборачиваем основной контент в ListView с обработчиком прокрутки для параллакса
    content_view = ft.ListView(
        expand=True,
        on_scroll=on_scroll,
        controls=[main_content]
    )

    # Объединяем фон и основной контент в Stack
    page.add(ft.Stack([bg_container, content_view]))
    load_data()

ft.app(target=main)
