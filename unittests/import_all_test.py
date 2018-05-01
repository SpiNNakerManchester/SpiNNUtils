import os
import spinn_utilities.package_loader as package_loader


def test_import_all():
    if os.environ.get('CONTINUOUS_INTEGRATION', 'false').lower() == 'true':
        package_loader.load_module("spinn_utilities", remove_pyc_files=False)
    else:
        package_loader.load_module("spinn_utilities", remove_pyc_files=True)


if __name__ == '__main__':
    test_import_all()
