import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_docs

f1 = cy_docs.fields.code
f2 = cy_docs.fields.name
fx = f2 > f1
import cy_kit
from cyx.base import DbConnect

fs = cy_kit.singleton(DbConnect)
from cy_xdoc.models.files import DocUploadRegister
from cyx.models import FsFile

qr = fs.db("hps-file-test").doc(DocUploadRegister)
qr_files = fs.db("hps-file-test").doc(FsFile)
cy_docs.FUNCS
r = qr.context.find_one(cy_docs.EXPR(qr.fields.RegisterOn.year() < 2023))
arg = qr.context.aggregate().group(
    group_by=(
        cy_docs.fields.Day >> qr.fields.RegisterOn.day(),
        cy_docs.fields.Month >> qr.fields.RegisterOn.month(),
        cy_docs.fields.Year >> qr.fields.RegisterOn.year()

    ),
    accumulators=(
            cy_docs.fields.total >> cy_docs.FUNCS.count()
    )
).sort(
    cy_docs.fields.Year.desc(),
    cy_docs.fields.Month.desc(),
    cy_docs.fields.Day.desc()
)
arg_files = qr_files.context.aggregate().group(
    group_by=(
        cy_docs.fields.year >> qr_files.fields.uploadDate.year(),
        cy_docs.fields.month >> qr_files.fields.uploadDate.month(),
        cy_docs.fields.day >> qr_files.fields.uploadDate.day(),
    ),
    accumulators=cy_docs.fields.totalAmount >> cy_docs.FUNCS.sum(qr_files.fields.length / (1024 * 1024))
)
fx1 = list(arg_files)

fx = list(arg)

print(fx1)
