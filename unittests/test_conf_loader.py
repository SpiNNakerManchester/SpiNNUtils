import unittests  # CRITICAL: *THIS* package!
from spinn_utilities.conf_loader import ConfigurationLoader

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


def test_create():
    ConfigurationLoader(unittests, CFGFILE)


def test_basic_use(tmpdir, default_config):
    with tmpdir.as_cwd():
        cl = ConfigurationLoader(unittests, CFGFILE)
        f = tmpdir.join(CFGFILE)
        f.write(default_config)
        config = cl.load_config()
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foo"]
        assert config.get("sect", "foo") == "bar"


def test_intermediate_use(tmpdir, default_config, mach_spec):
    with tmpdir.as_cwd():
        cl = ConfigurationLoader(unittests, CFGFILE)
        f = tmpdir.join(CFGFILE)
        f.write(default_config + "\n[Machine]\nmachine_spec_file=" +
                mach_spec + "\n")
        config = cl.load_config()
        assert config is not None
        assert config.sections() == ["sect", "Machine"]
        assert config.options("sect") == ["foo"]
        assert config.get("sect", "foo") == "bar"
        assert config.options("Machine") == ["machine_spec_file",
                                             "machinename", "version"]
        assert config.get("Machine", "MachineName") == "foo"
        assert config.getint("Machine", "VeRsIoN") == 5


def test_advanced_use(tmpdir, default_config):
    def parseAbc(parser):
        f = parser.getfloat("Abc", "def")
        parser.set("Abc", "ghi", f*3)
        parser.remove_option("Abc", "def")

    with tmpdir.as_cwd():
        cl = ConfigurationLoader(unittests, CFGFILE)
        f = tmpdir.join(CFGFILE)
        f.write(default_config + "\n[Abc]\ndef=1.25\n")
        config = cl.load_config([("Abc", parseAbc)])
        assert config.options("Abc") == ["ghi"]
        assert config.getfloat("Abc", "ghi") == 3.75
