import os
import sys
import json
import shutil
import tempfile
import itertools
import datetime
import string
import re
from contextlib import contextmanager
from future.utils import iteritems

import demo_config


# parses a datetime field in Elba format and groups the date+time and timezone chunks
DATETIME_RE = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(Z|[+-]\d{2}:\d{2})$')


def cache_value(field):
    """Returns the DB cache value corresponding to the given `field` name."""

    import demo_cmds

    rv = demo_cmds.db_cache(prefix=field)
    return json.loads(rv)[field]


def dict_eq(d1, d2):
    """Checks if two dictionaries are equal."""

    dump1 = json.dumps(d1, sort_keys=True)
    dump2 = json.dumps(d2, sort_keys=True)
    return dump1 == dump2


def unzip_file(data):
    """Returns `data` (a string containing a ZIP) unzipped."""

    import zipfile
    import StringIO

    data = StringIO.StringIO(data)
    f = zipfile.ZipFile(data, 'r', compression=zipfile.ZIP_DEFLATED)
    return f.read(f.namelist()[0])


def decompress_gzip(data):
    """Returns the decompressed GZIP stored in `data`."""

    import zlib
    window_bits = 15 + 16
    return zlib.decompress(data, window_bits)


def decompress_zlib(data):
    """Returns the decompressed ZLIB stored in `data`."""

    import zlib
    window_bits = 15
    return zlib.decompress(data, window_bits)


def decompress(data, compression_format):
    """Decompresses the content of `data` interpreting it in the specified `compression_format`
    (compression_format) enum."""

    decompressors = {
        'compression_format_zip': unzip_file,
        'compression_format_gzip': decompress_gzip,
        'compression_format_zlib': decompress_zlib
    }
    return decompressors[compression_format](data)


def get_constants():
    """Returns the constants from the reflection.
    This is a hack so the spec doc generators can access the constants because there's a conflict
    with the `constants.py` in the descriptions."""

    import inspect
    path = os.path.dirname(inspect.stack()[0][1])
    sys.stderr.write(path + '\n')

    import imp
    return imp.load_source('constants', path + '/constants.py')


@contextmanager
def tempdir():
    """Context manager that creates a temporary directory and destroys it at exit."""

    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path)
        except IOError:
            sys.stderr.write('Failed to clean up temp dir {}'.format(path))


@contextmanager
def cd(path):
    """Context manager that changes the working dir to `path` and returns to the original at exit."""

    prev_path = os.getcwd()
    os.chdir(path)

    try:
        yield
    finally:
        os.chdir(prev_path)


def grouper(iterable, n, fill_value=None, use_fill_value=False):
    """Collect data into fixed-length chunks or blocks.
    If `iterable`s length is not a multiple of `n` and `use_fill_value` is True, then the last chunk
    will be extended to have length `n`.

    >>> list(grouper('ABCDEFG', 3, fill_value='x', use_fill_value=True))
    [(A, B, C), (D, E, F), (G, x, x)]
    """

    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return

        # completes the last chunk, if required
        if use_fill_value and len(chunk) != n:
            chunk = tuple(list(chunk) + [fill_value] * (n - len(chunk)))
        yield chunk


def get_last_record(*rec_types):
    """Gets the last record of a given rec type set type (or the last record of any type if not
    specified).
    This function returns only 1 record, NOT 1 for each type."""

    import demo_cmds

    if rec_types:
        rv = demo_cmds.db_data(rec_types=list(
            rec_types), max_output_recs=1, reversed=True)
    else:
        rv = demo_cmds.db_data(max_output_recs=1, reversed=True)
    assert_no_error(rv)
    return json.loads(rv)['data'][0]


def count_records(rec_type):
    """Counts the records of the specified `rec_type`."""

    import demo_cmds

    rv = demo_cmds.db_data(rec_types=[rec_type])
    return len(json.loads(rv)['data'])


def current_date(fmt='%Y-%m-%d'):
    return datetime.datetime.today().strftime(fmt)


