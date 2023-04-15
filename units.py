def convert_bytes(bytes: int) -> str:
    """
        Convert a number of bytes to a more readable unit
    """
    units: list = ["B", "KB", "MB", "GB"]
    
    i = 0    
    while(bytes / (1024 ** i) > 1024):
        i += 1
    
    return f"{bytes / (1024 ** i):.3f} {units[i]}"
