# Copyright (c) 20172018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=redefined-outer-name, unused-argument
import os
import pytest
import random
import configparser
import unittests  # CRITICAL: *THIS* package!
from testfixtures import LogCapture
import spinn_utilities.conf_loader as conf_loader
from spinn_utilities.configs import (
    ConfigTemplateException, NoConfigFoundException, UnexpectedConfigException)
from spinn_utilities.testing import log_checker

CFGFILE = "configloader.cfg"
CFGPATH = os.path.join(os.path.dirname(unittests.__file__), CFGFILE)
ONEFILE = "config_one.cfg"
ONEPATH = os.path.join(os.path.dirname(unittests.__file__), ONEFILE)
TWOFILE = "config_two.cfg"
TWOPATH = os.path.join(os.path.dirname(unittests.__file__), TWOFILE)
THREEFILE = "config_three.cfg"
THREEPATH = os.path.join(os.path.dirname(unittests.__file__), THREEFILE)
FOURFILE = "config_four.cfg"
FOURPATH = os.path.join(os.path.dirname(unittests.__file__), FOURFILE)
VALIDATION_PATH = os.path.join(os.path.dirname(unittests.__file__),
                               "validation_config.cfg")


@pytest.fixture
def not_there():
    name = "test_config_for_spinnutils_unittests.{}.txt".format(
        random.randint(1, 1000000))
    place = os.path.join(os.path.expanduser("~"), f".{name}")
    if os.path.exists(place):
        # Check existing is a config from previsous test run
        config = configparser.ConfigParser()
        config.read(place)
        # Remove it
        os.remove(place)
    yield (name, place)
    os.remove(place)


@pytest.fixture
def default_config():
    with open(CFGPATH) as the_file:
        return the_file.read()


@pytest.fixture
def mach_spec(tmpdir):
    msf = tmpdir.join("machspec.cfg")
    msf.write("[Machine]\nmachineName=foo\nversion=5\n")
    return str(msf)


def test_different_value(tmpdir, default_config):
    name, place = not_there
    default_config = default_config.replace("bar", "cat")
    place.write(default_config)
    config = conf_loader.load_config(name, [CFGPATH])
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
            conf_loader.load_config(CFGFILE, [CFGPATH])


def test_dead_section(tmpdir, default_config):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        default_config = default_config + "[Pets]\nsam=cat\n"
        f.write(default_config)
        with pytest.raises(UnexpectedConfigException):
            conf_loader.load_config(CFGFILE, [CFGPATH])


def test_use_one_default(tmpdir, not_there):
    name, place = not_there
    with tmpdir.as_cwd():
        with pytest.raises(NoConfigFoundException):
            conf_loader.load_config(name, [CFGPATH])
        # Load the now created file
        config = configparser.ConfigParser()
        config.read(place)
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foobob"]
        assert config.get("sect", "foobob") == "bar"


def test_no_templates(tmpdir, default_config, not_there):  # @UnusedVariable
    name, place = not_there
    with tmpdir.as_cwd():
        with pytest.raises(ConfigTemplateException):
            conf_loader.load_config(name, [THREEPATH, FOURPATH])


def test_one_templates(tmpdir, default_config, not_there):  # @UnusedVariable
    name, place = not_there
    with tmpdir.as_cwd():
        with pytest.raises(NoConfigFoundException):
            conf_loader.load_config(name, [FOURPATH, ONEPATH, THREEPATH])


def test_two_templates(tmpdir, default_config, not_there):  # @UnusedVariable
    name, place = not_there
    with tmpdir.as_cwd():
        with pytest.raises(ConfigTemplateException):
            conf_loader.load_config(name, [ONEPATH, TWOPATH])


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


def test_str_list(tmpdir):
    with tmpdir.as_cwd():
        f = tmpdir.join(CFGFILE)
        f.write("[abc]\n"
                "as_list=bacon, is,so ,cool \n"
                "as_none=None\n"
                "as_empty=\n"
                "fluff=more\n")
        config = conf_loader.load_config(CFGFILE, [])
        assert config.get_str_list("abc", "as_list") == \
               ["bacon", "is", "so", "cool"]
        assert config.get_str_list("abc", "as_none") == []
        assert config.get_str_list("abc", "as_empty") == []
        assert config.get_str_list("abc", "fluff") == ["more"]
