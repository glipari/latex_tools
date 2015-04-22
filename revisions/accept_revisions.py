import sys
import getopt
import copy
import unittest

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

"""A simple exception: when reaching the end of the file and a closing
   brace has not been found
"""
class BraceError(Exception) :
    def __init__(self, value) :
        self.value = value
    def __str__(self):
        return 'Could not find closing brace:' + value

""" Index out of file exception
"""
class OutOfFile(Exception) :
    def __init__(self, l, i) :
        self.l = l
        self.i = i
    def __str__(self) :
        return 'Line/column out of bound: ' + l + ' : ' + i

"""The main class. It represents a position inside a list of lines
read from a txt file. The position is stored as line (the line number)
and column (the column number) of the point.  The class has a copy
constructor, a few mutable methods, but for the most part is
immutable.

"""
class PointInFile() :
    def __init__(self, lines, l, i) :
        self.lines = lines
        self.line = l
        self.column = i
        if self.line >= len(self.lines) or self.line < 0 :
            raise OutOfFile(self.line, self.column)
        if self.column < 0 or self.column >= len(self.lines[self.line]) :
            raise OutOfFile(self.line, self.column)

    def __str__(self):
        return '(%d, %d)' % (self.line, self.column)


    @staticmethod
    def copyConstructor(instance) :
        all_lines = instance.lines
        curr_line = copy.copy(instance.line)
        curr_col = copy.copy(instance.column)
        return PointInFile(all_lines, curr_line, curr_col)

    """
    Returns true if the cursor is beyond last character 
    """
    def eof(self) :
        return (self.line >= len(self.lines)) or (
            self.line == (len(self.lines)-1) and
            self.column >= (len(self.lines[self.line]))
        )
        
    """Compares two points. Returns -1, 0 or 1 if p1 comes first, is
    equal to p2 or comes later, respectively
    """ 
    @staticmethod
    def compare(p1, p2) :
        if p1.line < p2.line :
            return -1
        elif p1.line == p2.line and p1.column < p2.column :
            return -1
        elif p1.line == p2.line and p1.column == p2.column :
            return 0
        else :
            return 1

    """
    Given a list of points, returns the one tha comes first
    """
    @staticmethod
    def getMin(list_of_points) :
        if len(list_of_points) == 1 :
            return list_of_points[0]
        else :
            p1 = list_of_points[0]
            p2 = PointInFile.getMin(list_of_points[1:])
            if PointInFile.compare(p1, p2) <= 0 :
                return p1
            else:
                return p2

    @staticmethod
    def getMinIndex(list_of_points) :
        p = PointInFile.getMin(list_of_points)
        i=0
        for j in list_of_points : 
            if j == p : break
            i += 1
        return p, i

                
    """
    Returns the character at the current position
    """
    def getChar(self) :
        if self.eof() :
            raise OutOfFile(self.line, self.column)
        return self.lines[self.line][self.column]

    """
    Returns the current line
    """
    def getLine(self) :
        if self.eof() :
            raise OutOfFile(self.line, self.column)
        return self.lines[self.line]

    """
    Returns the current line until the current position
    """
    def getLineUntil(self) :
        if self.eof() :
            raise OutOfFile(self.line, self.column)
        return self.lines[self.line][:self.column]


    """
    returns from the current position until the end of the line
    """
    def getLineFrom(self) :
        if self.eof() :
            raise OutOfFile(self.line, self.column)
        return self.lines[self.line][self.column:]

    """
    returns from 2 lines before the current point until the current point
    """
    def getSnippetBefore(self) :
        if self.eof() :
            raise OutOfFile(self.line, self.column)
        init_line = max(self.line - 2, 0)
        end_line = self.line # min(self.line + 3, len(self.lines))
        output = ''
        for i in range(init_line, end_line) :
            output += self.lines[i]
        output += self.getLineUntil()
        return output

    """
    returns from the current point until two lines after
    """
    def getSnippetAfter(self) :
        if self.eof() :
            raise OutOfFile(self.line, self.column)
        init_line = self.line + 1
        end_line = min(self.line + 3, len(self.lines))
        output = self.getLineFrom()
        for i in range(init_line, end_line) :
            output += self.lines[i]
        return output

    """
    Advance the current position by 1. This function modifies the object
    """
    def advance(self) :
        if self.eof() :
            return
        self.column += 1
        if self.column >= len(self.lines[self.line]) :
            self.line += 1
            self.column = 0
        return

    """Move cursor to the beginning of the next line. This function
    modifies the object
    """
    def moveToNextLine(self) :
        if self.eof() :
            return
        self.line += 1;
        self.column = 0

    """Search for string s from the current position, and returns the
    point of beginning of the first occurrence. This function does not
    modify the object
    """
    def searchFor(self, s) :
        p1 = PointInFile.copyConstructor(self)
        # print 'POINT: ', p1
        while True :
            # print p1
            if p1.eof() :
                return p1
            elif p1.lines[p1.line].find('\\newcommand') != -1 :
                # print 'Found new command, moving to next line'
                p1.moveToNextLine()
            elif p1.lines[p1.line].find(s, p1.column) == -1 :
                # print 'search string ' + s + ' not found, moving to next'
                p1.moveToNextLine()
            else :
                # print 'search string ' + s + ' has been found!' 
                c = p1.lines[p1.line].find(s, p1.column)
                p1.column = c
                return p1


    def searchNextKeyword(self, klist) :
        plist = map((lambda x : self.searchFor(x)), klist )
        return PointInFile.getMinIndex(plist)
                
    """ 
    Returns the substring between two points in the file.
    The two points can span several lines.
    The function does not modify the object.
    """
    def getSubString(p1, p2) :
        if p1.lines != p2.lines : 
            raise Exception('Not the same file!')

        if p1.line > p2.line :
            return ''

        out = ''
        if p1.line < p2.line :
            out = p1.lines[p1.line][p1.column:]
            l = p1.line + 1
            c = 0
        else :
            l = p1.line
            c = p1.column

        while l < p2.line :
            out += p1.lines[l]
            l += 1
            c = 0
        
        if not p2.eof() :
            out += p1.lines[l][c:p2.column]

        return out

    """if the current character is at an opening parenthesis, returns a
    new PointInFile at the location of the corresponding balanced
    parenthesis.  This function does not mofify the object."""
    def findBalanced(self) :
        if self.getChar() != '{' :
            return False, self.advance()
            
        p1 = PointInFile.copyConstructor(self)
        while True :
            p1.advance()
            if p1.eof() :
                return False, p1 
            if p1.getChar() == '}' :
                return True, p1
            if p1.getChar() == '{' :
                flag, p1 = p1.findBalanced()
                if not flag:
                    return False, p1
                else :
                    p1.advance()
            

    """This function prints from two lines before p_start to two lines
    after p_end, and the text between p_start and p_end highlighted in
    blue
    """
    @staticmethod
    def printHighlight(keyword, p_start, p_end, subs=False):
        p1 = PointInFile.copyConstructor(p_start)
        p2 = PointInFile.copyConstructor(p_end)
        print '----------------------------------'
        print '@'+str(p1)
        output = p1.getSnippetBefore()
        output += bcolors.OKBLUE + keyword + '{'
        p1.column += len(keyword)
        p1.advance()
        output += PointInFile.getSubString(p1, p2)
        output += bcolors.ENDC
        if subs :
            p3 = p2.searchFor('{')
            flag, p3 = p3.findBalanced()
            p3.advance()
            output += bcolors.OKGREEN + PointInFile.getSubString(p2, p3) 
            output += bcolors.ENDC
            p2 = p3
        
        output += p2.getSnippetAfter()
        print output
        print '----------------------------------'