def current_datetime(fmt='%Y-%m-%dT%H:%M:%S', timezone='Z', offset=None):
    """Returns the current datetime in the specified format.
    If `offset` is not None, it should be a `timedelta` object that will be applied to the current
    datetime.
    """

    offset = offset or datetime.timedelta(0)
    return (datetime.datetime.today() + offset).strftime(fmt) + timezone


def device_datetime(fmt='%Y-%m-%dT%H:%M:%S', offset=None):
    """Returns the current device datetime in the specified format.
    If `offset` is not None, it should be a `timedelta` object that will be applied to the current
    datetime.
    """

    from demo_cmds import config_get_datetime

    current = json.loads(config_get_datetime())['date']
    current, tz = DATETIME_RE.match(current).groups()

    offset = offset or datetime.timedelta(0)
    return (datetime.datetime.strptime(current, fmt) + offset).strftime(fmt) + tz


def check_obj(obj, expected):
    """Checks if two objects match."""
    for k, v in iteritems(expected):
        if v is None:
            assert k not in obj, '%s shouldn\'t be present' % k
        else:
            assert k in obj, '%s should be present' % k
            assert obj[k] == v, '%s differs (%s expected, %s found)' % (
                k, v, obj[k])


def assertion_msg_fmt(cmd_output, msg=None, extra_msg=None):
    """Formats an error message to use it in an assertion."""
    full_msg = ', '.join(filter(None, [msg, extra_msg]))
    if full_msg:
        return '%(full_msg)s: %(cmd_output)s' % locals()
    else:
        return cmd_output


def assert_no_error(cmd_output, extra_msg=None):
    """Raises an error if the command failed, otherwise, returns loaded json"""
    try:
        cmd_output = json.loads(cmd_output)
    except TypeError:
        pass
    assert 'error' not in cmd_output, assertion_msg_fmt(
        cmd_output, extra_msg=extra_msg)

    return cmd_output


def assert_error(cmd_output, error_type=None, error_msg=None, error_data=None, extra_msg=None):
    """Raises an error if the command did not fail.
    If `error_type` is specified, then checks for that specific error
    and otherwise it fails.
    If `error_msg` is not None, checks `cmd_output` contains the field 'error_msg' and matches
    `error_msg` value.
    If `error_data` is not None, checks `cmd_output` contains the field 'error_data' and matches
    `error_data` value.
    `extra_msg` is an object to append to the assertion message in case it fails, concatenated
    before `cmd_output`."""
    try:
        cmd_output = json.loads(cmd_output)
    except TypeError:
        pass

    assert 'error' in cmd_output, assertion_msg_fmt(
        cmd_output, extra_msg=extra_msg)
    if error_type is not None:
        assert cmd_output['error'] == error_type, assertion_msg_fmt(
            cmd_output, extra_msg=extra_msg)

    if error_msg is not None:
        assert cmd_output['error_msg'] == error_msg, assertion_msg_fmt(
            cmd_output, extra_msg=extra_msg)

    if error_data is not None:
        assert cmd_output['error_data'] == error_data, assertion_msg_fmt(
            cmd_output, extra_msg=extra_msg)

    return cmd_output


def assert_no_error_batch(batch_output, extra_msg=None, cmd_idx=None):
    """Raises an error if either the batch command or any of the subcommands failed.
    `extra_msg` is an object to append to the assertion message in case it fails, concatenated
    before `cmd_output`.
    If `cmd_idx` is not None, checks that the specified command did not fail."""
    try:
        batch_output = json.loads(batch_output)
    except TypeError:
        pass

    assert_no_error(batch_output, extra_msg=extra_msg)
    if cmd_idx is None:
        for cmd_output in batch_output['batch_output']:
            assert_no_error(cmd_output, extra_msg=extra_msg)
    else:
        assert_no_error(batch_output['batch_output']
                        [cmd_idx], extra_msg=extra_msg)


