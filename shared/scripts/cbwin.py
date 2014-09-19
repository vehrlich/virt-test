import pyperclip
import sys
import os
from optparse import OptionParser


def return_nonrandom_str(length):
    """
    A method to return a nonrandom_string of the length determined by the input

    @param length, length of the string to be returned
    """
    input_string = "anonrandomstring_"
    finalstring = ""
    str_len = len(input_string)

    for i in xrange(int(length)):
        finalstring += input_string[i % str_len]

    return finalstring


def main(argv):
    '''
    usage to set image file in clipboard:     python clipboard.py --set <path>
    usage to get image file in clipboard:     python clipboard.py
    '''

    # Command line parser alternative
    parser = OptionParser()
    parser.add_option("-c", "--clear", dest="clear",
                     action="store_true", help="clear the clipboard")
    parser.add_option("-s", "--set", dest="setcb",
                     default='', help="Sets the local clip board")
    parser.add_option("-p", "--print", dest="setcb",
                     default='', help="Prints the text that was set")
    parser.add_option("-i", "--set_image", dest="setcbimage",
                     default='', help="Sets an image to local clip board")
    parser.add_option("-m", help="Saves an image to the /tmp directory",
                     dest="setfilename")
    parser.add_option("-r", "--file_copy", dest="setcb_file",
                     default='', help="Creates a file, Reads the text from " +
                     "a file and puts it onto the clipboard")
    parser.add_option("-f", "--file_paste", dest="pastecb_filename",
                     default='', help="Given a filename, the clipboard " +
                     "contents will be pasted")
    parser.add_option("-n", "--create_file", dest="setcb_lrgstr_file",
                     default='', help="Given a integer value a file will " +
                     "be created and put on the clipboard")

    # Read the command line parameters now
    (options, _) = parser.parse_args()

    if options.setcb:

        ssetcb = options.setcb
        # Set the clipboard text data
        pyperclip.setcb(ssetcb)

        print 'The text has been placed into the clipboard.'
    elif options.setfilename:
        # Saving image data
        print "This option is not supported yet"
    elif options.setcbimage:
        print 'This option in not supported yet.'
    elif options.clear:
        # Clear the clipboard
        pyperclip.setcb(None)
        print 'The clipboard has been cleared.'
    elif options.setcb_file:
        # Read a file and put the contents into the clipboard
        file_contents = open(options.setcb_file, 'r')
        pyperclip.setcb(file_contents.read())
        file_contents.close()
    elif options.pastecb_filename:
        # Get the text from the clipboard and write to a file
        print 'Getting the text from the clipboard'
        clipboard_text = pyperclip.getcb()
        print ('Starting to write the clipboard text to the file' +
               options.pastecb_filename)
        file_contents = open(options.pastecb_filename, 'w')
        file_contents.write(clipboard_text)
        print 'Writing of the clipboard text is complete'
        file_contents.close()
    elif options.setcb_lrgstr_file:
        # Create a non-random string of the size specified and write it to
        # a file and put it on the clipboard.
        finalstring = return_nonrandom_str(int(options.setcb_lrgstr_file))
        file_contents = open("StringLengthTest.txt", 'w')
        file_contents.write(finalstring)
        file_contents.close()
        file_contents = open("StringLengthTest.txt", 'r')
        pyperclip.setcb(file_contents.read())
        file_contents.close()
        print  ("Non random string put into file: /tmp/StringLengthTest. " +
                " The string has also been placed in the clipboard. " +
                "String of size " + options.setcb_lrgstr_file)
    else:
        # Read the clipboard text data.
        text = pyperclip.getcb()
        print 'clipboard=' + str(text)

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)
