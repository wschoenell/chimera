from chimera.core.serializer_pickle import PickleSerializer

from chimera.core.tests.test_enum import ExampleNewEnum


def check_serializer(data):
    serializer = PickleSerializer()
    out = serializer.dumps(data)
    inp = serializer.loads(out)
    assert data == inp


def test_new_enum():
    check_serializer(ExampleNewEnum.Foo)
