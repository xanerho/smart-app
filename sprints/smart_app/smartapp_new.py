from pathlib import Path

try:
    from apitests import get_weather
except ImportError:
    get_weather = None

# API doesn't provide people so we gotta add them ourselves, haha
def ask_for_people():
    while True:
        try:
            people = int(input("Number of people: "))
            if people < 0:
                print("The number of people cannot be negative")
            else:
                return people
        except ValueError:
            print("Please enter a whole number.")

def ask_for_temperature(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number, for example 19.5")

def aantal_dagen(inputFile):
    try:
        with open(inputFile, "r", encoding="utf-8") as file:
            lines = [line for line in file if line.strip()]

        if not lines:
            print("The input file is empty")

        # the first line is the header so not needed
        return len(lines) - 1
    except FileNotFoundError:
        print("No input file was found.")
        return -1

def read_input_data(inputFile):
    with open(inputFile, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if not lines:
        raise ValueError("The input file is empty")

    all_values = []

    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue

        # split on spaces (considering the layout will be as the one on the canvas site)
        values = line.replace(";", " ").split()

        if len(values) != 5:
            print(f"Skipping line {line_number}: it needs 5 values")
            continue

        try:
            date = values[0]
            people = int(values[1])
            setpoint = float(values[2])
            outside_temperature = float(values[3])
            neerslag = float(values[4])

            if people < 0 or neerslag < 0:
                raise ValueError

            all_values.append([
                date,
                people,
                setpoint,
                outside_temperature,
                neerslag
            ])
        except ValueError:
            print(f"Skipping line {line_number}: invalid values")

    return all_values

def auto_bereken(inputFile, outputFile):
    all_values = []

    source = input(
        "Do you want to use a text file or an API? "
    ).strip().lower()

    if source in ("file", "text", "text file"):
        try:
            all_values = read_input_data(inputFile)
        except FileNotFoundError:
            print("No input file was found")
            return -1
    elif source == "api":
        if get_weather is None:
            print("The weather API could not be imported")
            return -1

        try:
            weather_data = get_weather()

            if weather_data is None or weather_data.empty:
                print("The API did not return any weather data")
                return -1

            for index, weather_day in weather_data.iterrows():
                date = str(weather_day["date"])
                outside_temperature = float(
                    weather_day["temperature_2m_mean"]
                )
                neerslag = float(
                    weather_day["neerslag_sum"]
                )

                people = ask_for_people()
                setpoint = ask_for_temperature(
                    "Temperature setpoint: "
                )

                all_values.append([
                    date,
                    people,
                    setpoint,
                    outside_temperature,
                    neerslag
                ])

        except Exception as error:
            print(f"Something went wrong with the weather API: {error}")
            return -1

    else:
        print("Please enter 'file' or 'api'.")
        return -3

    results = []

    for values in all_values:
        date = values[0]
        people = values[1]
        setpoint = values[2]
        outside_temperature = values[3]
        neerslag = values[4]

        temperature_difference = setpoint - outside_temperature

        if temperature_difference >= 20:
            cv_ketel = 100
        elif temperature_difference >= 10:
            cv_ketel = 50
        else:
            cv_ketel = 0

        ventilatie = min(people + 1, 4)

        bewatering = neerslag < 3

        results.append([
            date,
            cv_ketel,
            ventilatie,
            bewatering
        ])

    # save all results to the output file
    # todo: do i wanna use w or a here
    with open(outputFile, "w", encoding="utf-8") as file:
        for result in results:
            file.write(
                f"{result[0]};{result[1]};"
                f"{result[2]};{result[3]}\n"
            )

    print(f"Successfully saved {len(results)} days.")
    return len(results)

# change an already saved value
def overwrite_settings(outputFile):
    try:
        with open(outputFile, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("The results file does not exist yet.")
        return -1

    results = []

    # read the previously saved settings
    for line in lines:
        values = line.split(";")

        if len(values) != 4:
            print("The results file contains an invalid row.")
            return -1

        try:
            date = values[0]
            cv_ketel = int(values[1])
            ventilatie = int(values[2])
            bewatering_text = values[3].lower()

            if not 0 <= cv_ketel <= 100:
                raise ValueError
            if not 0 <= ventilatie <= 4:
                raise ValueError

            if bewatering_text == "true":
                bewatering = True
            elif bewatering_text == "false":
                bewatering = False
            else:
                raise ValueError

            results.append([
                date,
                cv_ketel,
                ventilatie,
                bewatering
            ])

        except ValueError:
            print("The results file contains invalid settings.")
            return -1

    print("Available dates:")

    for result in results:
        print(result[0])

    date_to_change = input(
        "Which date do you want to change? "
    ).strip()

    selected_result = None

    for result in results:
        if result[0] == date_to_change:
            selected_result = result
            break

    if selected_result is None:
        print("Date not found.")
        return -1

    print("1: cv_ketel (0-100)")
    print("2: ventilatie (0-4)")
    print("3: bewatering (0=False, 1=True)")

    try:
        system = int(input("Which system do you want to change? "))

    except ValueError:
        print("Invalid system.")
        return -3

    if system not in (1, 2, 3):
        print("Choose system 1, 2, or 3.")
        return -3

    new_value = input("Enter the new value: ").strip()

    if system == 1:
        try:
            new_value = int(new_value)
        except ValueError:
            print("The cv_ketel setting must be a whole number.")
            return -3

        if not 0 <= new_value <= 100:
            print("The cv_ketel setting must be between 0 and 100.")
            return -3

        selected_result[1] = new_value

    elif system == 2:
        try:
            new_value = int(new_value)
        except ValueError:
            print("Ventilatie must be a whole number.")
            return -3

        if not 0 <= new_value <= 4:
            print("Ventilatie must be between 0 and 4.")
            return -3

        selected_result[2] = new_value

    else:
        if new_value not in ("0", "1"):
            print("Enter 0 for False or 1 for True.")
            return -3

        selected_result[3] = (new_value == "1")

    # save the updated settings
    try:
        with open(outputFile, "w", encoding="utf-8") as file:
            for result in results:
                file.write(
                    f"{result[0]};{result[1]};"
                    f"{result[2]};{result[3]}\n"
                )

    except (PermissionError, UnicodeError) as error:
        print(f"Could not save the changes: {error}")
        return -1

    print("Setting changed successfully.")
    return 0

# Main menu
def smart_app_controller():
    # find the files in the same folder as this py script
    folder = Path(__file__).resolve().parent

    input_file = folder / "tekstbestand.txt"
    output_file = folder / "results.txt"

    while True:
        print("\n1. Count days")
        print("2. Calculate actuator settings")
        print("3. Change a saved setting")
        print("4. Stop")

        choice = input("Your choice: ").strip()

        if choice == "1":
            number_of_days = aantal_dagen(input_file)

            if number_of_days >= 0:
                print(f"Number of days: {number_of_days}")

        elif choice == "2":
            auto_bereken(input_file, output_file)

        elif choice == "3":
            result = overwrite_settings(output_file)

            if result == 0:
                print("Changes saved.")
            elif result == -1:
                print("Could not find the date or read/write the file.")
            elif result == -3:
                print("Invalid system or value.")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    smart_app_controller()