def assert_error_batch(batch_output, error_type=None, error_msg=None, extra_msg=None, cmd_idx=None):
    """Raises an error if none of the commands failed.
    If `error_type` is specified, then checks for that specific error
    and otherwise it fails.
    If `error_msg` is not None, checks `cmd_output` contains the field 'error_msg' and matches
    `error_msg` value.
    `extra_msg` is an object to append to the assertion message in case it fails, concatenated
    before `cmd_output`.
    If `cmd_idx` is not None, checks that the specified command was the one that failed."""
    try:
        batch_output = json.loads(batch_output)
    except TypeError:
        pass

    assert_no_error(batch_output, extra_msg=extra_msg)
    if cmd_idx is None:
        for cmd_output in batch_output['batch_output']:
            try:
                assert_error(cmd_output, error_type=error_type,
                             error_msg=error_msg, extra_msg=extra_msg)
                break
            except AssertionError as e:
                pass
        else:
            assert False, assertion_msg_fmt(
                batch_output, msg='was expecting a command with error', extra_msg=extra_msg)
    else:
        assert len(batch_output['batch_output']) >= cmd_idx + 1,\
            assertion_msg_fmt(
                batch_output, msg='was expecting an error in command %d' % cmd_idx, extra_msg=extra_msg)
        assert_error(batch_output['batch_output'][cmd_idx],
                     error_type=error_type,
                     error_msg=error_msg,
                     extra_msg=extra_msg)


def log(msg):
    """Prints `msg` based on verbosity level."""

    if demo_config.VERBOSE_TESTS:
        print(msg)


# console colors
_COLORS = {
    'header': '\x1b[01;35m',
    'info': '\x1b[01;34m',
    'ok': '\x1b[01;32m',
    'warning': '\x1b[01;33m',
    'fail': '\x1b[01;31m',
    'endc': '\x1b[0m'
}


def fmt(color, msg):
    return '%s%s%s' % (color, msg, _COLORS['endc'])


# include format functions for each type in _COLORS and register them in the module
for color_name, color_fmt in iteritems(_COLORS):
    def _make_fmt_fun(c):
        def fmt_fun(msg):
            return fmt(c, msg)
        return fmt_fun

    _fmt = _make_fmt_fun(color_fmt)
    _fmt.__name__ = 'fmt_%s' % color_name
    globals()[_fmt.__name__] = _fmt


def display_assert_lines(expected_lines):
    ''' Ensere that the lines in the display match the expected ones'''
    from demo_cmds import display_read

    rv = json.loads(display_read())
    assert_no_error(rv)

    lines = [line.encode('utf-8') for line in rv['lines']]
    assert lines == expected_lines, "%s != %s" % (lines, expected_lines)

    return lines


def convert_key_sequence(sequence):
    ''' Convert a sequence of keys to their correct ecr_key enums'''

    # Add prefix 'char_' to every key if it's a letter a-zA-Z.
    if isinstance(sequence, str):
        sequence = ["char_{}".format(x) if x in string.letters else x for x in sequence]

    keys = ['ecr_key_{}'.format(x) for x in sequence]

    return keys


def send_key_sequence(sequence):
    ''' Send a sequence of keys '''
    from demo_cmds import keyboard_events_append
    from consts import KEYBOARD_EVENTS_COMMAND_BUFFER_LENGTH

    key_buf_len = KEYBOARD_EVENTS_COMMAND_BUFFER_LENGTH
    # Add prefix 'char_' to every key if it's a letter a-zA-Z.
    if isinstance(sequence, str):
        sequence = ["char_{}".format(
            x) if x in string.letters else x for x in sequence]

    # Send keyboard_events taking the buffer length into account
    while sequence:
        keys = ['ecr_key_{}'.format(x) for x in sequence[:key_buf_len]]
        assert_no_error(keyboard_events_append(keys=keys))
        sequence = sequence[key_buf_len:]


def send_sequence_and_check_display(sequence, display_lines):
    ''' Send a sequence of keys and check the display'''

    send_key_sequence(sequence)
    lines = display_assert_lines(display_lines)
    log("Display:")
    idx = 1
    for line in lines:
        log("\t{}: |{}|".format(idx, line))
        idx += 1
    log("")
    return lines


def normalize_subject(subject):
    """Formats the subject content so the test is compatible with different OpenSSL versions."""

    return re.sub(' = ', '=', subject)


def assert_equal(expected, obtained):
    assert expected == obtained, 'Expected %r but got %r' % (expected, obtained)
