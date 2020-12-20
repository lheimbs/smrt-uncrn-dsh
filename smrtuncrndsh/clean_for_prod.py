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
                print(f"opening {file}")
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    change = False
                    for line in lines:
                        if "// LIBRARY FILE" in line:
                            print(f"Skipping '{file_path}' due to library file!")
                            break
                        if "console.log(" in line:
                            change = True
                            line = line.replace("console.log(", "// console.log(")
                            print(line)
                        if "console.debug(" in line:
                            change = True
                            line = line.replace("console.debug(", "// console.debug(")
                            print(line)
                with open(file_path, 'w') as file:
                    if change and lines:
                        file.writelines(lines)


if __name__ == "__main__":
    clean_for_prod()
