import ast

__version__ = '0.0.5'
__all__ = ('FailsChecker', )

MESSAGES = {
    'PF101': 'PF101 Potential IndexError fail.',
    'PF102': 'PF102 Potential KeyError fail. You can replace this with `dict.get(key, failback_value)`',
    'PF103': 'PF103 Potential IndexError or KeyError fail.',
}


class PluginVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def check_exception_catch(self, node, exception_types):
        # TODO fix if indexing in try:else: statement
        parent = node
        while True:
            if getattr(parent, 'pf_parent', None):
                parent = parent.pf_parent
                if isinstance(parent, ast.Try):
                    for handler in parent.handlers:
                        if handler.type:
                            try:
                                if handler.type.id in exception_types:
                                    # error handled in specific exception
                                    return True
                            except AttributeError:
                                if isinstance(handler.type, ast.Tuple):
                                    for handler_type in handler.type.elts:
                                        if handler_type.id in exception_types:
                                            # error handled as one of list of errors
                                            return True
                        else:
                            # error handled in non specific exception
                            return True
            else:
                # no error handler
                return False

    def check_safe_if(self, node):
        parent = node
        while True:
            if getattr(parent, 'pf_parent', None):
                parent = parent.pf_parent
                if isinstance(parent, ast.If):
                    indexed_obj = node.pf_parent.value.id
                    if isinstance(parent.test, ast.Call):
                        # Check safe if for dict like this `if test_dict.get(key, None):`
                        checked_obj = parent.test.func.value.id
                        func = parent.test.func.attr
                        args = parent.test.args
                        if indexed_obj == checked_obj and func == 'get':
                            if isinstance(node.pf_parent.slice.value, ast.Str):
                                # dict key set as string
                                dict_key = node.pf_parent.slice.value.s
                                checked_key = args[0].s
                                if dict_key == checked_key:
                                    return True
                            elif isinstance(node.pf_parent.slice.value, ast.Name):
                                # dict key set as variable
                                dict_key = node.pf_parent.slice.value.id
                                try:
                                    checked_key = args[0].id
                                except (IndexError, AttributeError):
                                    pass
                                else:
                                    if dict_key == checked_key:
                                        return True

                    elif isinstance(parent.test, ast.Compare):
                        # Check safe if for dict like this `if index < len(test):`
                        compare_operator = parent.test.ops[0]
                        if isinstance(compare_operator, ast.Lt):
                            try:
                                func = parent.test.comparators[0].func.id
                            except (IndexError, AttributeError):
                                pass
                            else:
                                if func == 'len':
                                    if isinstance(node.pf_parent.slice.value, ast.Num):
                                        checked_obj = parent.test.comparators[0].args[0].id
                                        if indexed_obj == checked_obj:
                                            index = node.pf_parent.slice.value.n
                                            compare_index = parent.test.left.n
                                            if index == compare_index:
                                                return True
                                    elif isinstance(node.pf_parent.slice.value, ast.Name):
                                        checked_obj = parent.test.comparators[0].args[0].id
                                        if indexed_obj == checked_obj:
                                            index = node.pf_parent.slice.value.id
                                            compare_index = parent.test.left.id
                                            if index == compare_index:
                                                return True

                        elif isinstance(compare_operator, ast.Gt):
                            try:
                                func = parent.test.left.func.id
                            except AttributeError:
                                pass
                            else:
                                if func == 'len':
                                    if isinstance(node.pf_parent.slice.value, ast.Num):
                                        checked_obj = parent.test.left.args[0].id
                                        if indexed_obj == checked_obj:
                                            index = node.pf_parent.slice.value.n
                                            compare_index = parent.test.comparators[0].n
                                            if index == compare_index:
                                                return True
                                    elif isinstance(node.pf_parent.slice.value, ast.Name):
                                        checked_obj = parent.test.args[0].id
                                        if indexed_obj == checked_obj:
                                            index = node.pf_parent.slice.value.id
                                            compare_index = parent.test.comparators[0].id
                                            if index == compare_index:
                                                return True
            else:
                return False

    def check_safe_for(self, node):
        parent = node
        while True:
            if getattr(parent, 'pf_parent', None):
                parent = parent.pf_parent
                if isinstance(parent, ast.For):
                    indexed_obj = node.pf_parent.value.id
                    try:
                        key = node.value.id
                    except AttributeError:
                        pass
                    else:
                        if isinstance(parent.iter, ast.Name):
                            iter_obj = parent.iter.id
                            iter_var = parent.target.id
                            if indexed_obj == iter_obj and key == iter_var:
                                return True
            else:
                return False

    def handle_num(self, node):
        exception_types = ['IndexError']
        error = (
            node.value.lineno,
            node.value.col_offset,
            MESSAGES.get('PF101'),
            type(self)
        )

        error_handled = self.check_exception_catch(node, exception_types)

        if not error_handled:
            error_handled = self.check_safe_if(node)

        if not error_handled:
            self.errors.append(error)

    def handle_str(self, node):
        exception_types = ['KeyError']
        error = (
            node.value.lineno,
            node.value.col_offset,
            MESSAGES.get('PF102'),
            type(self)
        )

        error_handled = self.check_exception_catch(node, exception_types)

        if not error_handled:
            error_handled = self.check_safe_if(node)

        if not error_handled:
            self.errors.append(error)

    def handle_name(self, node):
        exception_types = ['IndexError', 'KeyError']
        error = (
            node.value.lineno,
            node.value.col_offset,
            MESSAGES.get('PF103'),
            type(self)
        )

        error_handled = self.check_exception_catch(node, exception_types)

        if not error_handled:
            error_handled = self.check_safe_if(node)

        if not error_handled:
            error_handled = self.check_safe_for(node)

        if not error_handled:
            self.errors.append(error)

    def visit_Index(self, node):
        if isinstance(node.value, ast.Num):
            self.handle_num(node)
        elif isinstance(node.value, ast.Str):
            self.handle_str(node)
        elif isinstance(node.value, ast.Name):
            self.handle_name(node)

        self.generic_visit(node)

    def generic_visit(self, node):
        super().generic_visit(node)


class FailsChecker(object):
    name = 'flake8-prevent-fails'
    version = __version__

    def __init__(self, tree, filename, tokens):
        for statement in ast.walk(tree):
            for child in ast.iter_child_nodes(statement):
                child.pf_parent = statement

        self.tree = tree
        self.filename = filename
        self.tokens = tokens

    def check_tree(self):
        visitor = PluginVisitor()
        visitor.visit(self.tree)

        return visitor.errors

    def run(self):
        for error in self.check_tree():
            yield error
