import ast
import os


class ImportChecker:
    """
    Checks a directory for imports that may lead to import for partial

    Any imports from init files in the same repository is dangerous.
    These require the init to be imported before some of the code files.
    Which in turn increases the risk of import from partial errors.

    Imports inside If TYPE_CHECKER can import from init
    as circular imports are allowed here.

    Importing from init files in test and scripts is fine.
    """

    def __init__(self, dir_path: str, ) -> None:
        """
       :param dir_path: Path to the top level directory
       """
        self.__dir_path = dir_path
        self.__parent, self.__repo = os.path.split(dir_path)
        self.__file_errors = 0
        self.__all_errors = 0
        # temp values until set on check_file
        self.__filepath = "TOBESET"
        self.__file_errors = 0
        self.__ast_tree = ast.AST()

    def _check_file(self) -> None:
        self.__file_errors = 0
        with open(self.__filepath, "r", encoding="utf-8") as file:
            raw_tree = file.read()
        try:
            self.__ast_tree = ast.parse(raw_tree, type_comments=True)
        except SyntaxError as ex:
            raise SyntaxError(f"{ex.msg} of {self.__filepath}") from ex
        self._check_dir_import()
        if self.__file_errors > 0:
            print()

    def _print_file_name(self) -> None:
        if self.__all_errors == 0:
            print("Import checker found errors")
        if self.__file_errors == 0:
            print(self.__filepath)
        self.__all_errors += 1
        self.__file_errors += 1

    def _check_dir_import(self) -> None:
        # Note the parent of each node
        parents = {}
        for node in ast.walk(self.__ast_tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(self.__ast_tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module
                assert module is not None
                module = module.replace(".", os.sep)
                dir = os.path.join(self.__parent, module)
                init = os.path.join(dir, "__init__.py")
                if os.path.isfile(init):
                    ok = False
                    for name in node.names:
                        py_file = os.path.join(dir, name.name + ".py")
                        if os.path.exists(py_file):
                            ok = True
                    if isinstance(parents[node], ast.If):
                        if "TYPE_CHECKING" in str(parents[node]):
                            ok = True
                    if ok:
                        continue
                    self._print_file_name()
                    print("\t", repr(node))

    def check_dir(self) -> int:
        """
        Checks the directory

        :return: Number of errors found
        """
        for root, dir_names, files in os.walk(self.__dir_path):
            for file_name in files:
                if file_name.endswith(".py"):
                    self.__filepath = os.path.join(root, file_name)
                    self._check_file()
        return self.__all_errors


if __name__ == "__main__":
    dir_checker = ImportChecker(
        "/home/brenninc/spinnaker/PACMAN/pacman")
    errors = dir_checker.check_dir()
    if errors:
        raise AssertionError(errors)
