import typing

__sepilcal_chacters__ = [
    "\n",
    "\t",
    "\r"
]
def well_form_text(content:typing.Optional[str])->typing.Optional[str]:
    global  __sepilcal_chacters__
    ret = content
    for x in __sepilcal_chacters__:
        ret = ret.replace(x,' ')
    while '  ' in ret:
        ret= ret.replace('  ', ' ')
    ret= ret.rstrip(' ').lstrip(' ')
    return ret

