import fitz

def reading_pdf_contents():
    try:
        pdf_path = './tdk_competors_main.pdf'
        pdf_document = fitz.open(pdf_path)
        
        if pdf_document.page_count < 35:
            print("The PDF has fewer than 34 pages.")
            return
        
        page = pdf_document.load_page(34)
        
        page_text = page.get_text("text")
        
        pdf_document.close()

        print("Text from the 34th page:\n", page_text)
        return page_text

    except Exception as e:
        print("An error occurred:", e)
        return None

