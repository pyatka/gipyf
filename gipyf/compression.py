import copy


class Table:
    def __init__(self, size):
        self.table = [[i] for i in range(size)]
        self.clear_value = size
        self.table.append([size])
        self.end_value = size + 1
        self.table.append([size + 1])

        self.exists_table = {
            "values": [],
            "entity": {}
        }

    def add(self, value):
        exists = True
        check = copy.copy(self.exists_table)
        for key in value[:-1]:
            if key in check["entity"].keys():
                check = check["entity"][key]
            else:
                exists = False

        if exists:
            exists = value[-1] in check["values"]

        if not exists:
            check = self.exists_table
            for key in value[:-1]:
                if key in check["entity"].keys():
                    check = check["entity"][key]
                else:
                    check["entity"][key] = {
                        "values": [],
                        "entity": {}
                    }

                    check = check["entity"][key]

            check["values"].append(value[-1])
            self.table.append(value)

    def get_value(self, index):
        return self.table[index]

    def get_size(self):
        return len(self.table)

    def is_clear(self, value):
        return value == self.clear_value

    def is_end(self, value):
        return value == self.end_value
