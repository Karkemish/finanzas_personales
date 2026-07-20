# src/cleaner.py
import re
from src.cleaners.base_cleaner import BaseCleaner

class BCPCreditosCleaner(BaseCleaner):

    PERIOD_REGEX = r'(?P<fecha_inicio>\d{2}/\d{2}/\d{2}).*?(?P<fecha_fin>\d{2}/\d{2}/\d{2})'
    TRANSACTION_REGEX = r'(?P<fecha_proceso>\d{2}[A-Z]+)\s+(?P<fecha_compra>\d{2}[A-Z]+)\s+(?P<descripcion>[\w\s\.\*\-\&Ñ\/:]+)\s+(?P<tipo>PAGO|CONSUMO)\s+(?P<monto>[\d,]*[\.]\d{2})'
    INFO_EECC_REGEX = r'ESTADO DE CUENTA DE\s+(?P<tipo_eecc>[A-ZÁÉÍÓÚÑ ]+)'
    ACCOUNT_LINE_REGEX = r'(?P<nro_cuenta>[\d\-\*X]{10,25})'
    MONEDA_REGEX = r'(?P<moneda>SOLES|DOLARES)'
    
    def _extract_period(self) -> tuple[str, str] | tuple[None, None]:

        matches = re.search(self.PERIOD_REGEX, self.content)
        if matches:
            fecha_inicio_str = matches.group("fecha_inicio")
            fecha_fin_str = matches.group("fecha_fin")           
            print(f"📍 Fecha Inicio Encontrada: {fecha_inicio_str} | 🏁 Fecha Fin Encontrada: {fecha_fin_str}")
            return fecha_inicio_str, fecha_fin_str

        print("❌ No se encontraron fechas en el formato esperado.")
        return None, None

    def _extract_relevant_blocks(self) -> tuple[list[str], int]:

        list_cont = [line.upper() for line in self.content.split("\n")]
        relevant_blocks = []
        max_string = 0
        for _, line in enumerate(list_cont):
            text = re.search(r'^[\d]{2}[A-Z]{3}', line.strip())
            if text:
                relevant_blocks.append(line.strip())
                max_string = max(max_string, len(line.strip()))
        return relevant_blocks, max_string

    def _extract_information_from_block(self, lines: list[str], max_string_len: int) -> list[dict]:
        
        data = []
        for line in lines:
            matches = re.match(self.TRANSACTION_REGEX, line)
            print(line)
            if matches:
                dict_data = matches.groupdict()
                dict_data["moneda"] = "USD" if len(line) >= (max_string_len - 3) else "PEN"
                dict_data["multiplicador"] = 1 if dict_data["tipo"] == "PAGO" else -1
                dict_data["monto"] = float(dict_data["monto"].replace(",", ""))
                print(dict_data)
                data.append(dict_data)
        return data
    
    def _extract_general_info(self) -> dict:

        info = {
            "tipo_eecc": "DESCONOCIDO",
            "nro_cuenta": "DESCONOCIDO",
            "moneda": "DESCONOCIDO"
        }

        content_upper = self.content.upper()

        match_eecc = re.search(self.INFO_EECC_REGEX, content_upper)
        if match_eecc:
            info["tipo_eecc"] = match_eecc.group("tipo_eecc").strip()
        match_account = re.search(self.ACCOUNT_LINE_REGEX, content_upper)
        if match_account:
            info["nro_cuenta"] = match_account.group("nro_cuenta").strip()
        match_moneda = re.search(self.MONEDA_REGEX, content_upper)
        if match_moneda:
            info["moneda"] = match_moneda.group("moneda").strip()
        return info