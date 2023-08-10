"""
This library provide a service in which stats all information about sizes and number of items in an application
Stats of File-Service including:
    Total of:
        1 - Finished items
        2 - Unfinished items (an unfinished item in case.A
            file was still uploading. Remember that: Some big file spend several days to finish content)
    Service also stat each day in a whole time of File-Service-System

    The stat looks like:

        total_items:...
        total_unfinished_items: ...
        total_size: ...
        total_unfinished_size: ...
        total_real_size: ...
        └── 2023
            ├── total_items:...
            ├── total_unfinished_items: ...
            ├── total_size: ...
            ├── total_unfinished_size: ...
            ├── total_real_size: ...
            ├── 01:
            │   ├── 01:
            │   │   ├── total_items:...
            │   │   ├── total_unfinished_items: ...
            │   │   ├── total_size: ...
            │   │   ├── total_unfinished_size: ...
            │   │   └── total_real_size: ...
            │   ├── ...
            │   ├── 30:
            │   │   ├── total_items:...
            │   │   ├── total_unfinished_items: ...
            │   │   ├── total_size: ...
            │   │   ├── total_unfinished_size: ...
            │   │   └── total_real_size: ...
            │   ├── total_items:...
            │   ├── total_unfinished_items: ...
            │   ├── total_size: ...
            │   ├── total_unfinished_size: ...
            │   └── total_real_size: ...
            ├── ...
            └── 12
                ├──
                │   ├── total_items:...
                │   ├── total_unfinished_items: ...
                │   ├── total_size: ...
                │   ├── total_unfinished_size: ...
                │   ├── total_real_size: ...
                │   └── total_items:...
                ├── total_unfinished_items: ...
                ├── total_size: ...
                ├── total_unfinished_size: ...
                └── total_real_size: ...
        ...
        └── 2024

"""


import datetime
import typing

import cy_docs
import cy_kit
import cyx.base
from cyx.base import DbConnect

"""
Need a db connection to do everything else
"""
import cy_xdoc

"""
Very useful lib for Mongodb manipulation
"""

from cy_xdoc.models.apps import App
from cy_xdoc.models.files import DocUploadRegister
from cyx.models import FsFile


