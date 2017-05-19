import unittests  # CRITICAL: *THIS* package!
from testfixtures import LogCapture
import spinn_utilities.conf_loader as conf_loader
import spinn_utilities.testing.log_checker as log_checker


import pytest
import os

CFGFILE = "configloader.cfg"


@pytest.fixture
def default_config():
    with open(os.path.join(os.path.dirname(unittests.__file__),
                           CFGFILE)) as the_file:
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
        config = conf_loader.load_config(unittests, CFGFILE)
        print config
        print type(config)
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foo"]
        assert config.get("sect", "foo") == "bar"


def test_None_machine_spec_file(tmpdir, default_config):
    with tmpdir.as_cwd():
        with LogCapture() as l:
            f = tmpdir.join(CFGFILE)
            f.write(default_config + "\n[Machine]\nmachine_spec_file=None\n")
            config = conf_loader.load_config(unittests, CFGFILE)
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foo"]
            assert config.get("sect", "foo") == "bar"
            log_checker.assert_logs_info_not_contains(l.records, "None")


def test_intermediate_use(tmpdir, default_config, mach_spec):
    with tmpdir.as_cwd():
        with LogCapture() as l:
            f = tmpdir.join(CFGFILE)
            f.write(default_config + "\n[Machine]\nmachine_spec_file=" +
                    mach_spec + "\n")
            config = conf_loader.load_config(unittests, CFGFILE)
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foo"]
            assert config.get("sect", "foo") == "bar"
            assert config.options("Machine") == ["machine_spec_file",
                                                 "machinename", "version"]
            assert config.get("Machine", "MachineName") == "foo"
            assert config.getint("Machine", "VeRsIoN") == 5
            log_checker.assert_logs_info_contains(l.records, CFGFILE)


def test_advanced_use(tmpdir, default_config):
    def parseAbc(parser):
        f = parser.getfloat("Abc", "def")
        parser.set("Abc", "ghi", f*3)
        parser.remove_option("Abc", "def")

    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        f.write(default_config + "\n[Abc]\ndef=1.25\n")
        config = conf_loader.load_config(unittests, CFGFILE,
                                         [("Abc", parseAbc)])
        assert config.options("Abc") == ["ghi"]
        assert config.getfloat("Abc", "ghi") == 3.75

