from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_template("""
You are a cybersecurity expert.

Question: {question}
                                          
if asked questions are simple and can be answered in few words then don't elobrate much                                          

else Explain clearly:
- What it is
- How it works
- Risks
- Prevention
""")


def ask_cyber_ai(question: str):
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return response.content