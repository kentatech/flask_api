#this is where function helpers or validators are kept for clean code in main.py


# Check if a value can be safely converted to an integer
def is_int(value):
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False

# Check if a value can be safely converted to a float (number)
def is_number(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

