import cy_es
fx= (cy_es.DocumentFields("MyDoc")!=None) & (cy_es.DocumentFields("MyDoc").Code=='xyz')
print(cy_es.DocumentFields("data_item").code==1)
fx = (cy_es.buiders.data_item != None) & (cy_es.buiders.data_item.FileName.__contains__('*.mp4'))
fx=cy_es.buiders.code==123
print(fx)
fx= cy_es.parse_expr("data_item !=None and data_item.code=1")
print(fx)