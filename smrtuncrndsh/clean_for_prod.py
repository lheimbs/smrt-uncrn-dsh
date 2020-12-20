import os


def clean_for_prod():
    BASE_DIR = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".py") or file.endswith(".html") or file.endswith(".js"):
                if file_path.startswith(os.path.join(BASE_DIR, 'static', 'gen')):
                    print(f"Skipping '{file}' in 'static/gen' folder.")
                    continue
                if file == __file__.split(os.sep)[-1]:
                    print("Skipping this file")
                    continue
                with open(file_path) as file:
                    lines = file.readlines()
                    for line in lines:
                        change = False
                        if "// LIBRARY FILE" in line:
                            print(f"Skipping '{file_path}' due to library file!")
                            break
                        if "console.log(" in line:
                            change = True
                            line = line.replace("console.log(", "// console.log(")
                        if "console.debug(" in line:
                            change = True
                            line = line.replace("console.log(", "// console.log(")
                        if change:
                            file.writelines(lines)


if __name__ == "__main__":
    clean_for_prod()