class TestPointInFile(unittest.TestCase) :
    def setUp(self) :
        self.text_lines = [
            '  \\newcommand{\\added}[1]{definition{}}\n',
            '\n',
            '\\section{My section}\n',
            'This is some text, \\added{text to add}, and end of line\n',
            'This is another line, without additions\n',
            'This is an added spawning several lines \\added{\n',
            'text to add on the second line\n',
            'and on the third line} and text already there\n',
            'now a delete, \\deleted{this text must be \n',
            'deleted}, and the continuation\n',
            '\\added{ad} and \\deleted{to delete} on the same \\substituted{to del}{to',
            'insert} and the end is close\n',
            'end of the file\n'
            ]
        self.point = PointInFile(self.text_lines, 0, 0)
        

    def test_found(self) :
        p1 = self.point.searchFor('\\added')
        self.assertEqual(p1.line, 3)
        self.assertEqual(p1.column, 19)
        p1.column += len('\\added')
        self.assertEqual(p1.column, 25)
        self.assertEqual(p1.getChar(), '{')
        flag, p2 = p1.findBalanced()
        self.assertTrue(flag)
        self.assertEqual(p2.line, 3)
        self.assertEqual(p2.column, 37)

        p3 = p2.searchFor('\\added')
        self.assertEqual(p3.line, 5)
        p3.column += len('\\added')
        flag, p4 = p3.findBalanced()
        self.assertTrue(flag)
        self.assertEqual(p4.line, 7)
        p3.advance()
        sub = PointInFile.getSubString(p3, p4)
        self.assertEqual(sub, '\ntext to add on the second line\nand on the third line')

    def test_min(self) :
        p1 = self.point.searchFor('\\added')
        p2 = self.point.searchFor('\\deleted')
        p3 = self.point.searchFor('\\substituted')
        p = PointInFile.getMin([p1, p2, p3])
        self.assertEqual(p, p1)
        self.assertEqual(p.line, 3)
        p.advance()
        p.advance()

        p4 = p.searchFor('\\added')
        p5 = p.searchFor('\\deleted')
        p6 = p.searchFor('\\substituted')
        p = PointInFile.getMin([p4, p5, p6])
        self.assertEqual(p, p4)
        self.assertEqual(p.line, 5)
        p.advance()
        p.advance()

        p7 = p.searchFor('\\added')
        p8 = p.searchFor('\\deleted')
        p9 = p.searchFor('\\substituted')
        p = PointInFile.getMin([p7, p8, p9])
        self.assertEqual(p, p8)
        self.assertEqual(p.line, 8)
        p.advance()
        p.advance()

        p1 = p.searchFor('\\added')
        p2 = p.searchFor('\\deleted')
        p3 = p.searchFor('\\substituted')
        p = PointInFile.getMin([p1, p2, p3])
        self.assertEqual(p, p1)
        self.assertEqual(p.line, 10)
        p.advance()
        p.advance()

        p1 = p.searchFor('\\added')
        p2 = p.searchFor('\\deleted')
        p3 = p.searchFor('\\substituted')
        p = PointInFile.getMin([p1, p2, p3])
        self.assertEqual(p, p2)
        self.assertEqual(p.line, 10)
        p.advance()
        p.advance()
        
        p1 = p.searchFor('\\added')
        p2 = p.searchFor('\\deleted')
        p3 = p.searchFor('\\substituted')
        p = PointInFile.getMin([p1, p2, p3])
        self.assertEqual(p, p3)
        self.assertEqual(p.line, 10)

            
    def test_min_all(self) :
        klist = ['\\added', '\\deleted', '\\substituted']
        p, j = self.point.searchNextKeyword(klist)
        self.assertEqual(j, 0)
        self.assertEqual(p.line, 3)
        p.column += len(klist[j])
        flag, p = p.findBalanced()
        self.assertTrue(flag)

        p, j = p.searchNextKeyword(klist)
        self.assertEqual(j, 0)
        self.assertEqual(p.line, 5)
        p.column += len(klist[j])
        flag, p = p.findBalanced()
        self.assertTrue(flag)


