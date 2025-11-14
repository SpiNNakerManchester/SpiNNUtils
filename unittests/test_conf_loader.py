# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import pytest
import random
import configparser
from types import ModuleType
from typing import Iterator

import unittests  # CRITICAL: *THIS* package!
from testfixtures import LogCapture

import spinn_utilities.conf_loader as conf_loader
import spinn_utilities.config_holder as config_holder
from spinn_utilities.configs import (
    NoConfigFoundException, UnexpectedConfigException)
from spinn_utilities.exceptions import ConfigException
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

logger = FormatAdapter(logging.getLogger(__name__))


def _random_name() -> str:
    return "test_config_for_spinnutils_unittests.{}.txt".format(
        random.randint(1, 1000000))


@pytest.fixture
def not_there() -> Iterator[str]:
    name = "test_config_for_spinnutils_unittests.{}.txt".format(
        random.randint(1, 1000000))
    place = os.path.join(os.path.expanduser("~"), f".{name}")
    if os.path.exists(place):
        # Check existing is a config from previsous test run
        config = configparser.ConfigParser()
        config.read(place)
        # Remove it
        os.remove(place)
    yield place
    os.remove(place)


@pytest.fixture
def default_config() -> str:
    with open(CFGPATH) as the_file:
        return the_file.read()


@pytest.fixture
def mach_spec(tmpdir: ModuleType) -> str:
    msf = tmpdir.join("machspec.cfg")
    msf.write("[Machine]\nmachineName=foo\nversion=5\n")
    return str(msf)


def test_user_cfg(
        not_there: str, default_config: str) -> None:
    default_config = default_config.replace("bar", "cat")
    with open(not_there, "w") as f:
        f.write(default_config)
    name = os.path.basename(not_there)[1:]
    config_holder.clear_cfg_files(unittest_mode=False)
    config_holder.add_default_cfg(CFGPATH)
    # not relevant for this test but needed
    config_holder.add_template(TWOPATH)
    config_holder.load_config(name)
    assert config_holder.config_sections() == ["sect"]
    assert config_holder.config_options("sect") == ["foobob"]
    assert config_holder.get_config_str("sect", "foobob") == "cat"


def test_current_dir_cfg(
        tmpdir: ModuleType, default_config: str) -> None:
    default_config = default_config.replace("bar", "cat")
    name = _random_name()
    with tmpdir.as_cwd():
        f = tmpdir.join(name)
        f.write(default_config)
        config_holder.clear_cfg_files(unittest_mode=False)
        config_holder.add_default_cfg(CFGPATH)
        # not relevant for this test but needed
        config_holder.add_template(TWOPATH)
        config_holder.load_config(name)
    assert config_holder.config_sections() == ["sect"]
    assert config_holder.config_options("sect") == ["foobob"]
    assert config_holder.get_config_str("sect", "foobob") == "cat"


def test_new_option_local(tmpdir: ModuleType, default_config: str) -> None:
    name = _random_name()
    with tmpdir.as_cwd():
        f = tmpdir.join(name)
        default_config = default_config + "sam=cat\n"
        f.write(default_config)
        with pytest.raises(UnexpectedConfigException):
            conf_loader.load_config(
                local_name=name, user_cfg=None, defaults=[CFGPATH])


def test_new_option_home(
        not_there: str, default_config: str) -> None:
    place = not_there
    default_config = default_config + "sam=cat\n"
    with open(place, "w") as f:
        f.write(default_config)
    with LogCapture() as lc:
        conf_loader.load_config(
            local_name=None, user_cfg=place, defaults=[CFGPATH])
        log_checker.assert_logs_warning_contains(
            lc.records, "Unexpected Option: [sect]sam")


def test_dead_section(not_there: str, default_config: str) -> None:
    place = not_there
    default_config = default_config + "[Pets]\nsam=cat\n"
    with open(place, "w") as f:
        f.write(default_config)
    with LogCapture() as lc:
        conf_loader.load_config(
            local_name=None, user_cfg=place, defaults=[CFGPATH])
        log_checker.assert_logs_warning_contains(
            lc.records, "Unexpected Section: [Pets]")


@pytest.mark.xdist_group(name="config_holder")
def test_create_user(not_there: str, tmpdir: ModuleType) -> None:
    config_holder.clear_cfg_files(unittest_mode=False)
    place = not_there
    config_holder.add_template(template=CFGPATH)
    # Based name less the start .
    name = os.path.basename(place)[1:]
    config_holder.add_default_cfg(CFGPATH)
    with tmpdir.as_cwd():
        config_holder.load_config(name)
        with pytest.raises(NoConfigFoundException):
            config_holder.check_user_cfg()
        # Load the now created file
        config = configparser.ConfigParser()
        config.read(place)
        assert config is not None
        assert config.sections() == ["sect"]
        assert config.options("sect") == ["foobob"]
        assert config.get("sect", "foobob") == "bar"


@pytest.mark.xdist_group(name="config_holder")
def test_no_templates(tmpdir: ModuleType, default_config: str) -> None:
    config_holder.clear_cfg_files(unittest_mode=False)
    name = _random_name()
    config_holder.add_default_cfg(CFGPATH)
    with pytest.raises(ConfigException):
        config_holder.load_config(name)


