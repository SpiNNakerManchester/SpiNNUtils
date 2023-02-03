# Copyright (c) 2017-2022 The University of Manchester
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

import logging
import os
import pytest
import random
import configparser
import unittests  # CRITICAL: *THIS* package!
from testfixtures import LogCapture
import spinn_utilities.conf_loader as conf_loader
import spinn_utilities.config_holder as config_holder
from spinn_utilities.configs import (
    ConfigTemplateException, NoConfigFoundException, UnexpectedConfigException)
from spinn_utilities.log import FormatAdapter
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
TYPESFILE = "config_types.cfg"
TYPESPATH = os.path.join(os.path.dirname(unittests.__file__), TYPESFILE)
VALIDATION_PATH = os.path.join(os.path.dirname(unittests.__file__),
                               "validation_config.cfg")

logger = FormatAdapter(logging.getLogger(__name__))


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


def test_different_value(not_there, default_config):
    name, place = not_there
    default_config = default_config.replace("bar", "cat")
    with open(place, "w") as f:
        f.write(default_config)
    config = conf_loader.load_config(name, [CFGPATH])
    assert config is not None
    assert config.sections() == ["sect"]
    assert config.options("sect") == ["foobob"]
    assert config.get("sect", "foobob") == "cat"


def test_new_option_local(tmpdir, default_config, not_there):
    name, place = not_there
    with open(place, "w") as f:
        f.write(default_config)
    with tmpdir.as_cwd():
        f = tmpdir.join(name)
        default_config = default_config + "sam=cat\n"
        f.write(default_config)
        with pytest.raises(UnexpectedConfigException):
            conf_loader.load_config(name, [CFGPATH])


def test_new_option_home(not_there, default_config):
    name, place = not_there
    default_config = default_config + "sam=cat\n"
    with open(place, "w") as f:
        f.write(default_config)
    with LogCapture() as lc:
        conf_loader.load_config(name, [CFGPATH])
        log_checker.assert_logs_warning_contains(
            lc.records, "Unexpected Option: [sect]sam")


def test_dead_section(not_there, default_config):
    name, place = not_there
    default_config = default_config + "[Pets]\nsam=cat\n"
    with open(place, "w") as f:
        f.write(default_config)
    with LogCapture() as lc:
        conf_loader.load_config(name, [CFGPATH])
        log_checker.assert_logs_warning_contains(
            lc.records, "Unexpected Section: [Pets]")


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


def test_None_machine_spec_file(tmpdir, default_config, not_there):
    name, place = not_there
    default_config += "\n[Machine]\nmachine_spec_file=None\n"
    with open(place, "w") as f:
        f.write(default_config)
    with tmpdir.as_cwd():
        with LogCapture() as lc:
            config = conf_loader.load_config(name, [])
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foobob"]
            assert config.get("sect", "foobob") == "bar"
            log_checker.assert_logs_info_not_contains(lc.records, "None")


def test_intermediate_use(tmpdir, default_config, mach_spec, not_there):
    name, place = not_there
    default_config += "\n[Machine]\nmachine_spec_file=" + mach_spec + "\n"
    with open(place, "w") as f:
        f.write(default_config)
    with tmpdir.as_cwd():
        with LogCapture() as lc:
            config = conf_loader.load_config(name, [])
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foobob"]
            assert config.get("sect", "foobob") == "bar"
            assert config.options("Machine") == ["machinename", "version"]
            assert config.get("Machine", "MachineName") == "foo"
            assert config.getint("Machine", "VeRsIoN") == 5
            log_checker.assert_logs_info_contains(lc.records, name)


def test_advanced_use(tmpdir, default_config, not_there):
    def parseAbc(parser):
        f = parser.getfloat("Abc", "def")
        parser.set("Abc", "ghi", f*3)
        parser.remove_option("Abc", "def")

    name, place = not_there
    default_config += "\n[Abc]\ndef=1.25\n"
    with open(place, "w") as f:
        f.write(default_config)
    with tmpdir.as_cwd():
        config = conf_loader.load_config(
            name, [], config_parsers=[("Abc", parseAbc)])
        assert config.options("Abc") == ["ghi"]
        assert config.getfloat("Abc", "ghi") == 3.75


