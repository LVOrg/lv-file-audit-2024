"""
    Remove all unfinished files were create at the past someday
    Xóa tất cả các tệp chưa hoàn thành đã được tạo vào một ngày nào đó trong quá khứ
    Time after time is 2 days
"""
import datetime
import pathlib
import sys
import time

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_docs
import cy_kit
from cy_xdoc.services.apps import AppServices


def clean_app(app_name: str, day_ago: int = 2):
    """
    Remove all unfinished files were create at the past someday
    Xóa tất cả các tệp chưa hoàn thành đã được tạo vào một ngày nào đó trong quá khứ
    :param app_name:
    :param day_ago:
    :return:
    """
    import cy_kit
    from cy_xdoc.services.files import FileServices

    file_service = cy_kit.singleton(FileServices)

    qr = file_service.get_queryable_doc(app_name=app_name)
    from_date = datetime.datetime.utcnow() - datetime.timedelta(days=day_ago)
    items = qr.context.aggregate().match(
        (qr.fields.RegisterOn < from_date) & \
        (qr.fields.Status == 0) & \
        (qr.fields.SizeInBytes > 0) & \
        cy_docs.EXPR(qr.fields.SizeUploaded < qr.fields.SizeInBytes)

    ).sort(
        qr.fields.RegisterOn.desc()
    ).project(
        qr.fields.id,
        qr.fields.MainFileId,
        qr.fields.AvailableThumbs,
        qr.fields.AvailableThumbSize,
        qr.fields.OCRFileId,
        qr.fields.OriginalFileId,
        qr.fields.NumOfChunks,
        qr.fields.NumOfChunksCompleted,
        qr.fields.SizeInBytes,
        qr.fields.SizeUploaded
    )
    for x in items:
        print(f"app={app_name} remove {x._id}")
        try:
            file_service.remove_upload(app_name=app_name, upload_id=x._id)
        except Exception as e:
            print(f"app={app_name} remove {x._id} fail")
            print(e)


if __name__ == "__main__":
    apps_service = cy_kit.singleton(AppServices)
    while True:
        apps = apps_service.get_list(app_name='admin')
        for x in apps:
            print(f"Process {x['Name']}")
            try:
                clean_app(x["Name"])
            except Exception as e:
                print(e)
        time.sleep(2 * 24 * 60 * 50)  # wait until the next 2 days
        print(f"I am waiting until the next 2 days")
