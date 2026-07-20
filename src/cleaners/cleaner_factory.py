from src.cleaners.bcp_ahorros import BCPAhorrosCleaner
from src.cleaners.bcp_creditos import BCPCreditosCleaner
# from src.cleaners.bbva_credito import BBVACreditoCleaner <-- vas importando tus variantes

def get_cleaner(content: str, type_account: str, bank: str):
    """Analiza el texto crudo y retorna la instancia del limpiador correcto."""

    if bank == "BCP" and type_account == "AHORROS":
        return BCPAhorrosCleaner(content)
    
    if bank == "BCP" and type_account == "CREDITOS":
        return BCPCreditosCleaner(content)
        
    # if "TARJETA DE CRÉDITO" in content_upper and "BBVA" in content_upper:
    #     return BBVACreditoCleaner(content)
        
    raise ValueError("❌ Banco o tipo de Estado de Cuenta no soportado aún.")