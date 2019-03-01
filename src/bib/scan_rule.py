import yaml
import fnmatch
import re
import collections


class Rule(object):
    """
    yml tags rule:
    ---
    tags:
      rule1:
        ext_name: jpg,png,bmp
        min_size: 1M
        path_match: image/.*
      rule2:
        ext_name:
          - jpg
          - png
          - bmp
        path_rule:
          - */png
          - */jpn
    """
    def __init__(self,
                 name,
                 ext_name=None,
                 min_size=None,
                 max_size=None,
                 path_re=None,
                 path_match=None,
                 mime_type=None):
        self.name = name

        if isinstance(ext_name, str):
            self.ext_names = [n for n in ext_name.split(',') if n]
        elif isinstance(ext_name, list):
            self.ext_names = ext_name
        elif ext_name is None:
            self.ext_names = None
        else:
            raise SyntaxError("expected name list or name rule")

        if isinstance(path_match, list):
            self.path_matches = path_match
        elif path_match is None:
            self.path_matches = None
        else:
            raise SyntaxError("expected path_match list")

        if path_re:
            self.path_re = re.compile(path_re)
        else:
            self.path_re = None

        self.min_size = min_size
        self.max_size = max_size
        self.mime_type = None

    def __str__(self):
        return f"<{self.__class__.__name__}_{self.name}>"

    def check_ext_name(self, file_path: str):
        if self.ext_names:
            for ext_name in (i for i in self.ext_names if i):
                if file_path.endswith(ext_name):
                    return True
            return False
        return True

    @staticmethod
    def sizestr_2_int(size: str, base=1000):
        return {
            'g': base ** 3,
            'm': base ** 2,
            'k': base
        }[size[-1]] * float(size[:-1])

    def check_max_size(self, size: int):
        if self.max_size:
            if size > self.sizestr_2_int(self.max_size):
                return False
        return True

    def check_min_size(self, size: int):
        if self.min_size:
            if size < self.sizestr_2_int(self.min_size):
                return True
        return True

    def check_path_match(self, file_path):
        if self.path_matches:
            for path_match in self.path_matches:
                if fnmatch.fnmatch(file_path, path_match):
                    return True
            return False
        return True

    def check_path_re(self, file_path):
        if self.path_re:
            if not self.path_re.match(file_path):
                return False
        return True

    def check(self, file_path, size):
        return (
            self.check_ext_name(file_path)
            and self.check_max_size(size)
            and self.check_min_size(size)
            and self.check_path_match(file_path)
            and self.check_path_re(file_path)
        )


class RuleEngine(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.rules = collections.OrderedDict()
        self.load_config()
        self.load_tag_rule()

    def load_config(self):
        with open(self.config_file, 'r') as fp:
            self._data = yaml.load(fp.read())

    def save_config(self):
        with open(self.config_file, 'w') as fp:
            yaml.dump(self._data, fp)

    def load_tag_rule(self):
        tags = self._data.get('tags', {})
        if not isinstance(tags, dict):
            raise SyntaxError("excepted dict tags config")
        for rule_name, config in tags.items():
            self.rules[rule_name] = Rule(rule_name, **config)

    def file_tags(self, file_path, size):
        tags = []
        for rname, rule in self.rules.items():
            if rule.check(file_path, size):
                tags.append(rname)
        return tags

    def could_index(self, file_path, size):
        tags = self.file_tags(file_path, size)
        for i_rule in self._data['index'].split(','):
            match_rule = True
            for r_node in i_rule.split(":"):
                if r_node.startswith("!"):  # op
                    if r_node[1:] in tags:
                        match_rule = False
                        break
                else:
                    if r_node not in tags:
                        match_rule = False
                        break
            if match_rule:
                return True
        return False

