def scaleParser(data: str):
    try:
        if 'N  ' not in data:
            return None
        data = data.replace('N', '')
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        data = data.replace('g', '')
        value = float(data)
        return value
    except ValueError:
        return None
    
def caliperParser(data: str):
    try:
        return float(data.split("+", 1)[1])  # everything after the first +
    except IndexError:
        return None