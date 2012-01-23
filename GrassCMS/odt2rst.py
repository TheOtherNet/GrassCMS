import sys
import re
import os
import shutil
import zipfile
import hashlib
import math
import getopt
import bisect
import textwrap
import xml.etree.ElementTree

# Level formats let you choose how you want each heading levels to be translated in the .rst file.
# It is a list of tuple corresponding to the list of header levels.
# The first element of the tuple is the charactere used to underline the header.
# The second element is a boolean which should be set to True if you want the header to be both underlined and 'upperlined' and  to False if you want it to be only underlined.
LEVEL_FORMATS = [("#", False), ("*", False), ("=", False), ("-", False), ("^", False), ('"', False)]

DEBUG_FLAG = False

office_prefix   =  "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
text_prefix     =  "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
table_prefix    =  "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
drawing_prefix  =  "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
style_prefix    =  "{urn:oasis:names:tc:opendocument:xmlns:style:1.0}"
fo_prefix       =  "{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}"

xlink_prefix    =  "{http://www.w3.org/1999/xlink}"


class Options:
    def __init__(self):
        self.images_relative_folder = "images"
        self.temp_folder = "."
        self.clean = True
        
        self.wrap_width = -1


def getRomanString(n):
    values = [
        (1, "I"),
        (4, "IV"), 
        (5, "V"), 
        (9, "IX"), 
        (10, "X"), 
        (40, "XL"), 
        (50, "L"), 
        (90, "XC"), 
        (100, "C"), 
        (400, "CD"), 
        (500, "D"), 
        (900, "CM"), 
        (1000, "M"), 
    ]
    
    ret = ""
    while n > 0:
        i = bisect.bisect(values, (n, "Z")) - 1
        n -= values[i][0]
        ret += values[i][1]
        
    return ret


def unpackOdt(input_path, temp_folder = "."):
    "Unpack the odt file into the temp folder and return a dictionary translating .png file path into they hashes."
    odtfile = zipfile.ZipFile(input_path)

    try:
        os.mkdir(temp_folder)
    except:
        pass

    try:
        os.mkdir(os.path.join(temp_folder, "Pictures"))
    except:
        pass

    odt_pictures_hashes = {}
    for path in odtfile.namelist():
        if path.lower() in ["content.xml", "styles.xml"]:
            g = open(os.path.join(temp_folder, path), "wb")
            bytes = odtfile.read(path)
            g.write(bytes)
            g.close()

        folder, name = os.path.split(path)
        name, ext = os.path.splitext(name)
        if folder.lower() == "Pictures".lower() and ext in [".png", ".jpg"]:
            g = open(os.path.join(temp_folder, path), "wb")
            bytes = odtfile.read(path)
            g.write(bytes)
            g.close()

            h = hashlib.md5()
            h.update(bytes)
            h = h.digest()
            odt_pictures_hashes[path] = h

    return odt_pictures_hashes


def cleanPack(temp_folder = "."):
    "Delete the files and folder created by unpackOdt apart from the temp_folder itself."
    os.remove(os.path.join(temp_folder, "content.xml"))
    os.remove(os.path.join(temp_folder, "styles.xml"))
    shutil.rmtree(os.path.join(temp_folder, "Pictures"))


def getHashesRstImages(output_folder, images_relative_folder):
    "Return a dictonary translating hash into the its .png file path."
    hashes_rst_images = {}

    image_folder = os.path.join(output_folder, images_relative_folder)

    if not os.path.isdir(image_folder):
        return {}

    for path in os.listdir(image_folder):
        name, ext = os.path.splitext(path)
        if ext not in [".png", ".jpg"]:
            continue

        path = os.path.join(images_relative_folder, path)

        f = open(path, "rb")
        bytes = f.read()
        f.close()

        h = hashlib.md5()
        h.update(bytes)
        h = h.digest()
        hashes_rst_images[h] = path

    return hashes_rst_images


