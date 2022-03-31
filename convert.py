import os
from datetime import date
from pprint import pprint

from simple_smartsheet import Smartsheet
from simple_smartsheet.models import Sheet, Column, Row, Cell, ColumnType

def main():

    parser = argparse.ArgumentParser(description='Process smartsheet to HTML.')
    parser.add_argument('--pi')
    parser.add_argument('--sheetname')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()

    filter_by_pi = False
    if args.pi:
        filter_by_pi = True

    TOKEN = os.getenv("SMARTSHEET_API_TOKEN")
    SHEET_NAME = "Copy of 2022 IBC Roadmap"
    if args.sheetname:
        SHEET_NAME = args.sheetname
    smartsheet = Smartsheet(TOKEN)

    # retrieve a list of sheets (limited set of attributes)
    sheets = smartsheet.sheets.list()
    pprint(sheets)

    # retrieve a sheet by name
    # this object is exactly the same as result.obj
    sheet = smartsheet.sheets.get(SHEET_NAME)

    # get columns details by column title (case-sensitive)
    full_name_column = sheet.get_column("Deliverable (based on level)")
    pprint(full_name_column.__dict__)

    print("\nSheet after adding rows:")
    # print a list of dictionaries containing column titles and values for each row
    #####pprint(sheet.as_list())

    print("<html><body>")

    valid_section = False
    for row in sheet.rows:
        deliverable = row.get_cell("Deliverable (based on level)").value
        aim = row.get_cell("Aim #").value
        level = row.get_cell("Level").value
        print(f"Deliverable: {deliverable} Aim: {aim} Level: {level}")
        #num_books = row.get_cell("Number of read books").value
        #print(f"{full_name} has read {num_books} books")
        if (level == "Project" and (deliverable == "Funded Grant-based Projects" or
        deliverable == "Closeout Grant-based Projects" or deliverable == "New Grant-based Projects" )) :
            valid_section = True
        else :
            valid_section = False
        # main action here
        if (valid_section) :
            if (level == "Project"):
                print("<h1>"+deliverable+"</h1>")

    print("</body></html>")

if __name__ == '__main__':
    main()
