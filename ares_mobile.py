import flet as ft
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64
import secrets
import string

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return kdf.derive(password.encode())

def main(page: ft.Page):
    page.title = "Ares Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # Variables para la UI (SIN expand=True para evitar bugs en móvil)
    password_input = ft.TextField(label="🔑 Clave Secreta", password=True, can_reveal_password=True)
    text_input = ft.TextField(label="Pega el mensaje cifrado o escribe uno nuevo", multiline=True, min_lines=3, max_lines=6)
    text_output = ft.TextField(label="Resultado", multiline=True, min_lines=3, max_lines=6, read_only=True)

    file_info = ft.Text("Ningún archivo seleccionado", color="gray", size=12)
    selected_file = {"path": None, "name": None}
    
    file_picker = ft.FilePicker()
    clipboard = ft.Clipboard()

    # --- LÓGICA DE TEXTO ---
    def encrypt_text(e):
        if not text_input.value or not password_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Faltan datos: escribe un texto y una clave"))
            page.snack_bar.open = True
            page.update()
            return
        try:
            salt = os.urandom(16)
            key = derive_key(password_input.value, salt)
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, text_input.value.encode('utf-8'), None)
            encrypted_data = base64.b64encode(salt + nonce + ciphertext).decode('utf-8')
            text_output.value = encrypted_data
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            page.snack_bar.open = True
            page.update()

    def decrypt_text(e):
        if not text_input.value or not password_input.value:
            return
        try:
            encrypted_data = base64.b64decode(text_input.value)
            salt, nonce, ciphertext = encrypted_data[:16], encrypted_data[16:28], encrypted_data[28:]
            key = derive_key(password_input.value, salt)
            aesgcm = AESGCM(key)
            decrypted_text = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
            text_output.value = decrypted_text
            page.update()
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text("Error: Clave incorrecta o texto alterado"))
            page.snack_bar.open = True
            page.update()

    async def copy_to_clipboard(e):
        await clipboard.set(text_output.value)
        page.snack_bar = ft.SnackBar(ft.Text("¡Copiado al portapapeles!"))
        page.snack_bar.open = True
        page.update()

    # --- LÓGICA DE ARCHIVOS ---
    async def pick_file(e):
        files = await file_picker.pick_files(allow_multiple=False)
        if files:
            selected_file["path"] = files[0].path
            selected_file["name"] = files[0].name
            file_info.value = f"Seleccionado: {files[0].name}"
            page.update()

    async def encrypt_file(e):
        if not selected_file["path"] or not password_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona archivo y clave"))
            page.snack_bar.open = True
            page.update()
            return
        try:
            with open(selected_file["path"], "rb") as f:
                data = f.read()
            salt = os.urandom(16)
            key = derive_key(password_input.value, salt)
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, data, None)
            output_path = selected_file["path"] + ".enc"
            with open(output_path, "wb") as f:
                f.write(salt + nonce + ciphertext)
            
            await file_picker.save_file(file_name=selected_file["name"] + ".enc", src=output_path)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al cifrar: {ex}"))
            page.snack_bar.open = True
            page.update()

    async def decrypt_file(e):
        if not selected_file["path"] or not password_input.value:
            return
        try:
            with open(selected_file["path"], "rb") as f:
                encrypted_data = f.read()
            salt, nonce, ciphertext = encrypted_data[:16], encrypted_data[16:28], encrypted_data[28:]
            key = derive_key(password_input.value, salt)
            aesgcm = AESGCM(key)
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            output_name = selected_file["name"].replace(".enc", "")
            output_path = "dec_" + output_name
            with open(output_path, "wb") as f:
                f.write(decrypted_data)
            
            await file_picker.save_file(file_name=output_name, src=output_path)
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text("Error: Clave incorrecta o archivo dañado"))
            page.snack_bar.open = True
            page.update()

    # --- DISEÑO DE LA INTERFAZ (Estructura Flet 1.0 optimizada para Web/Móvil) ---
    page.add(
        ft.Row([ft.Text("🛡️ Ares Mobile", size=28, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
        password_input,
        ft.Container(
            expand=True,
            content=ft.Tabs(
                selected_index=0,
                length=2,
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label="💬 Mensajes"),
                                ft.Tab(label="📁 Archivos"),
                            ]
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                # Contenido de la Pestaña 1
                                ft.Column(
                                    expand=True,
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=[
                                        text_input,
                                        ft.Row([
                                            ft.Button(content="🔒 Cifrar", on_click=encrypt_text, color="green"),
                                            ft.Button(content="🔓 Descifrar", on_click=decrypt_text, color="orange"),
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        text_output,
                                        ft.Button(content="📋 Copiar al portapapeles", on_click=copy_to_clipboard)
                                    ]
                                ),
                                # Contenido de la Pestaña 2
                                ft.Column(
                                    expand=True,
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=[
                                        ft.Button(content="📂 Seleccionar Archivo del Celular", on_click=pick_file),
                                        file_info,
                                        ft.Row([
                                            ft.Button(content="🔒 Cifrar Archivo", on_click=encrypt_file, color="green"),
                                            ft.Button(content="🔓 Descifrar Archivo", on_click=decrypt_file, color="orange"),
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                    ]
                                ),
                            ]
                        )
                    ]
                )
            )
        )
    )

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 8080))
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=puerto, host="0.0.0.0")