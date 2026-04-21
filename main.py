import flet as ft
import json
import os
import random

def main(page: ft.Page):
    # Configuración de la ventana (Simulando Android en escritorio)
    page.title = "Flashcards B2"
    page.window_width = 360
    page.window_height = 740
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK 
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- NUEVO SISTEMA DE GUARDADO CON JSON ---
    ARCHIVO_DATOS = "vocabulario_b2.json"

    def cargar_datos():
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    vocab = cargar_datos()

    def save_data():
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(vocab, f, ensure_ascii=False, indent=4)
    # ------------------------------------------

    # Contenedores de las distintas "pantallas"
    main_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
    study_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, visible=False)
    add_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, visible=False)

    # ---------------------------------------------------------
    # PANTALLA PRINCIPAL
    # ---------------------------------------------------------
    def show_main(e=None):
        main_view.visible = True
        study_view.visible = False
        add_view.visible = False
        page.update()

    # Botones con iconos en formato de texto
    btn_estudiar = ft.Button(
        "Estudiar (Todas)", 
        width=280, height=60, 
        icon="menu_book",  # <--- Cambiado a texto
        on_click=lambda e: start_session("study")
    )
    btn_repasar = ft.Button(
        "Repasar (Fallidas)", 
        width=280, height=60, 
        icon="replay",     # <--- Cambiado a texto
        on_click=lambda e: start_session("review")
    )
    btn_agregar = ft.Button(
        "Agregar Palabras", 
        width=280, height=60, 
        icon="add",        # <--- Cambiado a texto
        on_click=lambda e: show_add()
    )

    main_view.controls = [
        ft.Icon(ft.Icons.SCHOOL, size=80, color=ft.Colors.BLUE_400), # <--- updated for new API
        ft.Text("Mi Vocabulario", size=30, weight="bold"),
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        btn_estudiar,
        btn_repasar,
        btn_agregar
    ]

    # ---------------------------------------------------------
    # PANTALLA: AGREGAR PALABRAS
    # ---------------------------------------------------------
    en_input = ft.TextField(label="Palabra en Inglés", width=300, autofocus=True)
    pron_input = ft.TextField(label="Pronunciación (opcional)", width=300)
    es_input = ft.TextField(label="Traducción en Español", width=300)

    def add_word(e):
        if en_input.value and es_input.value:
            vocab.append({
                "en": en_input.value.strip(),
                "es": es_input.value.strip(),
                "pronunciation": pron_input.value.strip() if pron_input.value else "",
                "review": False,
                "streak": 0
            })
            save_data()
            en_input.value = ""
            pron_input.value = ""
            es_input.value = ""
            page.snack_bar = ft.SnackBar(ft.Text("¡Palabra agregada con éxito!"))
            page.snack_bar.open = True
            en_input.focus()
            page.update()

    add_view.controls = [
        ft.Text("Nueva Palabra", size=25, weight="bold"),
        en_input,
        pron_input,
        es_input,
        ft.Button("Guardar", on_click=add_word, width=300, height=50, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
        ft.TextButton("Volver al Menú", on_click=show_main)
    ]

    def show_add():
        main_view.visible = False
        study_view.visible = False
        add_view.visible = True
        page.update()

    # ---------------------------------------------------------
    # PANTALLA: ESTUDIO / REPASO 
    # ---------------------------------------------------------
    current_list = []
    current_index = 0
    current_mode = ""

    lbl_word = ft.Text("", size=35, weight="bold", text_align=ft.TextAlign.CENTER)
    lbl_pronunciation = ft.Text("", size=20, color=ft.Colors.BLUE_400, text_align=ft.TextAlign.CENTER)
    lbl_translation = ft.Text("", size=25, color=ft.Colors.GREEN_400, visible=False, text_align=ft.TextAlign.CENTER)
    lbl_streak = ft.Text("", size=14, color=ft.Colors.GREY_400, visible=False)

    def next_card():
        nonlocal current_index
        current_index += 1
        if current_mode == "review":
            # Si aún quedan tarjetas por repasar, volvemos a empezar (en orden aleatorio)
            if current_index >= len(current_list) and current_list:
                random.shuffle(current_list)
                current_index = 0
        show_card()

    def mark_correct(e):
        nonlocal current_index
        word_data = current_list[current_index]
        if current_mode == "review":
            word_data["streak"] += 1
            if word_data["streak"] >= 5:
                # Superada: la sacamos de la lista de repaso de esta sesión
                word_data["review"] = False
                word_data["streak"] = 0
                current_list.pop(current_index)
                save_data()
                show_card()
                return
        save_data()
        next_card()

    def mark_incorrect(e):
        word_data = current_list[current_index]
        word_data["review"] = True
        word_data["streak"] = 0
        save_data()
        next_card()

    def reveal_answer(e):
        lbl_translation.visible = True
        btn_reveal.visible = False
        row_actions.visible = True
        page.update()

    btn_reveal = ft.Button("Mostrar Respuesta", on_click=reveal_answer, width=250, height=50)
    btn_correct = ft.Button("Acerté", on_click=mark_correct, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, width=130, height=50)
    btn_incorrect = ft.Button("Fallé", on_click=mark_incorrect, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, width=130, height=50)
    row_actions = ft.Row([btn_incorrect, btn_correct], alignment=ft.MainAxisAlignment.CENTER, visible=False)

    card_container = ft.Container(
        content=ft.Column(
            [lbl_streak, lbl_word, lbl_pronunciation, lbl_translation], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        width=320,
        height=250,
        border_radius=15,
        bgcolor=ft.Colors.SURFACE,
        alignment=ft.Alignment.CENTER,
        padding=20
    )

    study_view.controls = [
        ft.Text("Sesión Activa", size=20, weight="bold"),
        card_container,
        btn_reveal,
        row_actions,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.TextButton("Terminar Sesión", on_click=show_main)
    ]

    def show_card():
        if current_index < len(current_list):
            word = current_list[current_index]
            lbl_word.value = word["en"]
            lbl_pronunciation.value = f"[{word.get('pronunciation', '')}]" if word.get('pronunciation') else ""
            lbl_translation.value = word["es"]
            
            if current_mode == "review":
                lbl_streak.value = f"Racha actual: {word.get('streak', 0)} / 5"
                lbl_streak.visible = True
            else:
                lbl_streak.visible = False

            lbl_translation.visible = False
            btn_reveal.visible = True
            row_actions.visible = False
        else:
            lbl_streak.visible = False
            lbl_word.value = "¡Completado!"
            lbl_pronunciation.value = ""
            lbl_translation.value = "Has terminado todas las tarjetas de esta sesión."
            lbl_translation.color = ft.Colors.BLUE_400
            lbl_translation.visible = True
            btn_reveal.visible = False
            row_actions.visible = False
        page.update()

    def start_session(mode):
        nonlocal current_list, current_index, current_mode
        current_mode = mode
        current_index = 0

        if mode == "study":
            current_list = vocab.copy()
        else:
            current_list = [w for w in vocab if w.get("review") == True]

        random.shuffle(current_list)

        if not current_list:
            page.snack_bar = ft.SnackBar(ft.Text("No hay palabras en esta sección."))
            page.snack_bar.open = True
            page.update()
            return

        main_view.visible = False
        add_view.visible = False
        study_view.visible = True
        show_card()

    page.add(main_view, add_view, study_view)

ft.run(main)