def fahrenheit(temp_celcius):
    fhr = 32 + 1.8 * temp_celcius
    return fhr

def gevoelstemperatuurfun(temp_celcius, windsnelheid, luchtvochtigheid):
    return temp_celcius - luchtvochtigheid / 100 * windsnelheid

def weerrapport(temp_celcius, windsnelheid, luchtvochtigheid):
    gevoelstemperatuur = gevoelstemperatuurfun(temp_celcius, windsnelheid, luchtvochtigheid)

    if gevoelstemperatuur < 0 and windsnelheid > 10:
        return "Het is heel koud en het stormt! Verwarming helemaal aan"
    elif gevoelstemperatuur < 0 and windsnelheid <= 10:
        return "Het is behoorlijk koud! Verwarming aan op de benedenverdieping"
    elif 0 <= gevoelstemperatuur < 10 and windsnelheid > 12:
        return "Het is behoorlijk koud! Verwarming aan op de benedenverdieping"
    elif 0 <= gevoelstemperatuur < 10 and windsnelheid <= 12:
        return "Het is een beetje koud, elektrische kachel op de benedenverdieping aan"
    elif 10 <= gevoelstemperatuur < 22:
        return "Heerlijk weer, niet te koud of te warm"
    else:
        return "Warm! Airco aan!"
    
def weerstation():
    total_temp = 0

    for day in range(1, 8):
        current_day_temp = input("Wat is op dag " + str(day) + " de temperatuur[C]: ")

        if current_day_temp == "" or current_day_temp.isdigit() == False: 
            break

        current_day_temp = int(current_day_temp)

        current_day_windsnelheid = input("Wat is op dag " + str(day) + " de windsnelheid[m/s]: ")

        if current_day_windsnelheid == "":
            break

        current_day_windsnelheid = int(current_day_windsnelheid)

        current_day_vochtigheid = input("Wat is op dag " + str(day) + " de vochtigheid[%]: ")

        if current_day_vochtigheid == "":
            break

        current_day_vochtigheid = int(current_day_vochtigheid)

        total_temp += current_day_temp

        temp_fahrenheit = fahrenheit(current_day_temp)

        rapport = weerrapport(
            current_day_temp,
            current_day_windsnelheid,
            current_day_vochtigheid
        )

        gemiddelde = total_temp / day

        print(weerrapport(current_day_temp, current_day_windsnelheid, current_day_vochtigheid))
        print(f"Het is {current_day_temp:.1f}C ({temp_fahrenheit:.1f}F)")
        print(rapport)
        print(f"Gem. temp tot nu toe is {gemiddelde:.1f}")
        print("======================================")


        total_temp += current_day_temp
        print(total_temp / day)

weerstation()