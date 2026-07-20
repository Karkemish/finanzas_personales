class AttachmentFilter:
    """Encapsula las reglas de negocio para validar si un adjunto debe ser procesado."""
    
    def __init__(self, allowed_extensions: list[str] = None, prefix: str = ""): # type: ignore
        self.allowed_extensions = allowed_extensions or [".pdf"]
        self.prefix = prefix.upper()

    def is_valid(self, filename: str) -> bool:
        """Determina si el archivo cumple con el criterio comercial."""
        if not filename:
            return False
            
        filename_upper = filename.upper()
        
        # Validar extensión
        has_valid_ext = any(filename_upper.endswith(ext.upper()) for ext in self.allowed_extensions)
        # Validar prefijo
        has_valid_prefix = filename_upper.startswith(self.prefix)
        
        return has_valid_ext and has_valid_prefix