import imaplib
import email
from email.header import decode_header
import os
from src.state import StateTracker
from src.filters import AttachmentFilter
from imaplib import Internaldate2tuple 
import time

class GmailStatementDownloader:
    """Clase puramente técnica encargada de la descarga vía IMAP."""
    
    def __init__(self, email_address: str, app_password: str):
        self.email_address = email_address
        self.app_password = app_password
        self.mail = None

    def connect(self):
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.mail.login(self.email_address, self.app_password)
        self.mail.select('"[Gmail]/All Mail"')

    def download_statements(
            self, 
            senders_query: str, 
            tracker: "StateTracker", 
            file_filter: "AttachmentFilter", 
            output_dir: str = "inputs"
        ) -> list[str]:
        
        if not self.mail:
            raise ConnectionError("Ejecuta .connect() antes de continuar.")
            
        os.makedirs(output_dir, exist_ok=True)
        downloaded_files = []

        since_date = tracker.get_since_date_for_imap()
        full_query = f"{senders_query} SINCE \"{since_date}\""
        print(f"🔍 Ejecutando Query IMAP: {full_query}")

        status, messages = self.mail.search(None, full_query)
        if status != "OK" or not messages[0]:
            return []

        for mail_id in messages[0].split():
            # 1. Obtener ID único y la Fecha Interna (INTERNALDATE) del correo
            # Pedimos ambas cosas en una sola consulta para ser eficientes
            status, data_meta = self.mail.fetch(mail_id, "(BODY[HEADER.FIELDS (MESSAGE-ID)] INTERNALDATE)")
            if status != "OK" or not data_meta:
                continue
            
            # Inicializamos variables de control
            msg_id = ""
            date_prefix = ""
            
            # Procesamos la respuesta de los metadatos
            for response_part in data_meta:
                if isinstance(response_part, tuple):
                    # Extraer Message-ID de la cabecera
                    if b"MESSAGE-ID" in response_part[0]:
                        header_text = response_part[1].decode('utf-8', errors='ignore')
                        msg_id = header_text.replace("Message-ID:", "").strip()
                    
                    # Extraer INTERNALDATE aportada por el servidor IMAP
                    # La respuesta suele verse como: b'12 (INTERNALDATE "15-Jan-2026 14:32:10 -0500" BODY...)'
                    if b"INTERNALDATE" in response_part[0]:
                        try:
                            # Convertimos la fecha de IMAP a una estructura de tiempo de Python
                            mail_time = Internaldate2tuple(response_part[0])
                            # Formateamos como "YYYYMM" -> Ejemplo: "202601"
                            date_prefix = time.strftime("%Y%m", mail_time)
                        except Exception:
                            date_prefix = ""

            # Si no pudimos obtener el ID, pasamos al siguiente por seguridad
            if not msg_id:
                continue

            # Delegamos la decisión al Tracker de duplicados
            if tracker.is_already_processed(msg_id):
                continue

            # 2. Descargar el cuerpo completo del correo
            status, data_body = self.mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                continue
                
            msg = email.message_from_bytes(data_body[0][1])
            email_has_valid_data = False

            # 3. Procesar adjuntos
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                    continue
                    
                raw_filename = part.get_filename()
                if raw_filename:
                    filename = self._decode_mime_words(raw_filename)
                    
                    # Delegamos la validación del nombre original al Filtro modular
                    if file_filter.is_valid(filename):
                        # MODIFICACIÓN: Si tenemos el prefijo de fecha, se lo agregamos al nombre
                        if date_prefix:
                            new_filename = f"{date_prefix}_{filename}"
                        else:
                            new_filename = filename
                            
                        filepath = os.path.join(output_dir, new_filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        
                        print(f"📥 Descargado: {new_filename}")
                        downloaded_files.append(filepath)
                        email_has_valid_data = True
            
            # 4. Si el correo fue útil, lo reportamos al Tracker
            if email_has_valid_data:
                tracker.mark_as_processed(msg_id)
        
        # Actualizamos la fecha de última ejecución en el tracker y guardamos
        tracker.update_sync_date()
        tracker.save()
        
        return downloaded_files

    def _decode_mime_words(self, s: str) -> str:
        """Soporte para nombres de archivos con tildes o eñes en las cabeceras del correo."""
        decoded = decode_header(s)
        return "".join([t.decode(e or 'utf-8', errors='ignore') if isinstance(t, bytes) else t for t, e in decoded])

    def disconnect(self):
        """Cierra la sesión de forma segura."""
        if self.mail:
            self.mail.close()
            self.mail.logout()
            print("🚪 Sesión de Gmail cerrada.")