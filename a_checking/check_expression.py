### I have "a=1 or b=2 and not c and not (d=2)"
# any python lib parse that text into
result= dict(
    _type='expr',
    left=dict(
        _type='expr',
        text="a=1",
        left= dict(
            _type="label",
            text="a",
            value='a'
        ),
        op='=',
        right=dict(
            _type='const',
            text="1",
            value='1'
        )
    ),
    op='or',
    right=dict(
        _type='expr',
        text="b=2 and not c and not (d=2)",
        left=dict(
            _type='expr',
            text="b=2",
            left=dict(
                text="b",
                _type='label',
                value='b'
            ),
            op="=",
            right=dict(
                _type="const",
                text="1",
                value="1"
            )
        ),
        op="and",
        right=dict(
            _type="expr",
            text="not c and not (d=2)",
            left=dict(
                _type="expr",
                text="not c",
                op="not",
                left=None,
                right=dict(
                    _type="label",
                    text="c",
                    value="c"
                )

            ),
            op="and",
            right=dict(
                _type="expr",
                text="not (d=2)",
                left=None,
                op="not",
                right=dict(
                    _type="expr",
                    text="d=2",
                    left=dict(
                        _type="label",
                        text="d",
                        value="d"
                    ),
                    op="=",
                    right=dict(
                        _type="const",
                        text="2",
                        value="2"
                    )
                )
            )
        )
    )
)


from pyparsing import infixNotation, opAssoc, Keyword, Word, alphas, alphanums, nums, ParserElement

ParserElement.enablePackrat()

# Define the grammar
identifier = Word(alphas, alphanums + "_")
integer = Word(nums)
operand = identifier | integer

# Define the operators
equals = Keyword("=")
not_op = Keyword("not")
and_op = Keyword("and")
or_op = Keyword("or")

# Define the expression
expr = infixNotation(operand,
    [
        (not_op, 1, opAssoc.RIGHT),
        (equals, 2, opAssoc.LEFT),
        (and_op, 2, opAssoc.LEFT),
        (or_op, 2, opAssoc.LEFT),
    ])

# Parse the expression
parsed_expr = expr.parseString("a=1 or b=2 and not c and not (d=2)", parseAll=True)

# Function to convert parsed expression to dictionary
def parse_to_dict(parsed):
    if isinstance(parsed, str):
        return {"_type": "label", "text": parsed, "value": parsed}
    elif len(parsed) == 1:
        return parse_to_dict(parsed[0])
    elif len(parsed) == 2:
        return {"_type": "expr", "op": parsed[0], "right": parse_to_dict(parsed[1])}
    elif len(parsed) == 3:
        return {
            "_type": "expr",
            "left": parse_to_dict(parsed[0]),
            "op": parsed[1],
            "right": parse_to_dict(parsed[2]),
        }

# Convert parsed expression to dictionary
result = parse_to_dict(parsed_expr.asList()[0])
print(result)
from cyx.repository import Repository
from cy_docs import DocumentObject, fields

class Student(DocumentObject):
    __collection_name__ = "my-student"

    id = fields.StringField()
    name = fields.StringField()
    age = fields.IntegerField()
    grade = fields.StringField()

    def __init__(self):
        super().__init__()