def test_str_list(tmpdir, not_there):
    name, place = not_there
    with open(place, "w") as f:
        f.write("[abc]\n"
                "as_list=bacon, is,so ,cool \n"
                "as_none=None\n"
                "as_empty=\n"
                "fluff=more\n")
    with tmpdir.as_cwd():
        config = conf_loader.load_config(name, [])
        assert config.get_str_list("abc", "as_list") == \
               ["bacon", "is", "so", "cool"]
        assert config.get_str_list("abc", "as_none") == []
        assert config.get_str_list("abc", "as_empty") == []
        assert config.get_str_list("abc", "fluff") == ["more"]


def test_logging(tmpdir, not_there):
    # tests the ConfiguredFilter
    name, place = not_there
    with open(place, "w") as f:
        f.write("[Logging]\n"
                "instantiate = True\n"
                "default = info\n"
                "debug =\n"
                "info =\n"
                "warning =\n"
                "error =\n"
                "critical =\n")
    with tmpdir.as_cwd():
        conf_loader.load_config(name, [])

    logger = FormatAdapter(logging.getLogger(__name__))
    logger.warning("trigger filter")


def test_errors(not_there):
    name, place = not_there
    with pytest.raises(ConfigTemplateException):
        conf_loader.install_cfg_and_IOError(
            filename=name, defaults=[], config_locations=[])


def test_config_holder(not_there):
    config_holder.clear_cfg_files(False)
    name, place = not_there
    config_holder.set_cfg_files(name, TYPESPATH)
    # first time creates file and errors
    try:
        config_holder.load_config()
        raise NotImplementedError("Why am I here")
    except NoConfigFoundException as ex:
        assert name in str(ex)
    # Should work the second time
    config_holder.load_config()
    # Note these values come from the template file not the default!
    assert "from template" == config_holder.get_config_str("sect", "a_string")
    assert ["alpha", "beta", "gamma"] == config_holder.get_config_str_list(
        "sect", "string_list")
    assert 123 == config_holder.get_config_int("sect", "a_int")
    assert 44.56 == config_holder.get_config_float("sect", "a_float")
    assert config_holder.get_config_bool("sect", "a_bool")


def test_no_default():
    config_holder.clear_cfg_files(False)
    try:
        config_holder.load_config()
        raise NotImplementedError("Why am I here")
    except Exception as ex:
        assert "No default configs set" in str(ex)


def test_preload_not_unittest():
    config_holder.clear_cfg_files(False)
    config_holder.set_cfg_files(None, TYPESPATH)
    try:
        assert "from default" == config_holder.get_config_str(
            "sect", "a_string")
        raise NotImplementedError("Why am I here")
    except Exception as ex:
        assert ("Accessing config values before setup is not supported"
                in str(ex))


def test_preload_str():
    config_holder.clear_cfg_files(True)
    config_holder.set_cfg_files(None, TYPESPATH)
    assert "from default" == config_holder.get_config_str("sect", "a_string")


def test_preload_str_list():
    config_holder.clear_cfg_files(True)
    config_holder.set_cfg_files(None, TYPESPATH)
    assert ["foo", "bar"] == config_holder.get_config_str_list(
        "sect", "string_list")


def test_preload_int():
    config_holder.clear_cfg_files(True)
    config_holder.set_cfg_files(None, TYPESPATH)
    assert 321 == config_holder.get_config_int("sect", "a_int")


def test_preload_float():
    config_holder.clear_cfg_files(True)
    config_holder.set_cfg_files(None, TYPESPATH)
    assert 56.44 == config_holder.get_config_float("sect", "a_float")


def test_preload_bool():
    config_holder.clear_cfg_files(True)
    config_holder.set_cfg_files(None, TYPESPATH)
    assert not config_holder.get_config_bool("sect", "a_bool")
