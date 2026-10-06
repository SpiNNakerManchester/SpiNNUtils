import ast
import os


class FileChecker:

    def __init__(self, file_path, ast_tree, parent):
        self.__filepath = file_path
        self.__ast_tree = ast_tree
        self.__parent = parent
        self.__errors = 0

    def print_file_name(self):
        if self.__errors == 0:
            print(self.__filepath)
        self.__errors += 1

    def error_count(self) -> int:
        if self.__errors > 0:
            print()
        return self.__errors

    def check_dir_import(self):
        for node in ast.walk(self.__ast_tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module.replace(".", os.sep)
                dir = os.path.join(self.__parent, module)
                init = os.path.join(dir, "__init__.py")
                if os.path.isfile(init):
                    ok = False
                    for name in node.names:
                        py_file = os.path.join(dir, name.name + ".py")
                        if os.path.exists(py_file):
                            ok = True
                    if ok:
                        continue
                    self.print_file_name()
                    print("\t", node)

    def check_init(self):
        for node in ast.walk(self.__ast_tree):
            if isinstance(node, ast.ImportFrom):
                if "." in node.module:
                    if "._version" in node.module:
                        continue
                    self.print_file_name()
                    print("\t", node)


class DirChecker:

    def __init__(self, dir_path):
        self.__dir_path = dir_path
        self.__parent = os.path.dirname(dir_path)
        self.__error = 0

    def check_file(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_tree = file.read()
        try:
            ast_tree = ast.parse(raw_tree, type_comments=True)
        except SyntaxError as ex:
            raise SyntaxError(f"{ex.msg} of {file_path}") from ex
        file_checker = FileChecker(file_path, ast_tree, self.__parent)
        if file_path.endswith("__init__.py"):
            file_checker.check_init()
        else:
            file_checker.check_dir_import()
        self.__error += file_checker.error_count()

    def check_dir(self):
        for root, dir_names, files in os.walk(self.__dir_path):
            for file_name in files:
                if file_name.endswith(".py"):
                    self.check_file(os.path.join(root, file_name))
        return self.__error


if __name__ == "__main__":
    dir_checker = DirChecker("/home/brenninc/spinnaker/SpiNNMan/spinnman")
    errors = dir_checker.check_dir()
    if errors:
        raise AssertionError(errors)
