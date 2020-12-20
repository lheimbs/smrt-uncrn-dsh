import os


def clean_for_prod():
    BASE_DIR = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
    print(BASE_DIR)
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".py") or file.endswith(".html") or file.endswith(".js"):
                if file_path.startswith(os.path.join(BASE_DIR, 'static', 'gen')):
                    print(f"Skipping '{file}' in 'static/gen' folder.")
                    continue
                with open(file_path) as file:
                    lines = file.readlines()
                    for line in lines:
                        if "// LIBRARY FILE" in line:
                            print(f"Skipping '{file_path}' due to library file!")
                            break
                        if "console.log(" in line:
                            line = line.replace("console.log(", "// console.log(")
                        if "console.debug(" in line:
                            line = line.replace("console.log(", "// console.log(")
                        file.writelines(lines)


if __name__ == "__main__":
    clean_for_prod()
