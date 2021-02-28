import regex
import unittest

from os2datascanner.engine2.rules.address import AddressRule
from os2datascanner.engine2.rules.rule import Sensitivity


# https://www.regular-expressions.info/unicode.html#category
# \p{L}: match a unicode letter, \p{Lu}: Uppercase letter
# https://regex101.com/r/zJBsXw/9
# Match whitespace except newlines


text = \
(
"H.C. Andersens Boul 15, 2. 0006, 1553 København V, Danmark\n"
"H.C. Andersens Boul, 1553 Kbh. V\n"
"10. Februar Vej 75\n"                    # unusual names from the list
"400-Rtalik\n"
"H/F Solpl-Lærkevej\n"
"H. H. Hansens Vej\n"
"H H Kochs Vej\n"
"Øer I Isefjord 15\n"                     # does unicode work?
"Tagensvej 15\n"                          # whitelisted
"der er en bygning på PilÆstræde, men\n"  # not in address list/blacklisted
"Magenta APS, PilÆstræde 43,  3. sal, 1112 København\n"
)


expected = \
    [
        ["H.C. Andersens Boul 15, 2. 0006, 1553 København V",
         Sensitivity.CRITICAL.value],
        ["H.C. Andersens Boul, 1553 Kbh. V", Sensitivity.PROBLEM.value],
        ["10. Februar Vej 75", Sensitivity.CRITICAL.value],
        ["400-Rtalik", Sensitivity.PROBLEM.value],
        ["H/F Solpl-Lærkevej", Sensitivity.PROBLEM.value],
        ["H. H. Hansens Vej", Sensitivity.PROBLEM.value],
        ["H H Kochs Vej", Sensitivity.PROBLEM.value],
        ["Øer I Isefjord 15", Sensitivity.CRITICAL.value],
        ["PilÆstræde", Sensitivity.CRITICAL.value],
        ["PilÆstræde 43,  3. sal, 1112 København", Sensitivity.CRITICAL.value],
    ]

whitelist = ["Tagensvej"]
blacklist = ["PilÆstræde"]

candidates = [
    (
        # user supplied sensitivity is not used
        AddressRule(whitelist=whitelist, blacklist=blacklist, sensitivity=Sensitivity.INFORMATION.value),
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