def synchronizeImagesFolders(temp_folder, output_path, images_relative_folder, odt_pictures_hashes):
    output_folder, output_name = os.path.split(output_path)
    image_folder = os.path.join(output_folder, images_relative_folder)

    hashes_rst_images = getHashesRstImages(output_folder, images_relative_folder)

    # Build the picture_dict that convert odt image path into rst image path (when possible)
    picture_prefix = "picture_"
    existing_picture_names = []
    if os.path.isdir(image_folder):
        for path in os.listdir(image_folder):
            path = path.lower()
            name, ext = os.path.splitext(path)
            if ext not in [".png", ".jpg"]:
                continue

            if not name.startswith(picture_prefix):
                continue

            existing_picture_names.append(name)

    picture_dict = {}
    picture_index = 0
    for path in odt_pictures_hashes:
        h = odt_pictures_hashes[path]
        if h in hashes_rst_images:
            picture_dict[path] = hashes_rst_images[h]
        else:
            # Find an available picture name:
            while picture_prefix + str(picture_index) in existing_picture_names:
                picture_index += 1

            picture_name = picture_prefix + str(picture_index)
            existing_picture_names.append(picture_name)

            name, ext = os.path.splitext(path)
            picture_relative_path = os.path.join(images_relative_folder, picture_name) + ext

            if not os.path.isdir(image_folder):
                os.mkdir(image_folder)

            shutil.copyfile(os.path.join(temp_folder, path), os.path.join(output_folder, picture_relative_path))

            picture_dict[path] = picture_relative_path

    return picture_dict


class Style:
    def __init__(self):
        self.name = ""
        self.parent_name = ""
        self.family = ""

        self.margin_left = 0

        self.font_style = ""
        self.font_weight = ""

    def translateNode(self, node):
        self.name = node.attrib[style_prefix + "name"]
        self.parent_name = node.attrib.get(style_prefix + "parent-style-name", "")
        self.family = node.attrib.get(style_prefix + "family", "")

        for child in node:
            if child.tag == style_prefix + "paragraph-properties":
                self.margin_left = child.attrib.get(fo_prefix + "margin-left", "0in")
                if self.margin_left.endswith("in"):
                    self.margin_left = float(self.margin_left[:-2])
                else:
                    raise Exception("unknown mesure: '%s'" % self.margin_left)

            if child.tag == style_prefix + "text-properties":
                self.font_style = child.attrib.get(fo_prefix + "font-style", "")
                self.font_weight = child.attrib.get(fo_prefix + "font-weight", "")

    def isBold(self):
        if self.family != "text":
            return False

        if self.font_weight == "bold":
            return True

        return False

    def isItalic(self):
        if self.family != "text":
            return False

        if self.font_style == "italic":
            return True

        return False

    def __str__(self):
        ret = "Style("
        ret += '\tName : "%s"\n' % self.name
        ret += '\tParent-Name : "%s"\n' % self.parent_name
        ret += '\tFamily : "%s"\n' % self.family
        ret += '\tMargin-Left : %f\n' % self.margin_left
        ret += '\tFont-Style : "%s"\n' % self.font_style
        ret += '\tFont-Weight : "%s"\n' % self.font_weight
        ret += ")\n"

        return ret


def extractStylesFromNode(node):
    ret = {}
    for child in node:
        if child.tag != style_prefix + "style":
            continue

        style = Style()
        style.translateNode(child)

        ret[style.name] = style

    return ret


def extractStylesFromRoot(root):
    ret = {}
    automatic_styles = root.find(office_prefix + "automatic-styles")
    if automatic_styles:
        ret.update(extractStylesFromNode(automatic_styles))

    styles = root.find(office_prefix + "styles")
    if styles:
        ret.update(extractStylesFromNode(styles))

    return ret


class ListLevelStyle:
    def __init__(self):
        self.num_format = ""

    def translateNode(self, node):
        if node.tag == text_prefix + "list-level-style-number":
            self.num_format = node.attrib.get(style_prefix + "num-format", "")


