import os
from src.extractor import extract_text_from_pdf
from src.cleaners.cleaner_factory import get_cleaner
from src.consolidation import consolidate_to_dataframe
from src.state import StateTracker
from src.filters import AttachmentFilter
from src.downloader import GmailStatementDownloader
from config.settings import EMAIL_ADDRESS, EMAIL_PASSWORD, INPUTS_DIR

def main():

    # 1. Inicializar los módulos independientes con sus configuraciones
    tracker = StateTracker(filepath="config/checkpoint.json")
    pdf_filter = AttachmentFilter(allowed_extensions=[".pdf"], prefix="EECC_")
    downloader = GmailStatementDownloader(EMAIL_ADDRESS, EMAIL_PASSWORD)
    
    # 2. Definir los remitentes bancarios objetivo
    senders_query = 'FROM "estadodecuenta@notificacionesbcp.com.pe"'
    
    # 3. Conectar y descargar delegando las reglas al filtro y al tracker
    downloader.connect()
    nuevos_pdfs = downloader.download_statements(
        senders_query=senders_query,
        tracker=tracker,
        file_filter=pdf_filter,
        output_dir=INPUTS_DIR
    )
    downloader.disconnect()
    
    # 4. Procesar los archivos resultantes...
    print(f"✨ Proceso terminado. {len(nuevos_pdfs)} archivos listos para el cleaner.")

    if not nuevos_pdfs:
        nuevos_pdfs = os.listdir("data/inputs/")
    if not nuevos_pdfs:
        print("⚠️ No se encontraron archivos PDF para procesar.")
        return

    for pdf_file in nuevos_pdfs:
        PATH_PDF = os.path.join(INPUTS_DIR, pdf_file)
        print(f"📄 Procesando archivo: {PATH_PDF}")
        raw_text = extract_text_from_pdf(PATH_PDF)
        # Aquí debes especificar el tipo de cuenta y el banco para obtener el limpiador correcto
        type_account = "AHORROS"  if "AHORRO" in PATH_PDF else "CREDITOS"  # Cambia esto según el tipo de cuenta
        bank = "BCP"  # Cambia esto según el banco
        cleaner = get_cleaner(raw_text, type_account, bank)
        result = cleaner.process()
        df_final = consolidate_to_dataframe(result)
        
        # Guardamos localmente antes de sincronizar a OneDrive
        output_path = "data/outputs/movimientos_consolidados.xlsx"
        df_final.to_excel(output_path, index=False)
        print(f"🚀 ¡Excel generado exitosamente en {output_path}!")


if __name__ == "__main__":
    main()
