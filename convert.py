import os
import argparse
import sys
from datetime import date
from pprint import pprint

from simple_smartsheet import Smartsheet
from simple_smartsheet.models import Sheet, Column, Row, Cell, ColumnType

def main():

    parser = argparse.ArgumentParser(description='Process smartsheet to HTML.')
    parser.add_argument('--pi')
    parser.add_argument('--sheetname')
    parser.add_argument('--debug', action='store_true')
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
    #pprint(sheets)

    # retrieve a sheet by name
    # this object is exactly the same as result.obj
    sheet = smartsheet.sheets.get(SHEET_NAME)

    # get columns details by column title (case-sensitive)
    full_name_column = sheet.get_column("Deliverable (based on level)")
    #pprint(full_name_column.__dict__)

    #print("\nSheet after adding rows:")
    # print a list of dictionaries containing column titles and values for each row
    if args.debug:
        pprint(sheet.as_list())

    print('''
<html><body>
<style>
  table, th, td {
    padding-top: 2px;
    padding-bottom: 2px;
    padding-left: 40px;
    padding-right: 2px;
    border: 1px solid;
  }
</style>
<table>
    ''')

    valid_section = False
    valid_project = True
    previous_project = False
    for row in sheet.rows:
        pi = ""
        pi_obj = row.get_cell("PI (at Sage)").object_value
        if (pi_obj != None) :
            pi = pi_obj.values
        deliverable = row.get_cell("Deliverable (based on level)").value
        aim = row.get_cell("Aim #").value
        aim_obj = row.get_cell("Aim #").object_value
        if (aim_obj != None) :
            aim = aim_obj.values
        if (aim == None) :
            aim = ""
        level = row.get_cell("Level").value
        def_comp = row.get_cell("Definition of Complete").value
        if (def_comp == None) :
            def_comp = "<i>fill me in</i>"
        del_obj = row.get_cell("Deliverable (based on level)")
        #print(f"Deliverable: {deliverable} Aim: {aim} Level: {level}")
        #num_books = row.get_cell("Number of read books").value
        #print(f"{full_name} has read {num_books} books")
        if (level == "Category" and (deliverable == "Funded Grant-based Projects" or
        deliverable == "Closeout Grant-based Projects" or deliverable == "New Grant-based Projects" )):
            valid_section = True
            #print("TRUE")
            print("<h1>"+deliverable+"</h1>")
        elif (level == "Category"):
            valid_section = False
            #print("FALSE")
        if (level == "Project" and filter_by_pi) :
            valid_project = False
            for individual_pi in pi:
                #print("<h1>PI Individual: "+str(individual_pi['name'])+"</h1>")
                if (individual_pi['name'] == args.pi) :
                    valid_project = True

        # collect PIs
        pi_array = []
        for individual_pi in pi:
            #print("<h1>PI Individual: "+str(individual_pi['name'])+"</h1>")
            pi_array.append(individual_pi['name'])
        # main action here
        if (valid_section and valid_project ) :
            if (level == "Project"):
                # LEFT OFF WITH: need to figure out indent logic with tables below
                if(previous_project) :
                    print("</td></tr>")
                print("<tr><td><h2>Project: "+str(deliverable)+"</h2>")
                print("<p><b>PI:</b>"+str(pi_array)+"</p>")
                print("<p><b>Description:</b><i>fill me in</i></p>")
                previous_project = True
            if(level == "Sub-Aim"):
                print("<h3> -> Sub-Aim: "+str(aim) + " " + str(deliverable)+"</h3>")
                print("<p><b>Description:</b> "+str(deliverable)+"</p>")
                print("<p><b>Definition of Complete:</b> "+str(def_comp)+"</p>")
            if(level == "Deliverable"):
                print("<h4> --> Deliverable: "+str(aim) + " " +str(deliverable)+"</h4>")
                print("<p><b>Description:</b> "+str(deliverable)+"</p>")
                print("<p><b>Definition of Complete:</b> "+str(def_comp)+"</p>")
            if(level == "Epic"):
                if (del_obj.hyperlink) :
                    print("<h5><a href='"+del_obj.hyperlink.url+"'> ---> Epic: "+str(aim_obj) + " " +str(deliverable)+"</a></h5>")
                else:
                    print("<h5> ---> Epic: "+str(aim) + " " +str(deliverable)+"</h5>")
                print("<p><b>Description:</b> "+str(deliverable)+"</p>")
                print("<p><b>Definition of Complete:</b> "+str(def_comp)+"</p>")

    if (previous_project) :
        print("</td></tr>")
    print("</table></body></html>")

if __name__ == '__main__':
    main()