class ListStyle:
    def __init__(self):
        self.name = ""
        self.levels = []

    def translateNode(self, node):
        self.name  = node.attrib.get(style_prefix + "name", "")
        #print self.name
        for child in node:
            if child.tag not in [text_prefix + "list-level-style-number", text_prefix + "list-level-style-bullet"]:
                print 'Unknown tag: "%s" in list style.' % child.tag
                continue

            list_level_style = ListLevelStyle()
            self.levels.append(list_level_style)

            list_level_style.translateNode(child)

def extractListStylesFromNode(node):
    ret = {}
    for child in node:
        if child.tag != text_prefix + "list-style":
            #print child.tag
            continue

        style = ListStyle()
        style.translateNode(child)

        ret[style.name] = style

    return ret


def extractListStylesFromRoot(root):
    ret = {}
    automatic_styles = root.find(office_prefix + "automatic-styles")
    if automatic_styles:
        ret.update(extractListStylesFromNode(automatic_styles))

    styles = root.find(office_prefix + "styles")
    if styles:
        ret.update(extractListStylesFromNode(styles))

    return ret


class ListInfo:
    def __init__(self):
        self.style_name = ""
        self.levels = []


class ListLevelInfo:
    def __init__(self):
        # Set to True when the '-', '#.' or '1.' have been inserted in the rst document.
        self.is_bullet_inserted = False

        # Set to -1 if the list is a bulleted list and to the current item index if the list is a numbered list.
        self.num_format = ""
        self.current_index = -1

        # Keep the identation level of list item (to be able to start a new sublist or to stop the list when the identation change)
        self.identation = 0


def splitIntoLines(text, wrap_width):
    if wrap_width <= 0:
        text = re.sub(r"([a-zA-Z]{2})\. +", r"\1.\n", text)
        text = re.sub(r"([\)\]\"'`\*])\. +", r"\1.\n", text)
    else:
        text = textwrap.fill(text, wrap_width)
    return text


def getRawText(node):
    text = ""
    if node.text:
        text += node.text
    for child in node:
        if child.tag in [text_prefix + "p", text_prefix + "span"]:
            text += getRawText(child)

        if child.tail:
            text += child.tail

    text = text.replace("\n", " ")
    return text


def getCodeText(node):
    text = ""
    if node.text:
        text += node.text
    for child in node:
        if child.tag in [text_prefix + "p", text_prefix + "span"]:
            text += getCodeText(child)

        if child.tag == text_prefix + "line-break":
            text += "\n"

        if child.tag == text_prefix + "s":
            identation = int(child.attrib[text_prefix + "c"])
            identation = " " * identation

            text += identation

        if child.tail:
            text += child.tail

    return text


def escapeCellText(text):
    "Return a rst version of the text that is suitable for rst cell content."
    text = text.replace("+", "\\+")
    text = text.replace("-", "\\-")
    text = text.replace("|", "\\|")
    return text


class Table:
    def __init__(self):
        self.rows = []

    def __str__(self):
        ret = "Table(\n"
        ret += "  rows : [\n"
        for row in self.rows:
            ret += str(row) + ",\n"
        ret += "  ]\n"
        ret += ")\n"

        return ret

    def addCoveredCells(self):
        num_columns = 0
        row  = self.rows[0]
        for cell in row.cells:
            num_columns += cell.h_span

        grid = [[None for i in range(num_columns)] for j in range(len(self.rows))]

        for row_index in range(len(self.rows)):
            row = self.rows[row_index]

            column_index = 0
            for cell in row.cells:
                while column_index < num_columns and grid[row_index][column_index]:
                    column_index += 1

                grid[row_index][column_index] = cell
                for extra_column_index in range(cell.h_span):
                    for extra_row_index in range(cell.v_span):
                        if extra_column_index == 0 and extra_row_index == 0:
                            continue
                        covered_cell = TableCell()
                        grid[row_index + extra_row_index][column_index + extra_column_index] = covered_cell
                        covered_cell.covered = True

                        if extra_column_index:
                            covered_cell.left_wall = False

                        if extra_row_index:
                            covered_cell.top_wall = False

        for row_index in range(len(self.rows)):
            row = self.rows[row_index]

            row.cells = grid[row_index]

    def getColumnWidths(self):
        column_widths = []

        for row in self.rows:
            column_index = 0
            while column_index < len(row.cells):
                cell = row.cells[column_index]

                if cell.covered:
                    column_index += 1
                    continue

                while len(column_widths) < column_index + cell.h_span:
                    column_widths.append(0)

                actual_width = sum(column_widths[column_index : column_index + cell.h_span]) + cell.h_span - 1
                width = len(cell.text) + 2
                if width > actual_width:
                    addition = int(math.ceil((width - actual_width) / float(cell.h_span)))
                    for index in range(column_index, column_index + cell.h_span):
                        column_widths[index] += addition

                column_index += cell.h_span

        return column_widths


