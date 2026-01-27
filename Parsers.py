def scaleParser(data: str):
    try:
        # to be researched difference between G and N
        print(f"scaleParser received data: '{data}'")
        if 'G  ' not in data:
            return None
        print("Data contains 'G  ', proceeding with parsing.")
        data = data.replace('G', '')
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