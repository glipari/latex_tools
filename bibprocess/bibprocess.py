import sys
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
from sets import Set

au_key_map=Set()


class GenerationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    #record = type(record)
    # record = author(record)
    #record = editor(record)
    # record = journal(record)
    #record = keyword(record)
    #record = link(record)
    #record = page_double_hyphen(record)
    #record = doi(record)
    record = homogeneize_latex_encoding(record)
    record = convert_to_unicode(record)
    return record


def print_bibtex(i) :
    print "<pre>"
    print "@" + i["type"] + " {" + i["id"] + ','
    for k, x in i.items() :
        if k == "type" or k == "id": continue;
        try : 
            print "    "+k.encode('utf-8')+ " = {" + x.encode('utf-8') + "}, "
        except TypeError as e :
            print x
            raise
    print "}"
    print "</pre>"


def print_author(i) :
    print "<span class='bib_author'>",
    au_list = i["author"].split(' and ')    
    au_str = u''
    for x in au_list :
        a = u''
        b = u''
        if ',' in x :
            a,b = x.split(',')
        else :
            a = x
            b = u''
        au_str += b.strip(' {}') + ' ' + a.strip(' {}') + unicode(', ')
    au_str = au_str.encode('utf-8')
    try :
        print au_str, unicode("</span>")
    except UnicodeEncodeError as e :
        print i
        raise

def print_title(i) :
    print "<span class='bib_title'>", i["title"].strip().translate({ord(i):None for i in '{}'})+',', "</span>"


def print_jour(i) :
    print "<span class='bib_journal'>", i["journal"].strip(' {}')+',',
    if "volume" in i.keys() :
        print "vol.", i["volume"]+',', 
    if "number" in i.keys() :
        print "n.", i["number"] + ',', 
    if "pages" in i.keys() :
        print "pp.", i["pages"],
    print "</span>"


def print_journal(i) :
    if i["type"] == "article" :
        print_jour(i)
    elif  i["type"] in ["inproceedings"] :
        print "<span class='bib_conf'>", i["booktitle"].strip(' {}').encode('utf-8'), "</span>"
    else : 
        raise GenerationError("Unknown type")


def print_year(i) :
    if "year" in i.keys() :
        print "<span class='bib_year'>", i["year"].strip(), "</span>"
    else :
        raise GenerationError("Missing year field")

    
def print_extra(i) :
    print "<div class='bib_extra'>"
    if 'doi' in i.keys() :
        print "<span class='bib_doi'>[<a href='http://dx.doi.org/" + i['doi'] + "'>DOI</a>]</span>"
    if "localfile" in i.keys() :
        print "[<a href='" + i["localfile"] + "'>pdf</a>]"
    if "howpublished" in i.keys() :
        print "[<a href='" + i["howpublished"] + "'>url</a>]"
    if "link" in i.keys() :
        print "[<a href='" + i["link"] + "'>link</a>]"
    print "</div>"


def print_extended(i) :
    #print "<span class='bib_more'> More... </span>"
    print "<div class='bib_other'>"
    # print abstract
    if "abstract" in i.keys() :
        print "<span class='bib_abstract'><b>Abstract:</b>",
        print i["abstract"],
        print "</span>"

    print_bibtex(i)
    
    print "<button class='close_button' onclick='if(event.stopPropagation){event.stopPropagation();}event.cancelBubble=true; close_other(this)'>X</button>"
    print "</div>"


def print_key(i) :
    print "<div class='bib_key'>"
    # take first two letters of the first 3 authors (if any)
    au_list = i["author"].split(' and ')    
    au_str = u''
    c = 0
    for x in au_list :
        c = c + 1
        surname = u''
        name = u''
        if ',' in x :
            surname,name = x.split(',')
        elif ' ' in x :
            name,surname = x.split(' ')
        else :
            surname = x

        au_str += surname.strip(unicode(' {}'))[:1] 
        if c==3 : break

    au_str += i["year"]
    au_str = au_str.encode('utf-8')
    add_on = ''
    final = au_str + add_on
    c = 0;
    while final in au_key_map :
        c = c+1
        add_on = '-' + str(c)
        final = au_str + add_on

    au_key_map.add(final)
    print '[' + final + ']'
    print "</div>"

def print_ref(i) :
    #print_key(i)
    print "<div class='bib_ref' onclick='show_other(this.parentNode)'>"
    print_author(i)
    print_title(i)
    print_journal(i)
    print_year(i)
    if 'issn' in i.keys() :
        print "<span class='bib_issn'> ISSN:", i['issn'], "</span>"
    print "</div>"
    

def print_entry(i) :
    print "<div class='bib_elem' id='"+ i["id"] + "'>"
    try : 
        print_ref(i)
        print_extra(i)
        print_extended(i)
    except ValueError as e :
        print "VALUE ERROR on Entry:"
        print i
        raise
    except KeyError as e :
        print "KEY ERROR on Entry: " 
        print i
        raise
    print '</div>'

# ----------------------------------------------------


def print_books(list_entries) :
    # first filter on books, then print them

    return 0


def print_journals(list_entries) :
    jlist = filter(lambda x : x["type"] == "article", list_entries)
    jlist.sort(key=lambda x : x["year"], reverse=True) 
    print "<h2 class='bib_journal_title'> <a name='journals'>Journals</a> </h2> </hr>"
    print "<ol>"
    for x in jlist :
        print "<li>" 
        print_entry(x)
        print "</li>"
    print "</ol>"

def list_years(list_entries, at) :
    clist = filter((lambda x : x["type"] in at), list_entries)

    try : 
        years = list(set([ x["year"] for x in clist ]))
        years.sort(reverse=True)
    except KeyError as e : 
        print "Missing year at some point in the conference list"
        raise 

    return years, clist



def print_conferences(list_entries) :
    years, clist = list_years(list_entries, ["inproceedings"])

    print "<h2 class='bib_journal_title'> Conferences and workshops </h2> </hr>" 
    count = 1

    for y in years :
        print "<h3 class='bib_title_year'><a name='year"+y+"'>", y, "</a></h3>"
        cyl = filter(lambda x : x["year"] == y, clist)

        first_of_year = True;
        print "<ol>"
        for x in cyl :
            if first_of_year: 
                print "<li value=\"", count, "\">"
                first_of_year = False;
            else :
                print "<li value=\"", count, "\">"
            print_entry(x)
            count += 1
            print "</li>"
        print "</ol>"

def print_summary(list_entries) :
    years, _ = list_years(list_entries, ["inproceedings"])

    print "<a href='#journals'>Journals</a>, ",

    print "Conferences: ", 
    for y in years:
        print "<a href=\"#year"+y+"\">"+y+"</a>,", 
    print ""
    return

# ---------------------------------------------------------------
# ---------------------------------------------------------------

def main(argv=None) :
    if argv is None:
        argv = sys.argv
        # etc., replacing sys.argv with argv in the getopt() call.

    filename = ""

    parser = BibTexParser()
    parser.customization = customizations

    if len(argv) > 1 : 
        filename = argv[1]
    else:
        filename = "example.bib"

    with open(filename) as bibtex_file:
        bibtex_str = bibtex_file.read()

    bib_database = bibtexparser.loads(bibtex_str, parser=parser)

    #print_books(bib_database.entries)
    print_summary(bib_database.entries)
    print_journals(bib_database.entries)
    print_conferences(bib_database.entries)

    return 0;


if __name__ == "__main__":
    sys.exit(main())
