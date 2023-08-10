def pack_list(url:str,app_name:str, items):
    ret_items = []

    for x in items:
        upload_doc_item = x._source.data_item
        if upload_doc_item:
            # upload_doc_item.UploadId = upload_doc_item._id
            upload_doc_item.Highlight = x.highlight

            upload_doc_item.AppName = app_name
            if hasattr(upload_doc_item, "FullFileName") and upload_doc_item.FullFileName is not None:
                upload_doc_item.RelUrlOfServerPath = f"/{app_name}/file/{upload_doc_item.FullFileName}"
                upload_doc_item.UrlOfServerPath = f"{url}/{app_name}/file/{upload_doc_item.FullFileName}"
            if hasattr(upload_doc_item, "FileName") and upload_doc_item.FileName is not None:
                upload_doc_item.ThumbUrl = url + f"/{app_name}/thumb/{upload_doc_item['_id']}/{upload_doc_item.FileName}.png"

            upload_doc_item.privileges = x._source.get('privileges')
            upload_doc_item.meta_data =upload_doc_item.meta_data or  x._source.get('meta_info')
            upload_doc_item.__score__ = x._score
            ret_items += [upload_doc_item]
    return ret_items