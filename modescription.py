#This file is part appstryton app for Flask.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
import os
import docutils.core

def get_description(lang, src, name):
    '''Get Description module from doc rst'''
    description = ''

    doc_path = '%s/doc/%s/index.rst' % (src, lang)
    if os.path.exists(doc_path):
        return read_rst(doc_path)

    doc_path = '%s/doc/index.rst' % (path)
    if os.path.exists(doc_path):
        return read_rst(doc_path)

def read_rst(doc_path):
    f = open(doc_path, "r")
    description = f.read()

    def rst2html(source, source_path=None, source_class=docutils.io.StringInput,
                 destination_path=None, reader=None, reader_name='standalone',
                 parser=None, parser_name='restructuredtext', writer=None,
                 writer_name='html', settings=None, settings_spec=None,
                 settings_overrides=None, config_section=None,
                 enable_exit_status=None):
        """
        Set up & run a `Publisher`, and return a dictionary of document parts.
        Dictionary keys are the names of parts, and values are Unicode strings;
        encoding is up to the client. For programmatic use with string I/O.

        For encoded string input, be sure to set the 'input_encoding' setting to
        the desired encoding. Set it to 'unicode' for unencoded Unicode string
        input. Here's how::

        publish_parts(..., settings_overrides={'input_encoding': 'unicode'})

        Parameters: see `publish_programmatically`.
        """
        output, pub = docutils.core.publish_programmatically(
            source=source, source_path=source_path, source_class=source_class,
            destination_class=docutils.io.StringOutput,
            destination=None, destination_path=destination_path,
            reader=reader, reader_name=reader_name,
            parser=parser, parser_name=parser_name,
            writer=writer, writer_name=writer_name,
            settings=settings, settings_spec=settings_spec,
            settings_overrides=settings_overrides,
            config_section=config_section,
            enable_exit_status=enable_exit_status)
        return pub.writer.parts['fragment'], pub.document.reporter.max_level, pub.settings.record_dependencies

    output, error_level, deps = rst2html(
            description, settings_overrides={
                'initial_header_level': 2,
                'record_dependencies': True,
                'stylesheet_path': None,
                'link_stylesheet': True,
                'syntax_highlight': 'short',
            })
    return output