added_macro = '\\added'
subs_macro = '\\substituted'
del_macro = '\\deleted'
klist = [added_macro, del_macro, subs_macro]

def accept_added(p_start, i) :
    p = PointInFile.copyConstructor(p_start)
    p.column += len(klist[i])
    flag, q = p.findBalanced()
    p.advance()
    out = PointInFile.getSubString(p,q)
    q.advance()
    return out, q

def reject_added(p_start, i) :
    p = PointInFile.copyConstructor(p_start)
    p.column += len(klist[i])
    flag, q = p.findBalanced()
    q.advance()
    return '', q

def skipping(p_start, i) :
    p = PointInFile.copyConstructor(p_start)
    p.column += len(klist[i])
    flag, q = p.findBalanced()
    # substitute (i=2), has two arguments
    if i==2 :
        q = q.searchFor('{')
        flag, q = q.findBalanced()

    q.advance()
    q.advance()

    out = PointInFile.getSubString(p_start, q)
    return out, q


def accept_substituted(p_start, i) :
    p = PointInFile.copyConstructor(p_start)
    p.column += len(klist[i])
    flag, p = p.findBalanced()
    p = p.searchFor('{')
    flag, q = p.findBalanced()
    p.advance()
    out = PointInFile.getSubString(p, q)
    q.advance()
    return out, q


def reject_substituted(p_start, i) :
    p = PointInFile.copyConstructor(p_start)
    p.column += len(klist[i])
    flag, q = p.findBalanced()
    p.advance()
    out = PointInFile.getSubString(p, q)
    q = q.searchFor('{')
    flag, q = q.findBalanced()
    q.advance()
    return out, q


InputFunctions = {
    'a' : { 0 : accept_added, 1 : reject_added,   2: accept_substituted},
    'r' : { 0 : reject_added, 1 : accept_added,   2: reject_substituted},
    's' : { 0 : skipping,     1 : skipping,       2: skipping}
}


def main(argv=None) :
    if argv is None :
        argv = sys.argv

    try:
        opts, args = getopt.getopt(argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print "Supprime accept/reject revisions from latex file"
            sys.exit(0)

    myfile = open(args[0], 'r')
    fout = open(args[0]+'_new.tex', 'w')
    
    p_curr = PointInFile(myfile.readlines(), 0, 0)
    p_old = PointInFile.copyConstructor(p_curr)
    
    while True:
        p_curr, i = p_curr.searchNextKeyword(klist)
        if p_curr.eof() : break

        p_start = PointInFile.copyConstructor(p_curr)
        p_start.column += len(klist[i])
        flag, p_end = p_start.findBalanced()
        p_start.advance()
        p_end.advance()
        PointInFile.printHighlight(klist[i], p_curr, p_end, i==2)
        c = raw_input('(A)ccept, (R)eject, (S)kip ?') 
        out, p_new = InputFunctions[c][i](p_curr, i)
        fout.write(PointInFile.getSubString(p_old, p_curr))
        fout.write(out)

        newout = p_curr.getSnippetBefore()
        newout += bcolors.BOLD
        newout += out 
        newout += bcolors.ENDC
        newout += p_new.getSnippetAfter()

        print '\n------ New text --------' 
        print newout
        print '------------------------\n\n'

        p_old = PointInFile.copyConstructor(p_new)
        p_curr = p_new
        # print '--- New p_curr = ' + str(p_curr)

    # last piece
    fout.write(PointInFile.getSubString(p_old, p_curr))

    print 'DONE'

    


if __name__ == "__main__":
    # sys.exit(unittest.main())
    sys.exit(main())
