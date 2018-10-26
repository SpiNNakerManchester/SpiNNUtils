from spinn_utilities.ping import Ping


def test_spalloc():
    # Should be able to reach Spalloc...
    assert(Ping.host_is_reachable("spinnaker.cs.man.ac.uk"))


def test_google_dns():
    # *REALLY* should be able to reach Google's DNS..
    assert(Ping.host_is_reachable("8.8.8.8"))


def test_localhost():
    # Can't ping localhost? Network catastrophically bad!
    assert(Ping.host_is_reachable("localhost"))


def test_ping_down_host():
    # Definitely unpingable host
    assert(not Ping.host_is_reachable("169.254.254.254"))
