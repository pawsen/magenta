import regex
import unittest

from os2datascanner.engine2.rules.name import NameRule
from os2datascanner.engine2.rules.rule import Sensitivity


# https://www.regular-expressions.info/unicode.html#category
# \p{L}: match a unicode letter, \p{Lu}: Uppercase letter
# https://regex101.com/r/nT9wL5/8
# Match whitespace except newlines

_whitespace = r"[^\S\n\r]+"
_simple_name = r"\p{Lu}(\p{L}+|\.?)"
_name = r"{0}(-{0})?".format(_simple_name)
full_name_regex = regex.compile(
    r"\b(?P<first>" + _name + r")" +
    r"(?P<middle>(" + _whitespace + _name + r"){0,3})" +
    r"(?P<last>" + _whitespace + _name + r"){1}\b", regex.UNICODE)


text = \
(
"Anders\n"           # match standalone name.
"Anders and\n"       # match standalone name
"Anders      And\n"  # match full name. Only first name in namelist
"Anders And\n"       # match full name
"A. And\n"           # match regex, but not in namelist -> not returned
"J.-V And\n"         # -"-
#"J-V. And\n"         # -"-
#"J.V. And\n"         # -"-
"J.v. And\n"         # Does not match regex
"Joakim And\n"       # match regex and namelist, but in whitelist
"Andrea V. And\n"    # First name in namelist
"Joakim Nielsen\n"   # last name in namelist and not whitelisted.
"Anders Andersine Mickey Per Nielsen\n"
                     # match full name
"Nora Malkeko\n"     # In blacklist
)


expected = \
    [
        ["Anders", Sensitivity.INFORMATION.value],
        ["Anders", Sensitivity.INFORMATION.value],
        ["Anders And", Sensitivity.PROBLEM.value],
        ["Anders      And", Sensitivity.PROBLEM.value],
        ["Andrea V. And", Sensitivity.PROBLEM.value],
        ["Joakim Nielsen", Sensitivity.PROBLEM.value],
        ["Anders Andersine Mickey Per Nielsen",
         Sensitivity.CRITICAL.value],
        ["Nora Malkeko", Sensitivity.CRITICAL.value],
    ]

whitelist = ["Joakim"]
blacklist = ["Malkeko"]

#def test_simplerule_matches():
candidates = [
    (
        NameRule(whitelist=whitelist, blacklist=blacklist, sensitivity=Sensitivity.INFORMATION.value),
        text,
        expected
    )
]

for rule, in_value, expected in candidates:
    matches = rule.match(in_value)
    match = list(matches)
    print(match)

class RuleTests(unittest.TestCase):
    def test_namerule_matches(self):
        for rule, in_value, expected in candidates:
            with self.subTest(rule):
                json = rule.to_json_object()
                back_again = rule.from_json_object(json)
                self.assertEqual(rule, back_again)

            with self.subTest(rule):
                matches = rule.match(in_value)
                result = [[match["match"], match['sensitivity']] for match in matches]
                print(result)
                if expected:
                    self.assertCountEqual(
                            result, expected)
                else:
                    self.assertFalse(list(matches))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
