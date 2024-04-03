from llama_index.core.query_pipeline import QueryPipeline as QP, Link, InputComponent
from llama_index.core.query_engine.pandas import PandasInstructionParser
from llama_index.llms.gemini import Gemini
from llama_index.core import PromptTemplate
from dotenv import load_dotenv
import pandas as pd
import os

# Load environment variables
load_dotenv()

def run_query(query_str):
    # Assuming the hotel.csv is already available and formatted correctly
    df = pd.read_csv("./data/hotel.csv")

    # Load Google API Key from environment variables
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Ensure that the API key is not None or empty
    if not GOOGLE_API_KEY:
        raise ValueError("Google API Key not found in environment variables.")

    # General setup for your query pipeline that doesn't need to be repeated for each query
    pandas_output_parser = PandasInstructionParser(df)
    llm = Gemini(model="models/gemini-pro")

    # These are the parts that depend on the query and might change for each call
    instruction_str = (
        "1. Convert the query to executable Python code using Pandas.\n"
        "2. If the output is null or empty, please try to get the nearest or matching data.\n"
        "3. The final line of code should be a Python expression that can be called with the `eval()` function.\n"
        "4. The code should represent a solution to the query.\n"
        "5. PRINT ONLY THE EXPRESSION.\n"
        "6. Do not quote the expression.\n"
    )
    pandas_prompt_str = (
        "You are working with a pandas dataframe in Python.\n"
        "The dataframe contains information about hotels.\n"
        "You have to take a query and convert it into executable Python code using Pandas.\n"
        "The name of the dataframe is `df`.\n"
        "This is the result of `print(df.head())`:\n"
        "{df_str}\n\n"
        "Follow these instructions:\n"
        "{instruction_str}\n"
        "Query: {query_str}\n\n"
        "Expression:"
    )
    response_synthesis_prompt_str = (
        "Given an input question, synthesize a response from the query results.\n"
        "Query: {query_str}\n\n"
        "Pandas Instructions (optional):\n{pandas_instructions}\n\n"
        "Pandas Output: {pandas_output}\n\n"
        "Response: "
    )
    
    pandas_prompt = PromptTemplate(pandas_prompt_str).partial_format(
        instruction_str=instruction_str, df_str=df.head(5).to_string()
    )
    response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str)
    
    qp = QP(
        modules={
            "input": InputComponent(),
            "pandas_prompt": pandas_prompt,
            "llm1": llm,
            "pandas_output_parser": pandas_output_parser,
            "response_synthesis_prompt": response_synthesis_prompt,
            "llm2": llm,
        },
        verbose=True,
    )
    
    qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"])
    qp.add_links([
        Link("input", "response_synthesis_prompt", dest_key="query_str"),
        Link("llm1", "response_synthesis_prompt", dest_key="pandas_instructions"),
        Link("pandas_output_parser", "response_synthesis_prompt", dest_key="pandas_output"),
    ])
    # Add link from response synthesis prompt to llm2
    qp.add_link("response_synthesis_prompt", "llm2")
    
    response = qp.run(query_str=query_str)
    return response
