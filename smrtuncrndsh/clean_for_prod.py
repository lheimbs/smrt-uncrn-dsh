import os


def clean_for_prod():
    BASE_DIR = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
    print(BASE_DIR)
    for root, dirs, files in os.walk(BASE_DIR):
        path = root.split(os.sep)
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".py") or file.endswith(".html") or file.endswith(".js"):
                print(file_path)
                if 

                with open(file_path) as file:
                    lines = file.readlines()
                    for line in lines:
                        if "console.log(" in line:
                            print(len(line))
                            line = line.replace("console.log(", "// console.log(")
                            # print(line)
        # break


if __name__ == "__main__":
    clean_for_prod()
