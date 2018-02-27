import pytest
import unittests
from spinn_utilities.helpful_functions import \
    get_valid_components, write_finished_file, set_up_report_specifics,\
    set_up_output_application_data_specifics
import os


def test_write_finished_file(tmpdir):
    sub1 = tmpdir.mkdir("a")
    f1 = sub1.join("finished")
    sub2 = tmpdir.mkdir("b")
    f2 = sub2.join("finished")
    assert not f1.check()
    assert not f2.check()
    write_finished_file(str(sub1), str(sub2))
    assert f1.check()
    assert f2.check()


def test_set_up_report_specifics_default(tmpdir):
    with tmpdir.as_cwd():
        base = tmpdir.join("reports")
        assert not base.check()

        a, b, c = set_up_report_specifics("DEFAULT", 2, 3, 4, "NOW")

        # Check expected results
        assert a == base.join("NOW/run_4")
        assert b == base.join("NOW")
        assert c == "NOW"

        # Check expected FS state
        assert base.check(dir=1)
        assert base.join("NOW").check(dir=1)
        assert base.join("NOW/run_4").check(dir=1)
        assert base.join("NOW/time_stamp").check(file=1)
        assert base.join("NOW/time_stamp").read() == "app_3_NOW"


def test_set_up_report_specifics_reports(tmpdir):
    with tmpdir.as_cwd():
        base = tmpdir.join("reports")
        assert not base.check()

        a, b, c = set_up_report_specifics("REPORTS", 2, 3, 4, "NOW")

        # Check expected results
        assert a == os.path.join("reports", "NOW", "run_4")
        assert b == os.path.join("reports", "NOW")
        assert c == "NOW"

        # Check expected FS state
        assert base.check(dir=1)
        assert base.join("NOW").check(dir=1)
        assert base.join(os.path.join("NOW", "run_4")).check(dir=1)
        assert base.join(os.path.join("NOW", "time_stamp")).check(file=1)
        assert base.join(os.path.join("NOW", "time_stamp")).read()\
            == "app_3_NOW"


def test_set_up_report_specifics_explicit(tmpdir):
    base = tmpdir.join("reports")
    assert not base.check()

    a, b, c = set_up_report_specifics(str(tmpdir), 2, 3, 4, "NOW")

    # Check expected results
    assert a == base.join("NOW/run_4")
    assert b == base.join("NOW")
    assert c == "NOW"

    # Check expected FS state
    assert base.check(dir=1)
    assert base.join("NOW").check(dir=1)
    assert base.join("NOW/run_4").check(dir=1)
    assert base.join("NOW/time_stamp").check(file=1)
    assert base.join("NOW/time_stamp").read() == "app_3_NOW"


def test_set_up_report_specifics_repeated(tmpdir):
    # Checks the auto-cleaning of finished outputs
    _, d, ts1 = set_up_report_specifics(str(tmpdir), 2, 3, 1, "NOW_1")
    write_finished_file(d, None)
    _, d, ts2 = set_up_report_specifics(str(tmpdir), 2, 3, 2, "NOW_2")
    _, d, ts3 = set_up_report_specifics(str(tmpdir), 2, 3, 3, "NOW_3")
    write_finished_file(d, None)
    _, d, ts4 = set_up_report_specifics(str(tmpdir), 2, 3, 4, "NOW_4")

    base = tmpdir.join("reports")
    # Check expected FS state
    assert not base.join(ts1).check(dir=1)
    assert base.join(ts2).check(dir=1)
    assert base.join(ts3).check(dir=1)
    assert base.join(ts4).check(dir=1)


def test_set_up_output_application_data_specifics_default(tmpdir):
    with tmpdir.as_cwd():
        base = tmpdir.join("application_generated_data_files")
        assert not base.check()

        a, b = set_up_output_application_data_specifics(
            "DEFAULT", 2, 3, 4, "NOW")

        # Check expected results
        assert a == base.join("NOW/run_4")
        assert b == base.join("NOW")

        # Check expected FS state
        assert base.check(dir=1)
        assert base.join("NOW").check(dir=1)
        assert base.join("NOW/run_4").check(dir=1)
        assert base.join("NOW/time_stamp").check(file=1)
        assert base.join("NOW/time_stamp").read() == "app_3_NOW"


@pytest.mark.skip(reason="horrible logic bug when TEMP used")
def test_set_up_output_application_data_specifics_temp(tmpdir):
    with tmpdir.as_cwd():
        a, b = set_up_output_application_data_specifics(
            "TEMP", 2, 3, 4, "NOW")

        # Check expected results
        assert a == tmpdir.join("NOW/run_4")
        assert b == tmpdir.join("NOW")

        # Check expected FS state
        assert tmpdir.check(dir=1)
        assert tmpdir.join("NOW").check(dir=1)
        assert tmpdir.join("NOW/run_4").check(dir=1)
        assert tmpdir.join("NOW/time_stamp").check(file=1)
        assert tmpdir.join("NOW/time_stamp").read() == "app_3_NOW"


def test_set_up_output_application_data_specifics_explicit(tmpdir):
    a, b = set_up_output_application_data_specifics(
        str(tmpdir), 2, 3, 4, "NOW")

    # Check expected results
    assert a == tmpdir.join("NOW/run_4")
    assert b == tmpdir.join("NOW")

    # Check expected FS state
    assert tmpdir.check(dir=1)
    assert tmpdir.join("NOW").check(dir=1)
    assert tmpdir.join("NOW/run_4").check(dir=1)
    assert tmpdir.join("NOW/time_stamp").check(file=1)
    assert tmpdir.join("NOW/time_stamp").read() == "app_3_NOW"


def test_get_valid_components():
    # WTF is this function doing?!
    d = get_valid_components(unittests.test_helpful_functions, "_c")
    assert len(d) == 3
    assert d['a'] == a_c
    assert d['a_b'] == a_b
    assert d['b'] == b_c


# Support class for test_get_valid_components
class a_b(object):  # noqa: N801
    pass


# Support class for test_get_valid_components
class b_c(object):  # noqa: N801
    pass


# Support class for test_get_valid_components
class a_c(object):  # noqa: N801
    pass
