import unittests  # CRITICAL: *THIS* package!
from spinn_utilities.conf_loader import ConfigurationLoader

import pytest
import os


@pytest.fixture
def default_config():
    with open(os.path.join(os.path.dirname(unittests.__file__),
                           "configloader.cfg")) as the_file:
        return the_file.read()


@pytest.fixture
def mach_spec(tmpdir):
    msf = tmpdir.join("machspec.cfg")
    msf.write("[Machine]\nmachineName=foo\nversion=5\n")
    return str(msf)


def test_create():
    ConfigurationLoader(unittests, "configloader.cfg")


def test_basic_use(tmpdir, default_config):
    with tmpdir.as_cwd():
        cl = ConfigurationLoader(unittests, "configloader.cfg")
        f = tmpdir.join("configloader.cfg")
        f.write(default_config)
        config = cl.load_config()
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foo"]
        assert config.get("sect", "foo") == "bar"


def test_advanced_use(tmpdir, default_config, mach_spec):
    with tmpdir.as_cwd():
        cl = ConfigurationLoader(unittests, "configloader.cfg")
        f = tmpdir.join("configloader.cfg")
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
