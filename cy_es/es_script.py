"""
{
  "query": {
    "function_score": {
      "query": {
        "exists": {
          "field": "meta_info.FileName.keyword"
        }
      },
      "functions": [
        {
          "script_score": {
            "script": {
              "lang": "painless",
              "source": "doc['meta_info.FileName.keyword'].value.toLowerCase().endsWith('060923.png') ? 1 : 0"
            }
          }
        }
      ]
    }
  }
}
"""

"""
    {
      "query": {
        "constant_score": {
          "filter": {
            "function_score": {
              "query": {
                "exists": {
                  "field": "meta_info.FileName.keyword"
                }
              },
              "functions": [
                {
                  "script_score": {
                    "script": {
                      "lang": "painless",
                      "source": "doc['meta_info.FileName.keyword'].value.toLowerCase().endsWith('060923.png') ? 1 : 0"
                    }
                  }
                }
              ]
            }
          },
          "boost": 1000
        }
      }
    }
"""


def script_end_with(field_name, value: str):
    ret = dict(
        function_score=dict(
            query=dict(
                exists=dict(
                    field=f"{field_name}.keyword"
                )

            ),
            functions=[
                dict(
                    script_score=dict(
                        script=dict(
                            lang="painless",
                            source=f"doc['{field_name}.keyword'].value.toLowerCase().endsWith(params.item) ? 100000 : 0",
                            params=dict(
                                item=value.lower()
                            )
                        )

                    )
                )

            ],
            min_score=1

        )
    )
    return ret


def script_start_with(field_name, value: str):
    ret = dict(
        function_score=dict(
            query=dict(
                exists=dict(
                    field=f"{field_name}.keyword"
                )

            ),
            functions=[
                dict(
                    script_score=dict(
                        script=dict(
                            lang="painless",
                            source=f"doc['{field_name}.keyword'].value.toLowerCase().startsWith(params.item) ? 100000 : 0",
                            params=dict(
                                item=value.lower()
                            )
                        )

                    )
                )

            ],
            min_score=1

        )
    )
    return ret


def script_index_of(field_name, value: str):
    ret = dict(
        function_score=dict(
            query=dict(
                exists=dict(
                    field=f"{field_name}.keyword"
                )

            ),
            functions=[
                dict(
                    script_score=dict(
                        script=dict(
                            lang="painless",
                            source=f"doc['{field_name}.keyword'].value.toLowerCase().indexOf(params.item)>=0 ? 100000 : 0",
                            params=dict(
                                item=value.lower()
                            )
                        )

                    )
                )

            ],
            min_score=1
        )
    )
    return ret


def constant_score(filter: dict, boost):
    if boost:
        ret = dict(
            constant_score=dict(
                filter=filter,
                boost=boost
            )
        )
        return ret
    else:
        return filter


def wild_card(field, value, boost):
    if boost:
        ret = {
            "must": {
                "query_string": {
                    "query": value,
                    "fields": [field],
                    "analyze_wildcard": True,
                    "allow_leading_wildcard": True,
                    "boost": boost
                }
            }
        }

        return ret
    else:
        ret = {
            "must": {
                "query_string": {
                    "query": value,
                    "fields": [field],
                    "analyze_wildcard": True,
                    "allow_leading_wildcard": True

                }
            }
        }
        return ret


def match_phrase(field, value, boost):
    if boost:
        ret = {
            "must": {
                "match_phrase": {
                    field: {
                        "query": value,
                        "boost": boost
                    }
                }
            }
        }
    else:
        ret = {
            "must": {
                "match_phrase": {
                    field: {
                        "query": value
                    }
                }
            }
        }
    return ret


def regex_filter(field, value: str, boost):
    if boost:
        ret = {
            "must": {
                "regexp": {
                    field: {
                        "query": value.replace(".", "\\."),
                        "boost": boost
                    }
                }
            }
        }
    else:
        ret = {
            "must": {
                "regexp": {
                    field: value.replace(".", "\\.")
                }
            }
        }
    return ret


def prefix(field, value, boost):
    ret = {
        "must": {
            "prefix": {field: value}
        }
    }
    return ret


def build(doc_field, query_dict: dict):
    doc_field.__es_expr__ = query_dict
    doc_field.__is_bool__ = True
    return doc_field


def must_wrapper(query_dict: dict):
    return {
        "must": query_dict
    }

def simple_query_string(field_name, value, boost):
    ret= {
        "must": {
            "simple_query_string": {
                "query": value,  # search_content,
                "fields": [field_name]

            }
        }
    }
    if boost:
        ret = {
            "must": {
                "simple_query_string": {
                    "query": value,  # search_content,
                    "fields": [field_name],
                    "boost":boost

                }
            }
        }
    return ret
def match(field_name, value, boost):
    ret = {
        "must": {
            "match": {
                field_name: value
            }
        }
    }
    if boost:
        ret = {
            "must": {
                "match": {
                    "name": {
                        field_name: value,
                        "boost": boost
                    }
                }
            }
        }
    return ret

def multi_match_slop_3(field_name, value, boost):
    """
    {
        "query": {
                "multi_match" : {
                    "query": "Thanh toán hợp đồng số 02.11/2023/HĐÐKT/HH-DTH",
                    "fields": ["content"],
                    "type": "phrase",
                    "slop": 3
                }
            }
        }
    @return:
    """
    ret = {
        "must": {
            "multi_match": {
                "query": value,
                "fields":[field_name],
                "type":"phrase",
                "slop": 3
            }
        }
    }
    if boost:
        ret = {
            "must": {
                "multi_match": {
                    "query": value,
                    "fields": [field_name],
                    "type": "phrase",
                    "slop": 3,
                    "boost": boost
                }
            }
        }
    return ret