class AppStatServices:
    """
    All about stat of application here
    """

    def __init__(self, db_connect: DbConnect = cy_kit.singleton(DbConnect)):
        self.db_connect = db_connect
    def get_context(self,app_name:str)->cyx.base.DbCollection[DocUploadRegister]:
        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        return docs

    def make_sum(self, agg: cy_docs.AggregateDocument,
                 docs: cyx.base.DbCollection[cy_xdoc.models.files.DocUploadRegister], unit_type: int = 3):
        unit_type= 2
        unit = 1024 ** unit_type
        return agg.project(
            cy_docs.fields.total_volume >> cy_docs.FUNCS.sum(
                cy_docs.FUNCS.cond(
                    docs.fields.SizeUploaded==docs.fields.SizeInBytes,docs.fields.SizeUploaded/unit,0)

            ),
            cy_docs.fields.total_unfinished_volume >> cy_docs.FUNCS.sum(
                cy_docs.FUNCS.cond(
                    docs.fields.SizeUploaded<docs.fields.SizeInBytes,docs.fields.SizeUploaded/ unit,0
                )
            ),
            cy_docs.fields.total_unfinished_files >> cy_docs.FUNCS.sum(cy_docs.FUNCS.cond(
                    docs.fields.SizeUploaded ==docs.fields.SizeInBytes,1,0)
            ),
            cy_docs.fields.total_files >> cy_docs.FUNCS.sum(cy_docs.FUNCS.cond(
                    docs.fields.SizeUploaded <docs.fields.SizeInBytes,1,0)
            )
        )

    def get_year_range(self, app_name: str) -> typing.Tuple[typing.Optional[int], typing.Optional[int]]:

        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        yearly_agg = docs.context.aggregate().project(
            cy_docs.fields.min_year >> cy_docs.FUNCS.min(docs.fields.RegisterOn.year()),
            cy_docs.fields.max_year >> cy_docs.FUNCS.max(docs.fields.RegisterOn.year()),
        )
        data = yearly_agg.first_item()
        if data:
            return data.min_year, data.max_year
        else:
            return None, None

    def get_day_range(self, app_name: str, year: int, month: int) -> typing.Tuple[
        typing.Optional[int], typing.Optional[int]]:

        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        yearly_agg = docs.context.aggregate().match(
            cy_docs.EXPR((docs.fields.RegisterOn.year() == year) & \
                         (docs.fields.RegisterOn.month() == month))
        ).project(
            cy_docs.fields.min_year >> cy_docs.FUNCS.min(docs.fields.RegisterOn.day()),
            cy_docs.fields.max_year >> cy_docs.FUNCS.max(docs.fields.RegisterOn.day()),
        )
        data = yearly_agg.first_item()
        if data:
            return data.min_year, data.max_year
        else:
            return None, None

    def get_month_range(self, app_name: str, year: int) -> typing.Tuple[typing.Optional[int], typing.Optional[int]]:

        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        yearly_agg = docs.context.aggregate().match(
            cy_docs.EXPR(docs.fields.RegisterOn.year() == year)
        ).project(
            cy_docs.fields.min_year >> cy_docs.FUNCS.min(docs.fields.RegisterOn.month()),
            cy_docs.fields.max_year >> cy_docs.FUNCS.max(docs.fields.RegisterOn.month()),
        )
        data = yearly_agg.first_item()
        if data:
            return data.min_year, data.max_year
        else:
            return None, None

    def quick_stats(self, app_name: str, from_year: int, to_year: int):

        unit = 1024 * 1024
        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        total_items = cy_docs.fields.total_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond((
                    (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                    (docs.fields.Status == 1)
            ), 1, 0)
        )
        total_size = cy_docs.fields.total_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond(
                (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                (docs.fields.Status == 1)
                , docs.fields.SizeInBytes / unit, 0)
        )
        total_unfinished_items = cy_docs.fields.total_unfinished_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond(
                (docs.fields.SizeInBytes < docs.fields.SizeUploaded)
                , 1, 0)
        )
        total_unfinished_size = cy_docs.fields.total_unfinished_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond(
                (docs.fields.SizeInBytes < docs.fields.SizeUploaded)
                , docs.fields.SizeInBytes / unit, 0)
        )
        selector = [
            total_items,
            total_unfinished_items,
            total_size,
            total_unfinished_size
        ]
        for year in range(from_year, to_year + 1):
            year_str = "{:04d}".format(year)
            total_items_year = cy_docs.fields[f"total_items_{year_str}"] >> \
                               cy_docs.FUNCS.sum(
                                   cy_docs.FUNCS.cond((
                                           (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                           (docs.fields.Status == 1) &
                                           (docs.fields.RegisterOn.year() == year)
                                   ), 1, 0)
                               )
            total_unfinished_items_year = cy_docs.fields[f"total_unfinished_items_{year_str}"] >> \
                                          cy_docs.FUNCS.sum(
                                              cy_docs.FUNCS.cond((
                                                      (docs.fields.SizeInBytes < docs.fields.SizeUploaded) & \
                                                      (docs.fields.RegisterOn.year() == year)
                                              ), 1, 0)
                                          )

            total_size_year = cy_docs.fields[f"total_size_{year_str}"] >> \
                              cy_docs.FUNCS.sum(
                                  cy_docs.FUNCS.cond((
                                          (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                          (docs.fields.Status == 1) &
                                          (docs.fields.RegisterOn.year() == year)
                                  ), docs.fields.SizeInBytes, 0)
                              )
            total_unfinished_size_year = cy_docs.fields[f"total_unfinished_size_{year_str}"] >> \
                                         cy_docs.FUNCS.sum(
                                             cy_docs.FUNCS.cond((
                                                     (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                     (docs.fields.Status == 1) &
                                                     (docs.fields.RegisterOn.year() == year)
                                             ), docs.fields.SizeInBytes, 0)
                                         )
            selector += [
                total_items_year,
                total_unfinished_items_year,
                total_size_year,
                total_unfinished_size_year
            ]
            for montth in range(1, 13):
                montth_str = "{:02d}".format(montth)
                total_items_month = cy_docs.fields[f"total_items_{year_str}_{montth_str}"] >> \
                                    cy_docs.FUNCS.sum(
                                        cy_docs.FUNCS.cond((
                                                (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                (docs.fields.Status == 1) &
                                                (docs.fields.RegisterOn.year() == year) & \
                                                (docs.fields.RegisterOn.month() == montth)
                                        ), 1, 0)
                                    )
                total_unfinished_items_month = cy_docs.fields[f"total_unfinished_items_{year_str}_{montth_str}"] >> \
                                               cy_docs.FUNCS.sum(
                                                   cy_docs.FUNCS.cond((
                                                           (docs.fields.SizeInBytes < docs.fields.SizeUploaded) & \
                                                           (docs.fields.RegisterOn.year() == year) & \
                                                           (docs.fields.RegisterOn.month() == montth)
                                                   ), 1, 0)
                                               )

                total_size_month = cy_docs.fields[f"total_size_{year_str}_{montth_str}"] >> \
                                   cy_docs.FUNCS.sum(
                                       cy_docs.FUNCS.cond((
                                               (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                               (docs.fields.Status == 1) &
                                               (docs.fields.RegisterOn.year() == year) & \
                                               (docs.fields.RegisterOn.month() == montth)
                                       ), docs.fields.SizeInBytes, 0)
                                   )
                total_unfinished_size_month = cy_docs.fields[f"total_unfinished_size_{year_str}_{montth_str}"] >> \
                                              cy_docs.FUNCS.sum(
                                                  cy_docs.FUNCS.cond((
                                                          (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                          (docs.fields.Status == 1) &
                                                          (docs.fields.RegisterOn.year() == year) & \
                                                          (docs.fields.RegisterOn.month() == montth)
                                                  ), docs.fields.SizeInBytes, 0)
                                              )

                selector += [
                    total_items_month,
                    total_unfinished_items_month,
                    total_size_month,
                    total_unfinished_size_month
                ]

                for day in range(1, 32):
                    day_str = "{:02d}".format(day)
                    total_items_day = cy_docs.fields[f"total_items_{year_str}_{montth_str}_{day_str}"] >> \
                                      cy_docs.FUNCS.sum(
                                          cy_docs.FUNCS.cond((
                                                  (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                  (docs.fields.Status == 1) &
                                                  (docs.fields.RegisterOn.year() == year) & \
                                                  (docs.fields.RegisterOn.month() == montth) & \
                                                  (docs.fields.RegisterOn.day() == day)
                                          ), 1, 0)
                                      )
                    total_unfinished_items_day = cy_docs.fields[
                                                     f"total_unfinished_items_{year_str}_{montth_str}_{day_str}"] >> \
                                                 cy_docs.FUNCS.sum(
                                                     cy_docs.FUNCS.cond((
                                                             (docs.fields.SizeInBytes < docs.fields.SizeUploaded) & \
                                                             (docs.fields.RegisterOn.year() == year) & \
                                                             (docs.fields.RegisterOn.month() == montth) & \
                                                             (docs.fields.RegisterOn.day() == day)
                                                     ), 1, 0)
                                                 )

                    total_size_day = cy_docs.fields[f"total_size_{year_str}_{montth_str}"] >> \
                                     cy_docs.FUNCS.sum(
                                         cy_docs.FUNCS.cond((
                                                 (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                 (docs.fields.Status == 1) &
                                                 (docs.fields.RegisterOn.year() == year) & \
                                                 (docs.fields.RegisterOn.month() == montth) & \
                                                 (docs.fields.RegisterOn.day() == day)
                                         ), docs.fields.SizeInBytes, 0)
                                     )
                    total_unfinished_size_day = cy_docs.fields[
                                                    f"total_unfinished_size_{year_str}_{montth_str}_{day_str}"] >> \
                                                cy_docs.FUNCS.sum(
                                                    cy_docs.FUNCS.cond((
                                                            (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                            (docs.fields.Status == 1) &
                                                            (docs.fields.RegisterOn.year() == year) & \
                                                            (docs.fields.RegisterOn.month() == montth) & \
                                                            (docs.fields.RegisterOn.day() == day)
                                                    ), docs.fields.SizeInBytes, 0)
                                                )

                    selector += [
                        total_items_day,
                        total_unfinished_items_day,
                        total_size_day,
                        total_unfinished_size_day
                    ]

        agg = docs.context.aggregate().project(
            *tuple(selector)
        )

        ret = agg.first_item()
        return ret

    def stat_app(self, app_name: str):
        from_year, to_year = self.get_year_range(app_name)
        if from_year is None:
            return None
        else:
            ret = self.quick_stats(app_name, from_year, to_year)
            return ret

    def stat_by_month(self, app_name: str, year: int, month: int, unit_type: int = 3):

        check = datetime.datetime(year=year, month=month, day=1, hour=23, minute=59, second=59)
        if check.year != year or check.month != month:
            raise Exception(f"Invalid time {year}-{month}")

        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        agg = docs.context.aggregate().match(
            cy_docs.EXPR((docs.fields.RegisterOn.year() == year) & \
                         (docs.fields.RegisterOn.month() == month))
        )
        agg = self.make_sum(agg, docs, unit_type)
        ret = agg.first_item()
        return ret

    def stat_by_year(self, app_name: str, year: int, unit_type: int = 3):

        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        agg = docs.context.aggregate().match(
            cy_docs.EXPR(docs.fields.RegisterOn.year() == year)
        )
        ret = self.make_sum(agg, docs, unit_type).first_item()
        return ret

    def stat_by_day(self, app_name: str, year: int, month: int, day: int, unit_type: int = 3):

        check = datetime.datetime(year=year, month=month, day=day, hour=23, minute=59, second=59)
        if check.year != year or check.month != month and check.day != day:
            raise Exception(f"Invalid time {year}-{month}-{day}")
        from_time = datetime.datetime(year=year, month=month, day=day, hour=0, minute=0, second=0)
        to_time = check
        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        agg = docs.context.aggregate().match(
            (docs.fields.RegisterOn >= from_time) & \
            (docs.fields.RegisterOn <= to_time)
        )
        ret = self.make_sum(agg, docs, unit_type).first_item()
        return ret

    def get_stat_of_app(self, app_name: str):
        ret  = {}
        from_year, to_year = self.get_year_range(app_name)
        if to_year:
            for year in range(from_year, to_year + 1):
                stat_data = self.stat_by_year(app_name,year)
                ret["{:04d}".format(year)] = stat_data
                from_month, to_month = self.get_month_range(app_name, year)

                if to_month:
                    for month in range(from_month, to_month + 1):
                        stat_data = self.stat_by_month(
                            app_name=app_name,
                            year=year,
                            month=month

                        )
                        ret["{:02d}".format(month)] = stat_data
                        from_day, to_day = self.get_day_range(app_name, year, month)
                        if to_day:
                            for day in range(from_day, to_day + 1):
                                stat_data = self.stat_by_day(
                                    app_name=app_name,
                                    year=year,
                                    month=month,
                                    day=day

                                )
                                ret["{:02d}".format(day)] = stat_data
        return ret

    def update_grant_stat(self, app_name:str):
        docs = self.get_context(app_name)
        agg = docs.context.aggregate().project(
            cy_docs.fields.total_volume >> cy_docs.FUNCS.sum(
                cy_docs.FUNCS.cond(
                    docs.fields.SizeInBytes==docs.fields.SizeUploaded, docs.fields.SizeInBytes, 0
                )
            ),
            cy_docs.fields.total_unfinished_volume >> cy_docs.FUNCS.sum(
                cy_docs.FUNCS.cond(
                    docs.fields.SizeInBytes > docs.fields.SizeUploaded, docs.fields.SizeUploaded, 0
                )
            )
        )
        


