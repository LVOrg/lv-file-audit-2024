import bs4
import re
class HtmlService:
    def raw(self,html_content:str)->str:
        """
        Clear htlm tag and get raw text
        @param html_content:
        @return:
        """
        html_content = re.sub(r"\s{2,}", " ", html_content)
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        for comment in soup.findAll(text=lambda text: isinstance(text, bs4.Comment)):
            comment.extract()

            # Remove hidden inputs
        hidden_inputs = soup.find_all("input", type="hidden")
        for hidden_input in hidden_inputs:
            hidden_input.extract()
        # Find elements with visibility:hidden or display:none
        hidden_elements = soup.find_all(lambda tag: tag.get('style') and (
                'visibility:hidden' in tag['style'].replace(' ','') or 'display:none' in tag['style'].replace(' ','')
        ))

        # Remove the elements
        for element in hidden_elements:
            element.extract()
        for img_tag in soup.find_all('img'):
            img_tag.extract()
        for img_tag in soup.find_all('image'):
            img_tag.extract()
        return soup.get_text()

if __name__ =="__main__":
    svc = HtmlService()
    html_text = "<!-- ok ok ok --> <p style='display:   none'> test cai coi</p> <p style=\"font-family: tahoma;font-size: 14px;\">Thông báo Giao ban kết quả công tác quý III và Kế hoạch công tác quý IV (Số 642/TB-VIETLOTT ngày 01/10/2024 của Chánh Văn phòng Nguyễn Tuấn Linh)</p><br/><span>Tài liệu chia sẻ :</span><a style='margin: 0px 2px;color: blue;' href='https://vps.vietlott.vn/default/viewfile?id=6701c112-1700-451d-88f9-d98ab5cd37d2'> TB 642.pdf </a><br/><span>Đường dẫn thư mục: Kho tài liệu > Kho tài liệu > Tập công văn đi có tên loại Văn thư/Thông báo</span><script>alert('ok')</script>"
    txt =svc.raw(html_text)
    print(txt)