class TableRow:
    def __init__(self):
        self.header = False
        self.cells = []

    def __str__(self):
        ret = "Row(\n"
        ret += "  rows : [\n"
        for cell in self.cells:
            ret += str(cell) + ",\n"
        ret += "  ]\n"
        ret += ")\n"

        return ret


class TableCell:
    def __init__(self):
        self.h_span = 1
        self.v_span = 1

        self.text = ""

        self.covered = False
        self.top_wall = True
        self.left_wall = True

    def __str__(self):
        ret = "Cell(\n"
        ret += "  h_span : %d,\n" % self.h_span
        ret += "  v_span : %d,\n" % self.v_span
        ret += '  text : "%s",\n' % self.text
        ret += '  covered : %d,\n' % self.covered
        ret += ")\n"

        return ret


class RstDocument:
    # Set here the char that should be used to underline the titles according to they levels.
    # The default is the Python convention for documentation.
    level_formats = LEVEL_FORMATS
    identation_string = "   "

    def __init__(self, path = ""):
        self.path = path
        self.file = None

        self.styles = {}
        self.list_styles = {}

        self.lists = []
        # Keep the list levels info to merge consecutive lists:
        self.last_levels = []

        self.picture_dict = {}
        self.options = Options()

        self.inline_images = {}
        self.paragraphs = []

    def getLastListLevel(self):
        return self.lists[-1].levels[-1]

    def getAllListLevels(self):
        ret = []
        for list_info in self.lists:
            ret += list_info.levels
        return ret

    def flush(self):
        for paragraph in self.paragraphs:
            text = paragraph
            if DEBUG_FLAG:
                text += "endof para"
            text += "\n"
            text = text.encode("utf8")
            self.file.write(text)

        self.paragraphs = []

    def open(self, path = ""):
        if path:
            self.path = path
        self.file = open(self.path, "w")

    def close(self):
        self.flush()

        for path in self.inline_images:
            name = self.inline_images[path]
            text = "\n.. |%s| image:: %s\n" % (name, path)
            text = text.encode("utf8")
            self.file.write(text)

        self.file.close()

    def write(self, text):
        self.flush()

        text = text.encode("utf8")
#       if text == "\n":
#           raise Exception("hidden return")
        self.file.write(text)

    def writeTitle(self, text, level):
        paragraph = ""
        if DEBUG_FLAG:
            paragraph += "pre-title"
        paragraph += "\n" + "\n"
        char = self.level_formats[level][0]
        upper_line = self.level_formats[level][1]
        if upper_line:
            paragraph += char * len(text) + "\n"
        paragraph += text + "\n" + char * len(text) + "\n"
        self.write(paragraph)

    def writeParagraph(self, text):
        if not text:
            return

        if text.startswith("Unknown interpreted text role"):
            return
            
#        if text.startswith("Unknown directive type"):
#            return

        paragraph = ""
        if DEBUG_FLAG:
            paragraph += "pre-para"
        paragraph += "\n"

#       if not self.lists:
#           if DEBUG_FLAG:
#               paragraph += "pre-para"
#           paragraph += "\n"

