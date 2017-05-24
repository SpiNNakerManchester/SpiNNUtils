from abstract_no_base_marker import AbstractNoBaseMarker
from abstract_has_label import AbstractHasLabel


class MixedParent(AbstractNoBaseMarker, AbstractHasLabel):
    pass

    def label(self):
        return "foo"

    def set_label(selfself, label):
        pass