from vws import RDRSegmenter, Tokenizer
rdrsegment = RDRSegmenter.RDRSegmenter()
tokenizer = Tokenizer.Tokenizer()
output = rdrsegment.segmentRawSentences(tokenizer,"Lượng khách Thái bắt đầu gia tăng từ đầu năm 2005. Bên cạnh đó, kể từ tháng 10-2005 đến nay, từ khi được phép của VN, các đoàn caravan của Thái Lan cũng đã ồ ạt đổ vào VN.")
print(output)