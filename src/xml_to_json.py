import xmltojson

with open("out.xml", "r") as xml_file:
    xml_data = xml_file.read()

json_data = xmltojson.parse(xml_data)

# Save the JSON data to a file
with open("out.json", "w") as json_file:
    json_file.write(json_data)	