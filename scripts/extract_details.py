from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import django
from django.conf import settings
from ai.config import OPEN_AI_KEY

from userapp.models.user import (
    User, UserDocuments, UserDocumentSummary
)

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
# django.setup()

# Initialize OpenAI
llm = ChatOpenAI(
    api_key=OPEN_AI_KEY,
    temperature=0,
    model_name="gpt-4"
)

def process_pdf_with_langchain(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(pages)
    
    return "\n".join([split.page_content for split in splits])

def analyze_academic_document(text, document_type):
    prompts = {
        "tenth": PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze this 10th grade academic document and extract:
            1. Overall percentage
            2. CGPA (if available)
            3. Year of passing
            4. School board
            5. Key subjects and their marks

            Format the response as JSON.
            
            Text: {text}
            """
        ),
        "inter": PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze this 12th grade academic document and extract:
            1. Overall percentage
            2. CGPA (if available)
            3. Stream (Science/Commerce/Arts)
            4. Year of passing
            5. School board
            6. Key subjects and their marks

            Format the response as JSON.
            
            Text: {text}
            """
        ),
        "disability": PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze this disability certificate and extract:
            1. Type of disability
            2. Percentage of disability
            3. Issuing authority
            4. Date of issue
            5. Validity period if any

            Format the response as JSON.
            
            Text: {text}
            """
        ),
        "sports": PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze this sports certificate and extract:
            1. Sport type
            2. Achievement level
            3. Issuing authority
            4. Date of issue
            5. Competition details

            Format the response as JSON.
            
            Text: {text}
            """
        )
    }

    if document_type not in prompts:
        raise ValueError(f"Unknown document type: {document_type}")

    chain = LLMChain(llm=llm, prompt=prompts[document_type])
    return chain.run(text)

def save_document_summary(user, document_analyses):
    summary, created = UserDocumentSummary.objects.get_or_create(user=user)
    
    # Update all available analyses
    if 'tenth' in document_analyses:
        summary.certificate_tenth = document_analyses['tenth']
        try:
            cgpa = float(document_analyses['tenth'].get("cgpa", 0))
            percentage = float(document_analyses['tenth'].get("percentage", 0))
            if cgpa > 0:
                summary.cgpa = cgpa
            if percentage > 0:
                summary.percentage = percentage
        except (ValueError, AttributeError):
            pass

    if 'inter' in document_analyses:
        summary.certificate_inter = document_analyses['inter']
        try:
            cgpa_12 = float(document_analyses['inter'].get("cgpa", 0))
            percentage_12 = float(document_analyses['inter'].get("percentage", 0))
            if cgpa_12 > summary.cgpa:
                summary.cgpa = cgpa_12
            if percentage_12 > summary.percentage:
                summary.percentage = percentage_12
        except (ValueError, AttributeError):
            pass

    if 'disability' in document_analyses:
        summary.certificate_disability = document_analyses['disability']
    
    if 'sports' in document_analyses:
        summary.certificate_sports = document_analyses['sports']

    summary.save()

def process_user_documents():
    users_with_documents = User.objects.filter(
        documents__isnull=False
    ).exclude(document_summary__isnull=False)

    for user in users_with_documents:
        try:
            user_docs = UserDocuments.objects.get(user=user)
            document_analyses = {}

            # Process all available documents
            document_fields = {
                'certificate_tenth': 'tenth',
                'certificate_inter': 'inter',
                'certificate_disability': 'disability',
                'certificate_sports': 'sports'
            }

            for field, doc_type in document_fields.items():
                document = getattr(user_docs, field)
                if document:
                    try:
                        text = process_pdf_with_langchain(document.path)
                        document_analyses[doc_type] = analyze_academic_document(text, doc_type)
                    except Exception as e:
                        print(f"Error processing {doc_type} document for user {user.id}: {str(e)}")
                        continue

            if document_analyses:  # Only save if we have any successful analyses
                save_document_summary(user, document_analyses)

        except Exception as e:
            print(f"Error processing documents for user {user.id}: {str(e)}")
            continue

if __name__ == "__main__":
    process_user_documents()