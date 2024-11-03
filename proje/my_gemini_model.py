import google.generativeai as genai

api_key = ""
# This function analyzes the transcribed text and generates a summary based on certain prompts/parameters.
def summarize_text(input_text):
    if not input_text or input_text.strip() == "":
        print("Input text is empty. Cannot generate summary.")
        return ""  

    genai.configure(api_key=api_key)

    # Model
    summary_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="""
        Amaç: Verilen metin dosyasının içeriğini kapsamlı bir şekilde analiz et. Analiz sırasında benzer konuları içeren zaman damgalarını birleştir. 
        Her bir zaman aralığı için 1-2 cümlelik, anlamlı ve bilgilendirici başlıklar oluştur.  Açıklayıcı, ve tamamlanmış cümleler kullan.

        Yapılması gereken Format:

        [Tüm metnin esas özeti (maksimum 6-7 cümle): Bu bölümde, metnin ana fikrini ve önemli noktalarını özetleyerek okuyucuya genel bir bakış sun.]
        [1. zaman aralığı] [1. zaman aralığı için başlık (maksimum 1-2 cümle): Bu başlık, Metnin ana fikrini ve önemli noktalarını özetleyerek okuyucuya genel bir bakış sun.
        [2. zaman aralığı] [2. zaman aralığı için başlık (maksimum 1-2 cümle): Bu başlık, Metnin ana fikrini ve önemli noktalarını özetleyerek okuyucuya genel bir bakış sun.
        [3. zaman aralığı] [3. zaman aralığı için başlık (maksimum 1-2 cümle): Bu başlık, Metnin ana fikrini ve önemli noktalarını özetleyerek okuyucuya genel bir bakış sun.
        [Diğer zaman aralıkları: Eğer varsa, bu bölümde diğer önemli zaman dilimlerini ve bunlara ait başlıkları ekleyin.]

        Örnek:
        """
    )

    try:
        summary_text = summary_model.generate_content(input_text)
        summary_text = summary_text.text
        print(summary_text) 
        return summary_text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""  

# This function takes two types of input: the original transcript and the summarized transcript.
# The original transcript is chunked and sent back to the model while the summarized transcript is also added to the prompt.
# This way, while deriving study notes from the chunked transcript, the model does not lose the topic.
# Sending the transcript in chunks allows us to obtain a higher quality output.

def improve_notes(input_text, summary_text):
    # Check if input_text is empty
    if not input_text or input_text.strip() == "":
        print("Input text for improving notes is empty. Cannot generate notes.")
        return ""

    # Initialize the generative model
    improve_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=f"""
        #### Amaç
        Sana verilen metin parçasından YKS sınavına uygun bir not çıkarmak. 
        Notu oluştururken konunun detaylarına in ve spesifik detaylar ver.
        Bu not, o alanda eğitimli kişiler tarafından okunacak bu nedenle teknik kısımları açıkla.
        YKS sınavına hazırlanan öğrencilere hitap et.
         

        #### Gerekli Adımlar

        1. **Zaman Aralıklarını Belirleme**:
        - Sana verilen zaman aralıklarını yaz.
        - Eğer birden fazla zaman aralığı varsa, bunları birleştirerek tek bir ifade halinde sun.
        2. **Notları oluşturma**
        -   Sana verilen metin özetinden fikir alarak bu metin parçasının anlattığı şeyi analiz et. 
        -   Analiz ettiğin metinden ders notu oluştur bu notun öğrenciye konuyu anlaması için gerekli bilgileri verdiğinden emin ol.
        -   Konuyla alakalı yorumlar yapabilir ek bilgiler ve tavsiyeler verebilirsin.
        3. **Konu**:
        - Metin özeti: {summary_text}
        
    """
    )

    improved_notes = []
    word_limit = 1000
    words = input_text.split()  

    # Process the summary in chunks
    for i in range(0, len(words), word_limit):
        chunk = " ".join(words[i:i + word_limit])  # Get a chunk of words
        try:
            improved_content = improve_model.generate_content(chunk)  # Generate improved content
            improved_notes.append(improved_content.text)  # Add the generated content to the list
        except Exception as e:
            print(f"Error generating improved notes for chunk: {e}")
            continue  # Skip this chunk if there's an error

    # Combine all improved notes into a single string
    final_improved_notes = "\n".join(improved_notes)

    return final_improved_notes


def process_text(input_text):
    summary_text = summarize_text(input_text)
    if summary_text:
        return improve_notes(input_text, summary_text)
    else:
        return "Summary text is empty, cannot improve notes."
