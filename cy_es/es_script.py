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
def script_end_with(field_name,value):
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
                            lang= "painless",
                            source=f"doc['{field_name}.keyword'].value.toLowerCase().endsWith('{value}') ? 1 : 0"
                        )
                    )
                )

            ]

        )
    )
    return ret