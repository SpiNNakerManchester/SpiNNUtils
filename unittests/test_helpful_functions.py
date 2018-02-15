import unittests
from spinn_utilities.helpful_functions import \
    get_valid_components, write_finished_file, set_up_report_specifics,\
    set_up_output_application_data_specifics


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


def test_set_up_report_specifics(tmpdir):
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


def test_set_up_output_application_data_specifics(tmpdir):
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


def test_get_valid_components():
    # WTF is this function doing?!
    d = get_valid_components(unittests.test_helpful_functions, "_c")
    assert len(d) == 3
    assert d['a'] == a_c
    assert d['a_b'] == a_b
    assert d['b'] == b_c


# Support class for test_get_valid_components
class a_b(object):
    pass


# Support class for test_get_valid_components
class b_c(object):
    pass


# Support class for test_get_valid_components
class a_c(object):
    pass
