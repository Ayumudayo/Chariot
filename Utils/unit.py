from Utils.Log import Logger as lg

class unit():
    # Convert Imperial to Metric
    def imperial_to_metric(value, unit):

        if unit == "in":
            return value * 2.54, "cm"
        elif unit == "ft":
            return value * 0.3048, "m"
        elif unit == "yd":
            return value * 0.9144, "m"
        elif unit == "mi":
            return value * 1.60934, "Km"
        elif unit == "gal":
            return value * 3.78541, "L"
        elif unit == "oz":
            return value * 28.3495, "g"
        elif unit == "lb":
            return value * 0.453592, "Kg"
        else:
            lg.error(f'[imperial_to_metric]: {value}, {unit} is an invalid input.')
            return 0, 'ERROR'