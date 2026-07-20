# src/cleaner.py
import re
from src.cleaners.base_cleaner import BaseCleaner

class BCPAhorrosCleaner(BaseCleaner):

    PERIOD_REGEX = r'(?P<fecha_inicio>\d{2}/\d{2}/\d{2}).*?(?P<fecha_fin>\d{2}/\d{2}/\d{2})'
    TRANSACTION_REGEX = r'(?P<fecha_proceso>\d{2}[A-Z]+)\s+(?P<fecha_compra>\d{2}[A-Z]+)\s+(?P<descripcion>[\w\s\.\*\-\&Ñ]+)\s{9,}(?P<monto>[\d,]*[\.]\d{2})'
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
        list_cont_cleaned = []
        switch = False
        blocks_count = 0
        max_string = 0

        for i, line in enumerate(list_cont):
            if 'FECHA PROC' in line:
                switch = True
                blocks_count += 1
                print(f"Block {blocks_count} started at line {i}")
                continue
            if 'TOTAL MOVIMIENTO' in line:
                if switch:
                    print(f"Block {blocks_count} ended at line {i}")
                switch = False
                continue
            if switch:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith("---"):
                    list_cont_cleaned.append(line_stripped)
                    max_string = max(max_string, len(line_stripped))
        return list_cont_cleaned, max_string

    def _extract_information_from_block(self, lines: list[str], max_string_len: int) -> list[dict]:
        
        data = []
        for line in lines:
            matches = re.match(self.TRANSACTION_REGEX, line)
            print(line)
            if matches:
                dict_data = matches.groupdict()
                dict_data["multiplicador"] = 1 if len(line) >= (max_string_len - 3) else -1
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