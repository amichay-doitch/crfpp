"""
This module provides all logging needs. 
It supports logging verbose, debug, info, warning and error messages to the console, or to the console 
and a file. The oridnary usage of this module is by getting the instance of the default logger like this:

    _logger = logger.getLogger()

In addition it gives special support for logging options by using the Headers class.
"""
from optparse import OptionParser, OptionGroup
import sys, os.path, logging, re
from time import strftime
from utils.ordered_dict import OrderedDict
import inspect

VERBOSE = logging.VERBOSE = 5
log_levels = {
    'verbose':  logging.VERBOSE,
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warning':  logging.WARNING,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL
}
log_level_names = sorted(log_levels, key=log_levels.get)
log_format = "%(levelname)7s-%(name)s %(asctime)s %(message)s"
log_datefmt = "%H:%M:%S"
logging.addLevelName(logging.VERBOSE, "VERBOSE")
logging.basicConfig(stream=sys.stdout, format=log_format, datefmt=log_datefmt, level=logging.INFO)

class MyLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
    def verbose(self, msg, *args, **kwargs):
        """
        Emit messages to "verbose" level which is a lower level than deubg, used to provide very detailed information. 
        
        :param: message to emit to logging level
        """
        self.log(logging.VERBOSE, msg, *args, **kwargs)
logging.setLoggerClass(MyLogger)

def getLogger(name=None):
    """
    Get instance of main logger. The common usage is::

    _logger = logger.getLogger()
    """
    if not name:
        frm = inspect.stack()[1]
        module = inspect.getmodule(frm[0])
        if module:
            name = module.__name__
            if name == "__main__":
                name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        else:
            name = "*SHELL*"

    return logging.getLogger(name)


def add_log_options_to_parser(parser):
    """
    Add logging options to options parser

    :param parser: instance of OptionParser
    """
    if not isinstance(parser, OptionParser):
        raise Exception("Argument should be instance of optparse.OptionParser")

    l_grp = OptionGroup(parser, "Logging Options", "Control creation and use of a log file, and the level of messages")

    l_grp.add_option("--log", metavar="FILE", help="Write log messages to FILE.")
    l_grp.add_option("--append-log", action="store_true", default=False,
                     help="Append to the log file.  Default: overwrite.")
    l_grp.add_option("-v", "--verbose", choices=log_level_names, default='info', metavar="LEVEL",
                     help="Set verbosity LEVEL to one of {0}.  Default: '%default'.".format(log_level_names))
    parser.add_option_group(l_grp)


def handle_log_options(options):
    """
    Makes the main logger instance work on the logging level sent from the command line in option -verbose
    and optionally creates a log file from option --log.

    :param options: options object returned by
    """
    logging.getLogger("").setLevel(log_levels[options.verbose])
    if options.log:
        handler = logging.FileHandler(options.log, 'a' if options.append_log else 'w')
        handler.setFormatter(logging.Formatter(log_format, log_datefmt))
        handler.setLevel(logging.VERBOSE)
        logging.getLogger("").addHandler(handler)
        logging.basicConfig(filename=options.log,level=logging.DEBUG)


class Headers(OrderedDict):
    """
    This class is used for printing command line options through the logger or to an xml file.
    It does this by storing a dictionary containing the keys and values of the different options added using "append".
    The Header class also extracts descriptive information from the provided option_parser instance.

    :param opt_parser: instance of a configured option_parser

    Example::

        headers = logger.Headers(parser.opt_parser)
        headers.append("FSDB File", options.filename)
        headers.append("Debug Counter", options.signal)
        headers.append("Counter Value", options.dcval)
        headers.emit(logger=_logger)

    """
    def __init__(self, opt_parser):
        from utils import stringize
        super(Headers, self).__init__()
        self._title = opt_parser.prog if opt_parser.prog \
                                      else os.path.basename(sys.argv[0])
        if opt_parser.description:
            self._title += " - " + \
                opt_parser.description.replace('\n', '\n'+' '*(len(self._title)+3))
        self["Command line"] = ' '.join(map(stringize, sys.argv[1:]))

    def append(self, key, value):
        """
        add an option 

        :param key: the option key
        :param key: the option value

        """
        self[key] = value
        return self

    def emit(self, logger = None, fout = None, comment_prefix='#'):
        """
        Print info on each option to file or to logger.
        
        :param logger: instance of MyLogger()
        :param fout: file descriptor 
        :param comment_prefix: Line prefix when writing to a file 
        """

        if "Produced at" not in self:
            self["Produced at"] = strftime("%Y-%m-%d %H:%M:%S")
        w = max(len(k) for k in self.iterkeys())
        if logger:
            for line in self._title.split('\n'):
                logger.info(line)
            for k, v in self.iteritems():
                logger.info("  {0:<{w}s}: {1}".format(k, v, w=w))
        if fout:
            for line in self._title.split('\n'):
                fout.write("{0} {1}\n".format(comment_prefix, line))
            for k, v in self.iteritems():
                fout.write("{0}   {1:<{w}s}: {2}\n".format(comment_prefix, k, v, w=w))

    @classmethod
    def keyword(cls, k):
        """
        Used to convert the option key string to a format acceptable by XML and GML file formats. 
        It includes removing spaces and some illegal characters (???, ?_?, ?-?), and converting to Camel Case.

        :param k: string containing option key
        """
        return re.sub('[?_\-]', ' ', k).title().replace(' ', '')

    def emit_xml(self, parent):
        """
        Adds a "headers" element to the xml document containing the options 

        :param parent: root element in an xml document

        """
        if "Produced at" not in self:
            self["Produced at"] = strftime("%Y-%m-%d %H:%M:%S")
        doc = parent.ownerDocument
        elem = parent.appendChild(doc.createElement("headers"))
        for k, v in self.iteritems():
            h = elem.appendChild(doc.createElement(self.keyword(k)))
            h.appendChild(doc.createTextNode(str(v)))

    def as_dict(self):
        """
        not used
        """
        d = {}
        for k, v in self.iteritems():
            d[self.keyword(k)] = str(v)
        return d
