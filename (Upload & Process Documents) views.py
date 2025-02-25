from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
import openai
import pdfplumber
import docx
from .models import Document
from .serializers import DocumentSerializer

openai.api_key = "your_openai_api_key"  # Replace with your API key

class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        file_path = default_storage.save(file.name, file)
        extracted_text = self.extract_text(file_path)

        document = Document.objects.create(
            user=request.user, title=file.name, file=file, text_content=extracted_text
        )

        summary = self.generate_summary(extracted_text)
        document.summary = summary
        document.save()

        return Response(DocumentSerializer(document).data)

    def extract_text(self, file_path):
        if file_path.endswith(".pdf"):
            return self.extract_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            return self.extract_from_docx(file_path)
        return ""

    def extract_from_pdf(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    def extract_from_docx(self, docx_path):
        doc = docx.Document(docx_path)
        return "\n".join([p.text for p in doc.paragraphs])

    def generate_summary(self, text):
        prompt = f"Summarize the following document in 200 words:\n\n{text}"
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a summarization assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