#       elif self.getLastListLevel().is_bullet_inserted:
#           # A new paragraph in a list item needs a blank line to mark the separation with the previous one.
#           if DEBUG_FLAG:
#               paragraph += "pre-item"
#           paragraph += "\n"

        identation = ""
        bullet = ""
        non_bullet = ""
        if self.lists:
            if self.getLastListLevel().num_format == "1":
                bullet = "   "
                non_bullet = "   "
                if not self.getLastListLevel().is_bullet_inserted:
                    bullet = "%d. " % (self.getLastListLevel().current_index % 10)
            elif self.getLastListLevel().num_format == "a":
                bullet = "   "
                non_bullet = "   "
                if not self.getLastListLevel().is_bullet_inserted:
                    bullet = "%c. " % (ord('a') + self.getLastListLevel().current_index - 1)
                    
            elif self.getLastListLevel().num_format == "A":
                bullet = " " * (5 + 1)
                non_bullet = " " * (5 + 1)
                if not self.getLastListLevel().is_bullet_inserted:
                    bullet = (getRomanString(self.getLastListLevel().current_index).upper() + ".").ljust(5) + " "

            elif self.getLastListLevel().num_format == "i":
                bullet = " " * (5 + 1)
                non_bullet = " " * (5 + 1)
                if not self.getLastListLevel().is_bullet_inserted:
                    bullet = (getRomanString(self.getLastListLevel().current_index).lower()+ ".").ljust(5) + " "
                    
            else:
                bullet = "  "
                non_bullet = "  "
                if not self.getLastListLevel().is_bullet_inserted:
                    bullet = "- "

            self.getLastListLevel().is_bullet_inserted = True

            for list_level_info in self.getAllListLevels()[:-1]:
                if list_level_info.current_index >= 0:
                    identation += "   "
                else:
                    identation += "  "

        text = splitIntoLines(text, self.options.wrap_width)
        text = text.split("\n")

        paragraph += identation + bullet + ("\n" + identation + non_bullet).join(text)

        self.paragraphs.append(paragraph)

    def writeDefinitionBody(self, text):
        if self.paragraphs:
            paragraph = self.paragraphs.pop()

            paragraph = paragraph.replace("**", "")
            self.write(paragraph)

        text = splitIntoLines(text, self.options.wrap_width)
        text = text.split("\n")

        self.write("\n")

        identation = self.identation_string
        text = identation + ("\n" + identation).join(text) + "\n"
        self.write(text)

    def writeCodeBlock(self, text):
        if self.paragraphs:
            paragraph = self.paragraphs[-1]
            paragraph += ":\n"
            self.paragraphs[-1] = paragraph

        identation = self.identation_string
        text = text.split("\n")
        self.write(identation + ("\n" + identation).join(text) + "\n")

    def writeNoteHeader(self):
        self.write("\n.. note::\n")

    def appendToNote(self, text):
        text = splitIntoLines(text, self.options.wrap_width)
        text = text.split("\n")
        self.write("   " + "\n   ".join(text) + "\n\n")

    def writeWarningHeader(self):
        self.write("\n.. warning::\n")

    def appendToWarning(self, text):
        self.write("   " + text + "\n\n")

    def writeImage(self, path):
        self.write("\n")
        if path in self.picture_dict:
            path = self.picture_dict[path]
        path = path.replace('\\', '/')
        self.write(".. image:: %s\n" % path)

    def writeFigure(self, path, legend):
        self.write("\n")
        if path in self.picture_dict:
            path = self.picture_dict[path]
        path = path.replace('\\', '/')
        self.write(".. figure:: %s\n\n" % path)
        if legend:
            self.write("   %s\n" % legend)

    def writeComment(self, text):
        text = text.split("\n")
        self.write("\n.. " +  text.pop(0)+ "\n")
        while text:
            self.write("   " + text.pop(0) + "\n")
        self.write("\n")

    def writeTable(self, table):
        self.write("\n")

        table.addCoveredCells()
        column_widths = table.getColumnWidths()

        bottom = ""
        previous_header = False
        for row_index in range(len(table.rows)):
            row = table.rows[row_index]

            top = ""
            body = ""
            column_index = 0
            while column_index < len(row.cells):
                cell = row.cells[column_index]

                if cell.covered:
                    while column_index < len(row.cells):
                        cursor_cell = row.cells[column_index]
                        if not cursor_cell.covered:
                            break

                        top_char = " "
                        if cursor_cell.top_wall:
                            if previous_header:
                                top_char = "="
                            else:
                                top_char = "-"

                        cross_char = "+"
                        if not cursor_cell.top_wall and not cursor_cell.left_wall:
                            cross_char = " "

                        top +=  cross_char + top_char * column_widths[column_index]

                        wall_char = " "
                        if cursor_cell.left_wall:
                            wall_char = "|"
                        body += wall_char + " " * column_widths[column_index]

                        column_index += 1

                else:
                    for cursor_column_index in range(column_index, column_index + cell.h_span):
                        cursor_cell = row.cells[cursor_column_index]
                        top_char = " "
                        if cursor_cell.top_wall:
                            if previous_header:
                                top_char = "="
                            else:
                                top_char = "-"

                        top +=  "+" + top_char * column_widths[cursor_column_index]

                    width = sum(column_widths[column_index : column_index + cell.h_span]) + cell.h_span - 1
                    body += "|" + " " + cell.text + " " * (width - len(cell.text) - 2) + " "

                    column_index += cell.h_span


            top += "+\n"
            if row_index == 0:
                bottom = top

            body += "|\n"

            self.write(top)
            self.write(body)

            previous_header = row.header

        self.write(bottom)

    def getElementText(self, node):
        text = ""
        if node.text:
            text += node.text

        for child in node:
            if child.tag == text_prefix + "span":
                style_name = child.attrib[text_prefix + "style-name"]
                style = self.styles.get(style_name, None)
                if style_name == "rststyle-strong":
                    text += "**%s**" % child.text

                elif style_name == "rststyle-emphasis":
                    text += "*%s*" % child.text

                elif style.isBold():
                    # TODO: we should check the attributes of the rststyle-strong and rststyle-emphasis styles.
                    text += "**%s**" % child.text

                elif style.isItalic():
                    # TODO: we should check the attributes of the rststyle-strong and rststyle-emphasis styles.
                    text += "*%s*" % child.text

                elif style_name in ["rststyle-inlineliteral"]:
                    text += "``%s``" % child.text

                else:
                    if child.text is not None:
                        text += child.text

            elif child.tag == drawing_prefix + "frame":
                if child[0].tag == drawing_prefix + "image":
                    image = child[0]
                    path = image.attrib[xlink_prefix + "href"]
                    if path in self.picture_dict:
                        path = self.picture_dict[path]
                    path = path.replace('\\', '/')

                    folder, name = os.path.split(path)
                    name, ext = os.path.splitext(name)

                    text += "|%s|" % name

                    self.inline_images[path] = name

            elif child.tag == text_prefix + "p":
                text += self.getElementText(child)

            else:
                print 'Unknown tag: "%s" in text.' % child.tag

            if child.tail:
                text += child.tail

        text = text.replace("\n", " ")
        return text

    def transformTableNode(self, table_node):
        table = Table()
        column_sizes = []

        for child in table_node:
            header = False
            row_node = child
            if child.tag == table_prefix + "table-header-rows":
                header = True
                row_node = child[0]

            if row_node.tag != table_prefix + "table-row":
                continue

            row = TableRow()
            row.header = header
            table.rows.append(row)

            for cell_node in row_node:
                cell = TableCell()
                if cell_node.tag != table_prefix + "table-cell":
                    continue
                row.cells.append(cell)

                cell.h_span = int(cell_node.attrib.get(table_prefix + "number-columns-spanned", 1))
                cell.v_span = int(cell_node.attrib.get(table_prefix + "number-rows-spanned", 1))
                cell.text = self.getElementText(cell_node)
                cell.text = escapeCellText(cell.text)

        self.writeTable(table)

    def transformNode(self, node):
        for child in node:
            if child.tag == text_prefix + "p":
                if not self.lists:
                    self.last_levels = []

                style = child.attrib[text_prefix + "style-name"]
                frame = child.find(drawing_prefix + "frame")
                comment = child.find(office_prefix + "annotation")

                if style == "rststyle-title":
                    self.writeTitle(child.text, 0)

                elif style == "rststyle-admon-note-hdr":
                    self.writeNoteHeader()

                elif style == "rststyle-admon-note-body":
                    self.appendToNote(self.getElementText(child))

                elif style == "rststyle-admon-warning-hdr":
                    self.writeWarningHeader()

                elif style == "rststyle-admon-warning-body":
                    self.appendToWarning(self.getElementText(child))

                elif style == "rststyle-blockindent":
                    self.writeDefinitionBody(self.getElementText(child))

                elif style == "rststyle-codeblock":
                    self.writeCodeBlock(getCodeText(child))

                elif frame and frame.attrib[text_prefix + "anchor-type"] == "paragraph":
                    if frame[0].tag == drawing_prefix + "image":
                        image = frame[0]
                        path = image.attrib[xlink_prefix + "href"]
                        self.writeImage(path)

                    elif frame[0].tag == drawing_prefix + "text-box":
                        try:
                            text_box = frame[0]
                            paragraph = text_box[0]
                            frame = paragraph[0]
                            image = frame[0]
                            path = image.attrib[xlink_prefix + "href"]
                            legend = frame.tail

                            self.writeFigure(path, legend)
                        except:
                            print "fail to convert the figure"

                elif comment:
                    try:
                        text = getRawText(comment)

                        self.writeComment(text)
                    except:
                        print "fail to find the comment"

                else:
                    self.writeParagraph(self.getElementText(child))

            elif child.tag == text_prefix + "h":
                level = int(child.attrib[text_prefix + "outline-level"])
                self.writeTitle(self.getElementText(child), level)

            elif child.tag == text_prefix + "section":
                self.transformNode(child)

            elif child.tag == text_prefix + "list":
                style_name = child.attrib.get(text_prefix + "style-name", "")
                if style_name == "Outline":
                    item = child[0]
                    while item._children:
                        if item[0].tag == text_prefix + "h":
                            self.transformNode(item)
                            break;
                        item = item[0]

                else:
                    list_info = ListInfo()
                    list_info.style_name = style_name
                    list_info.levels = list(self.last_levels)

                    self.lists.append(list_info)
                    self.transformNode(child)
                    self.last_levels = self.lists[-1].levels
                    self.lists.pop()

            elif child.tag == text_prefix + "list-item":
                paragraph = child.find(text_prefix + "p")

                style = None
                if paragraph != None:
                    style_name = paragraph.attrib.get(text_prefix + "style-name", "")
                    style = self.styles.get(style_name, None)

                identation = 0
                if style:
                    identation = style.margin_left

                if not self.lists[-1].levels or self.getLastListLevel().identation < identation:
                    list_level_info = ListLevelInfo()

                    list_level_style = None
                    list_info = self.lists[-1]
                    list_style = self.list_styles.get(list_info.style_name, None)
                    if list_style:
                        list_level_style = list_style.levels[len(self.lists[-1].levels)]
                    elif list_info.style_name == "":
                        print 'Empty list style. This probably mean uncorrect rst list near: "%s"' % self.getElementText(child)[:20]
                    else:
                        print 'Unknown list style: "%s"' % list_info.style_name

                    # Child list will be of the same kind of the parent list.
                    if self.lists[-1].style_name in ["rststyle-bulletitem", "rststyle-blockquote-bulletitem"]:
                        list_level_info.current_index = 0

                    elif self.lists[-1].style_name in ["rststyle-enumitem", "rststyle-blockquote-bulletitem"]:
                        list_level_info.current_index = -1

                    elif list_level_style and list_level_style.num_format != "":
                        list_level_info.num_format = list_level_style.num_format
                        list_level_info.current_index = 0

                    else:
                        list_level_info.current_index = -1

                    self.lists[-1].levels.append(list_level_info)

