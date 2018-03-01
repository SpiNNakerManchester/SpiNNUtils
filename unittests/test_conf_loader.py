#pylint: disable=redefined-outer-name, unused-argument
import unittests  # CRITICAL: *THIS* package!
from testfixtures import LogCapture
import spinn_utilities.conf_loader as conf_loader
from spinn_utilities.configs.unexpected_config_exception \
    import UnexpectedConfigException
from spinn_utilities.configs.no_config_found_exception import \
    NoConfigFoundException
import spinn_utilities.testing.log_checker as log_checker

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import os
import pytest

CFGFILE = "configloader.cfg"
CFGPATH = os.path.join(os.path.dirname(unittests.__file__), CFGFILE)
ONEFILE = "config_one.cfg"
ONEPATH = os.path.join(os.path.dirname(unittests.__file__), ONEFILE)
TWOFILE = "config_two.cfg"
TWOPATH = os.path.join(os.path.dirname(unittests.__file__), TWOFILE)
VALIDATION_PATH = os.path.join(os.path.dirname(unittests.__file__),
                               "validation_config.cfg")
NOTTHERE = "test_config_for_spinnutils_unittests.txt"
NOTTHEREPATH = os.path.join(os.path.expanduser("~"), ".{}".format(NOTTHERE))


@pytest.fixture
def not_there():
    if os.path.exists(NOTTHEREPATH):
        # Check existing is a config from previsous test run
        config = ConfigParser.ConfigParser()
        config.read(NOTTHEREPATH)
        # Remove it
        os.remove(NOTTHEREPATH)
    return NOTTHEREPATH


@pytest.fixture
def default_config():
    with open(CFGPATH) as the_file:
        return the_file.read()


@pytest.fixture
def mach_spec(tmpdir):
    msf = tmpdir.join("machspec.cfg")
    msf.write("[Machine]\nmachineName=foo\nversion=5\n")
    return str(msf)


def test_basic_use(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        f.write(default_config)
        config = conf_loader.load_config(CFGFILE, [])
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foobob"]
        assert config.get("sect", "foobob") == "bar"
        assert config.get("sect", "fooBob") == "bar"
        assert config.get("sect", "foo_bob") == "bar"


def test_as_default(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        f.write(default_config)
        config = conf_loader.load_config(CFGFILE, [CFGPATH])
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foobob"]
        assert config.get("sect", "foobob") == "bar"
        assert config.get("sect", "fooBob") == "bar"
        assert config.get("sect", "foo_bob") == "bar"


def test_different_value(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config.replace("bar", "cat")
        f.write(default_config)
        config = conf_loader.load_config(CFGFILE, [CFGPATH])
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foobob"]
        assert config.get("sect", "foobob") == "cat"


def test_new_option(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config + "sam=cat\n"
        f.write(default_config)
        with pytest.raises(UnexpectedConfigException):
            conf_loader.load_config(CFGFILE, [CFGPATH],
                                    validation_cfg="blank.cfg")


def test_new_section_validation(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config + "[Pets]\nsam=cat\n"
        f.write(default_config)
        conf_loader.load_config(CFGFILE, [CFGPATH], validation_cfg="blank.cfg")


def test_dead_section(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config + "[Pets]\nsam=cat\n"
        f.write(default_config)
        with pytest.raises(UnexpectedConfigException):
            conf_loader.load_config(CFGFILE, [CFGPATH],
                                    validation_cfg=VALIDATION_PATH)


def test_previous_value(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config.replace("bar", "alpha")
        f.write(default_config)
        with pytest.raises(UnexpectedConfigException):
            conf_loader.load_config(CFGFILE, [CFGPATH],
                                    validation_cfg=VALIDATION_PATH)


def test_new_section(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config + "[other]\nsam=cat\n"
        f.write(default_config)
        config = conf_loader.load_config(CFGFILE, [CFGPATH])
        assert config.sections() == ["sect", "other"]
        assert config.options("sect") == ["foobob"]
        assert config.get("sect", "foobob") == "bar"
        assert config.get("other", "sam") == "cat"


def test_use_one_default(not_there):
    with pytest.raises(NoConfigFoundException):
        conf_loader.load_config(NOTTHERE, [CFGPATH])
    # Load the now created file
    config = ConfigParser.ConfigParser()
    config.read(NOTTHEREPATH)
    assert config is not None
    assert config.sections() == ["sect"]
    assert config.options("sect") == ["foobob"]
    assert config.get("sect", "foobob") == "bar"


def test_use_two_default(tmpdir, default_config, not_there):  # @UnusedVariable
    with pytest.raises(NoConfigFoundException):
        conf_loader.load_config(NOTTHERE, [ONEPATH, TWOPATH])
    # Load the now created file
    config = ConfigParser.ConfigParser()
    config.read(NOTTHEREPATH)
    assert config is not None
    assert config.sections() == ["sect", "extra"]
    assert config.options("sect") == ["foo", "bar"]
    assert config.get("sect", "foo") == "notbar"
    assert config.options("extra") == ["bob", "sam"]
    assert config.get("extra", "sam") == "cat"


def test_None_machine_spec_file(tmpdir, default_config):
    with tmpdir.as_cwd():
        with LogCapture() as lc:
            f = tmpdir.join(CFGFILE)
            f.write(default_config + "\n[Machine]\nmachine_spec_file=None\n")
            config = conf_loader.load_config(CFGFILE, [])
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foobob"]
            assert config.get("sect", "foobob") == "bar"
            log_checker.assert_logs_info_not_contains(lc.records, "None")


def test_intermediate_use(tmpdir, default_config, mach_spec):
    with tmpdir.as_cwd():
        with LogCapture() as lc:
            f = tmpdir.join(CFGFILE)
            f.write(default_config + "\n[Machine]\nmachine_spec_file=" +
                    mach_spec + "\n")
            config = conf_loader.load_config(CFGFILE, [])
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foobob"]
            assert config.get("sect", "foobob") == "bar"
            assert config.options("Machine") == ["machinename", "version"]
            assert config.get("Machine", "MachineName") == "foo"
            assert config.getint("Machine", "VeRsIoN") == 5
            log_checker.assert_logs_info_contains(lc.records, CFGFILE)


def test_advanced_use(tmpdir, default_config):
    def parseAbc(parser):
        f = parser.getfloat("Abc", "def")
        parser.set("Abc", "ghi", f*3)
        parser.remove_option("Abc", "def")

    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        f.write(default_config + "\n[Abc]\ndef=1.25\n")
        config = conf_loader.load_config(CFGFILE, [],
                                         config_parsers=[("Abc", parseAbc)])
        assert config.options("Abc") == ["ghi"]
        assert config.getfloat("Abc", "ghi") == 3.75
