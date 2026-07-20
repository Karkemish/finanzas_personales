import hashlib
from abc import ABC, abstractmethod

class BaseCleaner(ABC):
    """Clase abstracta que define la estructura para cualquier extractor de banco."""
    
    MONTH_MAPPING = {
        "ENE": "01", "FEB": "02", "MAR": "03", "ABR": "04", "MAY": "05", "JUN": "06",
        "JUL": "07", "AGO": "08", "SET": "09", "OCT": "10", "NOV": "11", "DIC": "12"
    }

    def __init__(self, content: str):
        self.content = content
        self.period = (None, None)

    def process(self) -> dict:
        
        self.period = self._extract_period()
        if not self.period[0]:
            return {}
        
        lines, max_len = self._extract_relevant_blocks()
        raw_data = self._extract_information_from_block(lines, max_len)
        return self._build_final_transactions(raw_data)

    # Métodos abstractos: CADA BANCO OBLIGATORIAMENTE DEBE IMPLEMENTAR EL SUYO
    @abstractmethod
    def _extract_period(self) -> tuple[str, str] | tuple[None, None]: pass

    @abstractmethod
    def _extract_relevant_blocks(self) -> tuple[list[str], int]: pass

    @abstractmethod
    def _extract_information_from_block(self, lines: list[str], max_string_len: int) -> list[dict]: pass

    @abstractmethod
    def _extract_general_info(self) -> dict: pass

    def _hash_account_number(self, nro_cuenta: str) -> str:
        """
        Toma el número de cuenta/tarjeta sucio, lo normaliza 
        y devuelve un hash SHA-256 corto y seguro.
        """
        if not nro_cuenta or nro_cuenta == "DESCONOCIDO":
            return "DESCONOCIDO"
            
        # 1. Normalizamos: quitamos espacios, saltos de línea y pasamos a mayúsculas
        clean_nro = nro_cuenta.strip().replace(" ", "").upper()
        
        # 2. Generamos el hash SHA-256
        hash_object = hashlib.sha256(clean_nro.encode('utf-8'))
        hash_completo = hash_object.hexdigest()
        
        # 3. Retornamos una versión corta (primeros 12 caracteres) 
        # Es más que suficiente para identificar tu cuenta en Excel y se ve más limpio
        return f"HASH_{hash_completo[:12].upper()}"

    # Métodos comunes: Se heredan tal cual para ahorrar código
    def _parse_month(self, date_str: str) -> tuple[str, str]:
        
        date_str = date_str.strip()
        day = date_str[:2]
        month_abbr = date_str[2:]
        month = self.MONTH_MAPPING.get(month_abbr, "00")  # Default to '00' if month abbreviation is not found
        return day, month

    def _build_final_transactions(self, raw_data: list[dict]) -> dict:
        
        transaction = []

        anio_start = self.period[0].split("/")[-1] # type: ignore
        anio_end = self.period[1].split("/")[-1] # type: ignore
        
        change_anio = False
        last_month = None

        info_general = self._extract_general_info()

        for item in raw_data:
            day, month = self._parse_month(item["fecha_compra"])

            if last_month == "12" and month == "01":
                change_anio = True
                print(f"🔄 ¡Salto de año detectado! Transición de Diciembre ({anio_start}) a Enero ({anio_end}).")
            
            last_month = month
            anio = anio_end if change_anio else anio_start
            fecha_compra = f"{day}/{month}/20{anio}"

            tipo = item.get("tipo", "").strip().upper()
            tipo = "PAGO" if (tipo == "PAGO" or item.get("multiplicador") == 1) else "CONSUMO"

            moneda = item.get("moneda", "").strip().upper()
            moneda = moneda if moneda != "" else info_general.get("moneda", "").strip().upper().replace("DOLARES", "USD").replace("SOLES", "PEN")

            transaction.append({
                "fecha_compra": fecha_compra,
                "descripcion": item["descripcion"].strip(),
                "tipo": tipo,
                "monto": item["monto"] * item["multiplicador"],
                "moneda": moneda,
                "categoria": "POR DEFINIR"
            })
        
        info_general.pop('moneda', None)
        info_general["nro_cuenta"] = self._hash_account_number(info_general.get("nro_cuenta", ""))

        result = {
            "info_general": info_general,
            "transactions": transaction
        }

        return result