#                   separator = ""
#                   if DEBUG_FLAG:
#                       separator += "prelist"
#                   separator += "\n"
#                   self.write(separator)

                else:
                    while self.lists[-1].levels and self.getLastListLevel().identation > identation:
                        self.lists[-1].levels.pop()

                    list_level_info = self.lists[-1].levels[-1]

                list_level_info.identation = identation
                list_level_info.is_bullet_inserted = False # Make sure the first paragraph get its bullet mark.

                # Update the item index of the item:
                if list_level_info.current_index >= 0:
                    list_level_info.current_index += 1

                self.transformNode(child)

            elif child.tag == table_prefix + "table":
                self.transformTableNode(child)

    def transform(self, content_path, styles_path, picture_dict, options):
        self.picture_dict = picture_dict
        self.options = options

        styles = {}
        list_styles = {}

        if os.path.isfile(styles_path):
            parser = xml.etree.ElementTree.XMLTreeBuilder()
            doc = xml.etree.ElementTree.parse(styles_path, parser)
            root = doc.getroot()

            styles.update(extractStylesFromRoot(root))
            list_styles.update(extractListStylesFromRoot(root))

        parser = xml.etree.ElementTree.XMLTreeBuilder()
        doc = xml.etree.ElementTree.parse(content_path, parser)
        root = doc.getroot()

        styles.update(extractStylesFromRoot(root))
        list_styles.update(extractListStylesFromRoot(root))

        self.styles = styles
        self.list_styles = list_styles

