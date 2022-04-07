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
    parser.add_argument('--header')
    args = parser.parse_args()
    #if args.help:
        #parser.print_help()

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
    width: 600px;
  }
  h4, h5, h6 {
    font-size: 1.17em;
  }
  .red {
    background-color: #fcd9d9;
  }
  .yellow {
    background-color: #fcfbd9;
  }
</style>
    ''')

    valid_section = False
    valid_project = True
    previous_project = False

    previous_level = 0

    # print initial table
    print("<table>")

    if (args.header):
        text_file = open(args.header, "r")
        #read whole file to a string
        header = text_file.read()
        text_file.close()
        print(header)

    for row in sheet.rows:
        # collect a bunch of information
        pi = ""
        pi_obj = row.get_cell("PI (at Sage)").object_value
        if (pi_obj != None) :
            pi = pi_obj.values
        deliverable = row.get_cell("Deliverable (based on level)").value
        confidence = row.get_cell("Confidence scale").value
        if (confidence == None):
            confidence = "low concern"
        flag = row.get_cell("Flag").value
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

        # start and finish
        start = row.get_cell("Start").value
        if (start == None):
            start = "<i>fill me in YYYY-MM-DD</i>"
        else:
            start = str(row.get_cell("Start").value)[0:10]
        finish = row.get_cell("Finish").value
        if (finish == None):
            finish = "<i>fill me in YYYY-MM-DD</i>"
        else:
            finish = str(row.get_cell("Finish").value)[0:10]

        # save state
        new_level = 0

        # now check to see if it's a category we want
        if (level == "Category" and (deliverable == "Funded Grant-based Projects" or
        deliverable == "Closeout Grant-based Projects" or deliverable == "New Grant-based Projects" )):
            valid_section = True
            #print("TRUE")
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
        pi_comma_list = ", ".join(pi_array)

        # main action here
        # seeing if this is a valid project to report
        if ((valid_section and valid_project) or level == "Category") :
            if (level == "Category"):
                new_level = 1
            elif (level == "Project"):
                new_level = 2
            elif (level == "Sub-Aim"):
                new_level = 3
            elif (level == "Deliverable"):
                new_level = 4
            elif (level == "Epic"):
                new_level = 5

            if (new_level > previous_level):
                for i in range(previous_level, new_level, 1) :
                    print("<tr><td><table>")
            elif (new_level < previous_level):
                for i in range (previous_level, new_level, -1) :
                    print("</table></td></tr>")

            previous_level = new_level

            # background color
            open_row = "<tr><td>"
            confidence_emoji = "🟢"
            if (str(confidence) == "Red"):
                open_row = "<tr class='red'><td>"
                confidence_emoji = "🔴"
            elif (str(confidence) == "Yellow"):
                open_row = "<tr class='yellow'><td>"
                confidence_emoji = "🟡"
            flag_str = "⚐"
            if (str(flag) == "True"):
                flag_str = "🚩"

            if (level == "Category"):
                print("<tr><td>")
                print("<h1>Category: "+str(deliverable)+"</h1>")
                print("</td></tr>")
            if (level == "Project"):
                print(open_row)
                print("<h2>Project: "+str(deliverable)+"</h2>")
                print("<p><b>PIs: </b>"+pi_comma_list+"</p>")
                print("<p><b>Flagged for Concern:</b> "+flag_str+" <b>Confidence Level:</b> "+confidence_emoji+"</p>")
                print("<p><b>Overall Project Start:</b> "+str(start)+" <b>Finish:</b> "+str(finish)+"</p>")
                print("<p><b>Description: </b><i>fill me in</i></p>")
                print("</td></tr>")
                previous_project = True
            if(level == "Sub-Aim"):
                print(open_row)
                print("<h3>Sub-Aim: "+str(aim) + " " + str(deliverable)+"</h3>")
                print("<p><b>Flagged for Concern:</b> "+flag_str+" <b>Confidence Level:</b> "+confidence_emoji+"</p>")
                print("<p><b>Start:</b> "+str(start)+" <b>Finish:</b> "+str(finish)+"</p>")
                print("<p><b>Description:</b> "+str(deliverable)+"</p>")
                print("<p><b>Definition of Complete:</b> "+str(def_comp)+"</p>")
                print("</td></tr>")
            if(level == "Deliverable"):
                print(open_row)
                print("<h4>Deliverable: "+str(aim) + " " +str(deliverable)+"</h4>")
                print("<p><b>Flagged for Concern:</b> "+flag_str+" <b>Confidence Level:</b> "+confidence_emoji+"</p>")
                print("<p><b>Start:</b> "+str(start)+" <b>Finish:</b> "+str(finish)+"</p>")
                print("<p><b>Description:</b> "+str(deliverable)+"</p>")
                print("<p><b>Definition of Complete:</b> "+str(def_comp)+"</p>")
                print("</td></tr>")
            if(level == "Epic"):
                print(open_row)
                if (del_obj.hyperlink) :
                    print("<h5><a href='"+del_obj.hyperlink.url+"'>Epic: "+str(aim_obj) + " " +str(deliverable)+"</a></h5>")
                else:
                    print("<h5>Epic: "+str(aim) + " " +str(deliverable)+"</h5>")
                print("<p><b>Flagged for Concern:</b> "+flag_str+" <b>Confidence Level:</b> "+confidence_emoji+"</p>")
                print("<p><b>Start:</b> "+str(start)+" <b>Finish:</b> "+str(finish)+"</p>")
                print("<p><b>Description:</b> "+str(deliverable)+"</p>")
                print("<p><b>Definition of Complete:</b> "+str(def_comp)+"</p>")
                print("</td></tr>")

    #if (previous_project) :
    #    print("</td></tr>")
    #print("</table></body></html>")

    for i in range (previous_level, 0, -1) :
        print("</table></td></tr>")

    # print final table
    print("</table>")

if __name__ == '__main__':
    main()
