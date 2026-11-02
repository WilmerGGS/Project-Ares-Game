import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64
import secrets
import string

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("green")  

class SecureApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cifrar Online Pro - Comunicación Segura")
        self.geometry("850x750")
        
        self.password_var = ctk.StringVar()
        self.password_visible = False
        self.copy_label = None
        
        self.setup_ui()

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="🛡️ Comunicación Segura (AES-256-GCM)", font=("Roboto", 24, "bold"))
        self.title_label.pack(pady=15)

        self.pass_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pass_frame.pack(pady=10, fill="x", padx=40)
        
        self.pass_label = ctk.CTkLabel(self.pass_frame, text="🔑 Clave Secreta:")
        self.pass_label.pack(side="left", padx=10)
        
        self.pass_input_frame = ctk.CTkFrame(self.pass_frame, fg_color="transparent")
        self.pass_input_frame.pack(side="right")
        
        self.gen_pass_btn = ctk.CTkButton(self.pass_input_frame, text="🎲", width=35, fg_color="#4a4a4a", hover_color="#333333", command=self.generate_password)
        self.gen_pass_btn.pack(side="left", padx=(0, 5))

        self.pass_entry = ctk.CTkEntry(self.pass_input_frame, textvariable=self.password_var, show="*", width=250)
        self.pass_entry.pack(side="left")
        
        self.toggle_btn = ctk.CTkButton(self.pass_input_frame, text="👁️", width=35, fg_color="gray30", hover_color="gray20", command=self.toggle_password)
        self.toggle_btn.pack(side="left", padx=(5, 0))

        self.tabview = ctk.CTkTabview(self, width=750, height=500)
        self.tabview.pack(padx=40, pady=10, fill="both", expand=True)
        
        self.tab_text = self.tabview.add("Mensajes / Enlaces")
        self.tab_file = self.tabview.add("Archivos")

        self.setup_text_tab()
        self.setup_file_tab()

    def toggle_password(self):
        if self.password_visible:
            self.pass_entry.configure(show="*")
            self.toggle_btn.configure(text="👁️")
            self.password_visible = False
        else:
            self.pass_entry.configure(show="")
            self.toggle_btn.configure(text="🙈")
            self.password_visible = True

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(24))
        self.password_var.set(password)
        if not self.password_visible:
            self.toggle_password()

    def setup_text_tab(self):
        self.input_tools = ctk.CTkFrame(self.tab_text, fg_color="transparent")
        self.input_tools.pack(fill="x", padx=20, pady=(10,0))
        
        self.btn_paste = ctk.CTkButton(self.input_tools, text="📋 Pegar", width=80, fg_color="#555555", hover_color="#333333", command=self.paste_text)
        self.btn_paste.pack(side="left", padx=5)
        
        self.btn_clear_in = ctk.CTkButton(self.input_tools, text="🗑️ Limpiar", width=80, fg_color="#555555", hover_color="#333333", command=lambda: self.text_input.delete("0.0", "end"))
        self.btn_clear_in.pack(side="left", padx=5)

        self.text_input = ctk.CTkTextbox(self.tab_text, height=120)
        self.text_input.pack(pady=5, padx=20, fill="x")
        self.text_input.insert("0.0", "Escribe aquí tu mensaje o enlace...")

        self.btn_frame_text = ctk.CTkFrame(self.tab_text, fg_color="transparent")
        self.btn_frame_text.pack(pady=10)

        self.encrypt_text_btn = ctk.CTkButton(self.btn_frame_text, text="🔒 Cifrar", command=self.encrypt_text, width=150)
        self.encrypt_text_btn.grid(row=0, column=0, padx=10)

        self.decrypt_text_btn = ctk.CTkButton(self.btn_frame_text, text="🔓 Descifrar", command=self.decrypt_text, width=150, fg_color="#b58332", hover_color="#8c6322")
        self.decrypt_text_btn.grid(row=0, column=1, padx=10)

        self.output_tools = ctk.CTkFrame(self.tab_text, fg_color="transparent")
        self.output_tools.pack(fill="x", padx=20, pady=(10,0))
        
        self.btn_copy = ctk.CTkButton(self.output_tools, text="📄 Copiar Resultado", width=130, fg_color="#1f538d", hover_color="#14375e", command=self.copy_result)
        self.btn_copy.pack(side="left", padx=5)

        self.copy_feedback = ctk.CTkLabel(self.output_tools, text="", text_color="#4CAF50", font=("Roboto", 14, "bold"))
        self.copy_feedback.pack(side="left", padx=10)

        self.text_output = ctk.CTkTextbox(self.tab_text, height=120)
        self.text_output.pack(pady=5, padx=20, fill="x")

    def paste_text(self):
        try:
            clipboard_text = self.clipboard_get()
            self.text_input.delete("0.0", "end")
            self.text_input.insert("0.0", clipboard_text)
        except Exception:
            pass

    def copy_result(self):
        result = self.text_output.get("0.0", "end").strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            self.show_feedback("¡Copiado al portapapeles!")
        else:
            messagebox.showwarning("Vacío", "No hay nada que copiar.")

    def show_feedback(self, message):
        self.copy_feedback.configure(text=message)
        self.after(2000, lambda: self.copy_feedback.configure(text=""))

    def encrypt_text(self):
        text = self.text_input.get("0.0", "end").strip()
        password = self.password_var.get()
        
        if not text or not password:
            messagebox.showwarning("Error", "Debes ingresar un texto y una clave secreta.")
            return

        try:
            salt = os.urandom(16)
            key = self.derive_key(password, salt)
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)
            
            ciphertext = aesgcm.encrypt(nonce, text.encode('utf-8'), None)
            encrypted_data = base64.b64encode(salt + nonce + ciphertext).decode('utf-8')
            
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", encrypted_data)
            self.show_feedback("¡Cifrado con éxito!")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cifrar: {str(e)}")

    def decrypt_text(self):
        encrypted_b64 = self.text_input.get("0.0", "end").strip()
        password = self.password_var.get()

        if not encrypted_b64 or not password:
            messagebox.showwarning("Error", "Debes ingresar el texto cifrado y la clave secreta.")
            return

        try:
            encrypted_data = base64.b64decode(encrypted_b64)
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:28]
            ciphertext = encrypted_data[28:]

            key = self.derive_key(password, salt)
            aesgcm = AESGCM(key)
            
            decrypted_text = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
            
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", decrypted_text)
            self.show_feedback("¡Descifrado con éxito!")
        except Exception:
            messagebox.showerror("Error", "Clave incorrecta o el mensaje ha sido alterado.")

    def setup_file_tab(self):
        self.file_label = ctk.CTkLabel(self.tab_file, text="Ningún archivo seleccionado", font=("Roboto", 14))
        self.file_label.pack(pady=20)

        self.select_file_btn = ctk.CTkButton(self.tab_file, text="📂 Seleccionar Archivo", command=self.select_file)
        self.select_file_btn.pack(pady=10)

        self.btn_frame_file = ctk.CTkFrame(self.tab_file, fg_color="transparent")
        self.btn_frame_file.pack(pady=20)

        self.encrypt_file_btn = ctk.CTkButton(self.btn_frame_file, text="🔒 Cifrar Archivo", command=lambda: self.process_file(True), width=150)
        self.encrypt_file_btn.grid(row=0, column=0, padx=10)

        self.decrypt_file_btn = ctk.CTkButton(self.btn_frame_file, text="🔓 Descifrar Archivo", command=lambda: self.process_file(False), width=150, fg_color="#b58332", hover_color="#8c6322")
        self.decrypt_file_btn.grid(row=0, column=1, padx=10)

        self.selected_filepath = None

    def select_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.selected_filepath = filepath
            filename = os.path.basename(filepath)
            self.file_label.configure(text=f"Archivo: {filename}")

    def process_file(self, encrypt: bool):
        if not self.selected_filepath:
            messagebox.showwarning("Error", "Primero selecciona un archivo.")
            return
        
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Error", "Debes ingresar una clave secreta.")
            return

        # --- NUEVO: Pedir al usuario dónde guardar el resultado ---
        default_name = os.path.basename(self.selected_filepath)
        
        if encrypt:
            # Si ciframos, sugerimos el nombre original + .enc
            output_path = filedialog.asksaveasfilename(
                title="Guardar archivo cifrado como...",
                initialfile=default_name + ".enc",
                defaultextension=".enc",
                filetypes=[("Archivos cifrados", "*.enc"), ("Todos los archivos", "*.*")]
            )
        else:
            # Si desciframos, sugerimos quitarle el .enc
            if default_name.endswith(".enc"):
                default_name = default_name[:-4] # Quita el .enc
            else:
                default_name += ".dec"
                
            output_path = filedialog.asksaveasfilename(
                title="Guardar archivo descifrado como...",
                initialfile=default_name,
                filetypes=[("Todos los archivos", "*.*")]
            )

        # Si el usuario cancela la ventana de guardado, detenemos el proceso
        if not output_path:
            return

        self.title("⏳ Procesando... Por favor espera")
        self.update_idletasks()

        try:
            if encrypt:
                with open(self.selected_filepath, "rb") as f:
                    data = f.read()
                
                salt = os.urandom(16)
                key = self.derive_key(password, salt)
                aesgcm = AESGCM(key)
                nonce = os.urandom(12)
                
                ciphertext = aesgcm.encrypt(nonce, data, None)
                
                # Usamos la ruta que el usuario eligió
                with open(output_path, "wb") as f:
                    f.write(salt + nonce + ciphertext)
                
                messagebox.showinfo("Éxito", f"Archivo cifrado guardado en:\n{output_path}")
            
            else:
                with open(self.selected_filepath, "rb") as f:
                    encrypted_data = f.read()
                
                salt = encrypted_data[:16]
                nonce = encrypted_data[16:28]
                ciphertext = encrypted_data[28:]
                
                key = self.derive_key(password, salt)
                aesgcm = AESGCM(key)
                
                decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
                
                # Usamos la ruta que el usuario eligió
                with open(output_path, "wb") as f:
                    f.write(decrypted_data)
                    
                messagebox.showinfo("Éxito", f"Archivo descifrado guardado en:\n{output_path}")

        except Exception:
            messagebox.showerror("Error", "Fallo al procesar el archivo. Verifica la clave o si el archivo está corrupto.")
        finally:
            self.title("Cifrar Online Pro - Comunicación Segura")

if __name__ == "__main__":
    app = SecureApp()
    app.mainloop()