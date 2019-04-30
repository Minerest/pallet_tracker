from datetime import datetime

# utility library to perform calculations

def float_to_time(time_val):
    hour = int(float(time_val))
    time_str = str(time_val)

    try:
        _, mins = time_str.split(".")
        mins = float("." + mins)
        minutes = round(mins * 60)  # the floating point is the percentage of an hour.
    except:
        minutes = 0

    return hour, minutes


def time_to_float():
    hour = datetime.now().hour
    minute = datetime.now().minute
    minute = float(minute/60)
    return hour + minute



# driver
if __name__ == "__main__":
    hour = datetime.now().hour
    minute = datetime.now().minute
    h, m = float_to_time(str(time_to_float()))
    assert(h == hour)
    assert(m == minute)