#       f = open("styles.tsn", "w")
#       for style in styles:
#           f.write(str(styles[style]))
#       f.close()

        body = root.find(office_prefix + "body")
        text = body.find(office_prefix + "text")

        self.open()
        self.transformNode(text)
        self.close()


def odt2rst(input_path, output_path, options):
    odt_pictures_hashes = unpackOdt(input_path, options.temp_folder)

    picture_dict = synchronizeImagesFolders(options.temp_folder, output_path, options.images_relative_folder, odt_pictures_hashes)

    content_path = os.path.join(options.temp_folder, "content.xml")
    styles_path = os.path.join(options.temp_folder, "styles.xml")

    rst_document = RstDocument(output_path)
    rst_document.transform(content_path, styles_path, picture_dict, options)

    if options.clean:
        cleanPack(options.temp_folder)


def version():
    print "1.0"


def help():
    print "odt2rst.py [--images images-folder] [--temp temp-folder] [--wrap-width width] odtfile [rstfile]"


def main():
    opts, args = getopt.getopt(sys.argv[1:], "vh", ["version", "help", "do-not-clean", "images=", "temp=", "wrap-width="])
    
    options = Options()
    
    images_relative_folder = "images"
    temp_folder = "."
    clean = True
    wrap_width = -1
    for o, v in opts:
        if o in ["-v", "--version"]:
            version()
            return

        if o in ["-h", "--help"]:
            help()
            return

        if o in ["--images"]:
            #images_relative_folder = v
            options.images_relative_folder = v

        if o in ["--temp"]:
            #temp_folder = v
            options.temp_folder = v
            
        if o in ["--wrap-width"]:
            options.wrap_width = int(v)

        if o in ["--do-not-clean"]:
            #clean = False
            options.clean = False

    input_file = ""
    if len(args) >= 1:
        input_file = args[0]

    if input_file == "":
        help()
        return

    name, ext = os.path.splitext(input_file)
    output_file = name + ".rst"
    if len(args) >= 2:
        output_file = args[1]

#   print "input", input_file
#   print "output:", output_file
#   print "temp:", temp_folder
#   print "images:", images_relative_folder

    odt2rst(input_file, output_file, options)


if __name__ == "__main__":
    main()
