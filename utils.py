def extract_sections(response):

    sections = {}

    current_section = None

    lines = response.split("\n")

    for line in lines:

        if line.startswith("## "):

            current_section = line.replace("## ", "").strip()

            sections[current_section] = ""

        elif current_section:

            sections[current_section] += line + "\n"

    return sections