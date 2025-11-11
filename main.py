try:
    from pypdf import PdfReader as pdfr # For reading PDFs
    from pypdf import PdfWriter as pdfw # For writing PDFs
    from time import sleep              # Not used yet
    import os                           # Paths
    import threading                    # For multi-threading
    import traceback                    # For detailed errors
    
except ImportError:
    print("This script needs pypdf, and pycryptodome!")

    print("Please install through pip!")

pdfs = []
pdfs_lock = threading.Lock()
workers = 100
threads = []
pages_to_read = 0
pages_read = 0
pages_lock = threading.Lock()

stop_pages_thread = False

class newPDF:
    # Class for creating new PDF documents
    filename = ""
    catalog_pulled_from = ""
    data = pdfw()


def contain_pdfs(pdf=None):
    global pdfs
    global pdfs_lock
    with pdfs_lock:
        if pdf is not None:
            pdfs.append(pdf)
        return pdfs

def pages(_pages_read=0, _pages_to_read=0):
    global pages_lock
    global pages_to_read
    global pages_read
    with pages_lock:
        pages_to_read += _pages_to_read
        pages_read += _pages_read
        return (pages_read, pages_to_read)

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

def get_data():
    contents = os.listdir("Catalogs/")
    return contents

def check_contents_for_query(query, doc):
    try:
        # Set up path to actually read document
        path = os.path.join("Catalogs", doc)
        reader = pdfr(path)
        pages(0, len(reader.pages))
        
        # Figure out how many pages each worker will read
        num = 25
        while True:
            if len(reader.pages) % num == 0:
                break
            else:
                num += 1
        
        # Start workers.
        local_threads = []
        count = 0
        for i in range(workers+500):
            try:
                temp_pdf = newPDF()

                for page in reader.pages[count: count+num]:
                    temp_pdf.data.add_page(page)

                if len(temp_pdf.data.pages) == 0:
                    break

                thread = threading.Thread(target=check_pages_for_query, args=[doc, query, temp_pdf.data, count, num])
                thread.start()

                local_threads.append(thread)

                count += num
            except IndexError:
                break
        
        for thread in local_threads:
            thread.join()
            # print("Finished reading pages!")

    except Exception as error:
        print(f"Error! File: {doc}\nQuery: {query}, Error: {error}")
        print(traceback.format_exc())

def check_pages_for_query(doc, query, reader, start, end):
    try:
        for index, page in enumerate(reader.pages[start:end]):
            pages(1, 0)
            if query in page.extract_text():
                temp_pdf = newPDF()
                temp_pdf.catalog_pulled_from = doc
                temp_pdf.data.add_page(page)
                contain_pdfs(pdf=temp_pdf)
                # print("Found something!")
                break
    except Exception as error:
        print(f"Error! File: {doc}\nQuery: {query}, Error: {error}")

def figure_contents(data):
    num = 5
    while True:
        if len(data) % num == 0:
            return num
        else:
            num += 1

def start_threads(workers, query, contents, number_of_files):
    num = 0
    print("Starting threads!")
    global threads
    for i in range(workers):
        try:
            th_content = contents[i]
            # print(th_content)
            # sleep(5)
            if len(th_content) == 0:
                break
            # print(f"Starting thread number: {i}")
            # print(f"Query: {query}")
            # print(f"Data: {th_content}")
            thread = threading.Thread(target=check_contents_for_query, args=[query, th_content])
            thread.start()
            threads.append(thread)
            num += number_of_files
        except IndexError:
            break

    return


def start_all_workers(query, data):
    global threads
    global workers
    global stop_pages_thread

    pages_thread = threading.Thread(target=update_display)
    pages_thread.start()
    start_threads(len(data), query, data, figure_contents(data))
    
    for thread in threads:
        thread.join()
    
    stop_pages_thread = True

def update_display():
    clear_screen()
    global stop_pages_thread
    while not stop_pages_thread:
        sleep(1)
        # clear_screen()
        local_pages_read, local_pages_to_read = pages()
        local_pdf = contain_pdfs()
        print(f"Pages read: {local_pages_read} / Pages to read: {local_pages_to_read}\tResults Found: {len(local_pdf)}", end="\r", flush=True)
        # sleep(0.1)

def main():
    clear_screen()
    data = get_data()
    query = get_part_number()
    start_all_workers(query, data)
    
    for pdf in pdfs:
        print(pdf)

main()