@pytest.mark.xdist_group(name="config_holder")
def test_two_templates() -> None:
    config_holder.clear_cfg_files(unittest_mode=False)
    config_holder.add_template(template=ONEPATH + ".template")
    with pytest.raises(ConfigException):
        config_holder.add_template(template=TWOFILE + ".template")


def test_None_machine_spec_file(tmpdir: ModuleType, default_config: str,
                                not_there: str) -> None:
    place = not_there
    default_config += "\n[Machine]\nmachine_spec_file=None\n"
    with open(place, "w") as f:
        f.write(default_config)
    with tmpdir.as_cwd():
        with LogCapture() as lc:
            config = conf_loader.load_config(
                local_name=None, user_cfg=place, defaults=[])
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foobob"]
            assert config.get("sect", "foobob") == "bar"
            log_checker.assert_logs_info_not_contains(lc.records, "None")


def test_intermediate_use(tmpdir: ModuleType, default_config: str,
                          mach_spec: str, not_there: str) -> None:
    place = not_there
    default_config += "\n[Machine]\nmachine_spec_file=" + mach_spec + "\n"
    with open(place, "w") as f:
        f.write(default_config)
    with tmpdir.as_cwd():
        with LogCapture() as lc:
            config = conf_loader.load_config(
                local_name=None, user_cfg=place, defaults=[])
            assert config is not None
            assert config.sections() == ["sect", "Machine"]
            assert config.options("sect") == ["foobob"]
            assert config.get("sect", "foobob") == "bar"
            assert config.options("Machine") == ["machinename", "version"]
            assert config.get("Machine", "MachineName") == "foo"
            assert config.getint("Machine", "VeRsIoN") == 5
            log_checker.assert_logs_info_contains(lc.records, place)


def test_str_list(tmpdir: ModuleType, not_there: str) -> None:
    place = not_there
    with open(place, "w") as f:
        f.write("[abc]\n"
                "as_list=bacon, is,so ,cool \n"
                "as_none=None\n"
                "as_empty=\n"
                "fluff=more\n")
    with tmpdir.as_cwd():
        config = conf_loader.load_config(
            local_name=None, user_cfg=place, defaults=[])
        assert config.get_str_list("abc", "as_list") == \
               ["bacon", "is", "so", "cool"]
        assert config.get_str_list("abc", "as_none") == []
        assert config.get_str_list("abc", "as_empty") == []
        assert config.get_str_list("abc", "fluff") == ["more"]


def test_logging(tmpdir: ModuleType, not_there: str) -> None:
    # tests the ConfiguredFilter
    place = not_there
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
        conf_loader.load_config(local_name=None, user_cfg=place, defaults=[])

    logger = FormatAdapter(logging.getLogger(__name__))
    logger.warning("trigger filter")


@pytest.mark.xdist_group(name="config_holder")
def test_no_default() -> None:
    config_holder.clear_cfg_files(False)
    try:
        config_holder.load_config("irrelevant.cfg")
        raise NotImplementedError("Why am I here")
    except Exception as ex:
        assert "No default configs set" in str(ex)


@pytest.mark.xdist_group(name="config_holder")
def test_preload_not_unittest() -> None:
    config_holder.clear_cfg_files(False)
    config_holder.add_default_cfg(TYPESPATH)
    try:
        assert "from default" == config_holder.get_config_str(
            "sect", "a_string")
        raise NotImplementedError("Why am I here")
    except Exception as ex:
        assert ("Accessing config values before setup is not supported"
                in str(ex))


@pytest.mark.xdist_group(name="config_holder")
def test_preload_str() -> None:
    config_holder.clear_cfg_files(True)
    config_holder.add_default_cfg(TYPESPATH)
    assert "from default" == config_holder.get_config_str("sect", "a_string")


@pytest.mark.xdist_group(name="config_holder")
def test_preload_str_list() -> None:
    config_holder.clear_cfg_files(True)
    config_holder.add_default_cfg(TYPESPATH)
    assert ["foo", "bar"] == config_holder.get_config_str_list(
        "sect", "string_list")


@pytest.mark.xdist_group(name="config_holder")
def test_preload_int() -> None:
    config_holder.clear_cfg_files(True)
    config_holder.add_default_cfg(TYPESPATH)
    assert 321 == config_holder.get_config_int("sect", "a_int")


@pytest.mark.xdist_group(name="config_holder")
def test_preload_float() -> None:
    config_holder.clear_cfg_files(True)
    config_holder.add_default_cfg(TYPESPATH)
    assert 56.44 == config_holder.get_config_float("sect", "a_float")


@pytest.mark.xdist_group(name="config_holder")
def test_preload_bool() -> None:
    config_holder.clear_cfg_files(True)
    config_holder.add_default_cfg(TYPESPATH)
    assert not config_holder.get_config_bool("sect", "a_bool")


def test_local_name() -> None:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(this_dir)
    config = conf_loader.load_config(
        local_name=ONEFILE, user_cfg=None, defaults=[])
    assert config.get_str("sect", "foo") == "notbar"
