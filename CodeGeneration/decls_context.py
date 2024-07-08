from .ast_visitor import HulkToCVisitor, Auxiliar

class DefsInC:
    def __init__(self, context) -> None:
        self.context: Context = context
        self.ast_visitor = HulkToCVisitor(context)
        self.protocols = {}
        self.objects_def = {}
        self.method_defs = {}
        self.function_defs = []

        self.generate_definitions()

    def generate_definitions(self):
        for type in self.context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                self.protocols[type.name] = []

                for protocol in self.context.protocols.values():
                    if type.conforms_to(protocol):
                        self.protocols[type.name].append(protocol)

                if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                    create_def = "Object* create" + type.name + " ("
                    create_params = []
                    current = type

                    while current is not None:
                        for att in current.attributes:
                            create_params.append(current.name + "_" + att.name)
                            create_def += "Object* " + create_params[-1] + ", "

                        current = current.parent

                    if len(create_params) > 0:
                        create_def = create_def[:-2]
                    create_def += ")"

                    self.objects_def[type.name] = (create_def, create_params)
                    self.method_defs[type.name] = []
                    for method in type.methods:
                        method_name = "method_" + type.name + "_" + method.name
                        method_def = "Object* " + method_name + " (Object* self"

                        method.node.scope.children[0].find_variable("self").setNameC("self")

                        for i, name in enumerate(method.param_names):
                            id_param = "p" + str(i)
                            method.node.scope.children[0].find_variable(name).setNameC(id_param)
                            method_def += ", Object* " + id_param

                        method_def += ")"
                        self.method_defs[type.name].append((method_def, method_name, method))

        for function in self.context.functions.values():
            if function.name not in ['print', 'sqrt', 'sin', 'cos', 'exp', 'log', 'rand', 'range', 'parse']:
                function_name = "function_" + function.name
                function_def = "Object* " + function_name + " ("

                for i, name in enumerate(function.param_names):
                    id_param = "p" + str(i)
                    function.node.scope.children[0].find_variable(name).setNameC(id_param)
                    function_def += "Object* " + id_param + ", "

                if len(function.param_names):
                    function_def = function_def[:-2]

                function_def += ")"
                self.function_defs.append((function_def, function_name, function))

    @staticmethod
    def generate(ast, context):
        instance = DefsInC(context)
        return instance.generate_definitions()