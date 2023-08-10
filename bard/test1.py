import torch
from transformers import AutoModel, AutoTokenizer
from pyvi.ViTokenizer import tokenize

PhobertTokenizer = AutoTokenizer.from_pretrained("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")
model = AutoModel.from_pretrained("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")

sentences = ['Kẻ đánh bom đinh tồi tệ nhất nước Anh.',
          'Nghệ sĩ làm thiện nguyện - minh bạch là việc cấp thiết.',
          'Bắc Giang tăng khả năng điều trị và xét nghiệm.',
          'HLV futsal Việt Nam tiết lộ lý do hạ Lebanon.',
          'việc quan trọng khi kêu gọi quyên góp từ thiện là phải minh bạch, giải ngân kịp thời.',
          '20% bệnh nhân Covid-19 có thể nhanh chóng trở nặng.',
          'Thái Lan thua giao hữu trước vòng loại World Cup.',
          'Cựu tuyển thủ Nguyễn Bảo Quân: May mắn ủng hộ futsal Việt Nam',
          'Chủ ki-ốt bị đâm chết trong chợ đầu mối lớn nhất Thanh Hoá.',
          'Bắn chết người trong cuộc rượt đuổi trên sông.'
          ]

sentences = [tokenize(sentence) for sentence in sentences]

inputs = PhobertTokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

with torch.no_grad():
    embeddings = model(**inputs, output_hidden_states=True, return_dict=True).pooler_output
