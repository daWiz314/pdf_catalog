

userInput = ""
partNumber = ""




def clear_screen():
    for i in range(100):
        print()

def get_part_number():
    while True:
        clear_screen()
        print("Please enter the part number!")
        userInput = input(">")
        clear_screen()
        print("You entered: " + userInput)
        print("Is this correct? Y/N")
        confirm = input(">")
        if confirm.lower() == "y":
            break
        else:
            continue
    
    return userInput.strip()

def run_imports():
    try:
        from pypdf import PdfReader as pdfr
    except ImportError:
        print("This script needs pypdf!")
        print("Please install through pip!")

def main():
    clear_screen()
    run_imports()
    print(get_part_number())

main()

