import os
import webbrowser
from json2html import json2html
import tempfile

def show_json_table(json_list):
    """
    Show a json data as a table in browser
    :param json_list: The json data to show
    :return:
    """
    table_html = json2html.convert(json=json_list, escape=False)
    # write the html to a file
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Table</title>
    <style>
        table {{
            border-collapse: collapse;
            width: 100%;
        }}

        th, td {{
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }}

        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    {table_html}
</body> 
</html>
"""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as file:
        file.write(html)
        filename = 'file:///' + file.name
    webbrowser.open_new_tab(filename)


if __name__ == '__main__':
    data = [
        {
            "Name": "John",
            "Age": 30,
            "City": "New York"
        },
        {
            "Name": "Peter",
            "Age": 45,
            "City": "Boston"
        }
    ]
    show_json_table(data)
