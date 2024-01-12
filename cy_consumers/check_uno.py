import uno

def split_doc_by_page(input_file, output_prefix):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.loadComponentFromURL(input_file, "_blank", 0, ())

    pages = doc.Text.PageCount
    for i in range(1, pages + 1):
        exporter = smgr.createInstanceWithContext(
            "com.sun.star.document.ExportFilter", ctx)
        exporter.FilterName = "writer_pdf_Export"  # Or any other desired format
        props = exporter.getExportProperties()
        props.PageRange = str(i) + "-" + str(i)  # Export only the current page
        output_file = output_prefix + str(i) + ".pdf"  # Adjust extension as needed
        doc.storeToURL(output_file, props)

split_doc_by_page(f"/home/vmadmin/python/cy-py/cy_consumers/delete_files_clean_unfinish.py","x")