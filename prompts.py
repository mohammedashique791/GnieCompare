def converting_to_correct_output(data):
    return f"""
    - You are an intelligent human who knows about different types of products, companies and everything exist in this world and know what are the different attributes the product or companies or whatever the item have.
    - Translate the following data into a structured format. For each product, return a dictionary that contains the product name and price, along with any other relevant attributes such as RAM, processor, battery, etc. for electronic products. If user searches any products other than electronics, you must identify what are the attributes the product has like a human think, depending on the product type Add also the url from which the data is obtained and name it as Reference . Ensure each product has a "product_name" and "Price" field at a minimum and if no data found for a specific field, write No Data Found in it. Ensure you extract details from every url you identify. Right now iam not getting few webistes details. I dont want that. I want every website comparison data . This is strict.
    - If the data is related to food items, for each food item, return a dictionary that contains food name and price, along with other relevant attributes such as Hotel Name, location, category, ingredients.
    - If the data is related to ai models, return a dictionary with key as the name of the large language model company and value as a dictionary which contains free_model_name which includes free version details (price/token) or N/A, enterprise_model_name which contains enterprise name or N/A, pricing_details which contains enterprise_version details(price/token) or N/A, and a reference which contains the url from the information is obtained.
    - If data is related to some other topics, identify the relevant attributes of that topic and return a dictionary with key name as the items extracted from the topic and if every items have a specific attribute and the data in it is no data found, dont include that attribute for the item. eg: RAM: No data Found for every item, remove the attribute RAM. 
    - If ther user specifies condition for some attributes(eg: below price range of 500), then extract only those products which satisfy this conditions with above conditions.
    - Ensure you create dictionary with each urls with extracted details. i want product dictionary with every urls. This is very strict. i dont want response without this.
    - "Please provide pricing and token limit details for AI models in a structured manner. For each model, include both the free and enterprise versions. If a version doesn't exist, use 'N/A' for its price and token limit. The response should contain:

    - The model name.
    - Free version details: price and token limit (use 'N/A' if unavailable).
    - Enterprise version details: price and token limit (use 'N/A' if unavailable).
    - Cover all the models and return in this format . only return the response.
    - Model Name: <model name>
    - Free Version:
    - Price: <price or 'N/A'>
    - Token Limit: <limit or 'N/A'>
    - Enterprise Version:
    - Price: <price or 'N/A'>
    - Token Limit: <limit or 'N/A'>"
    - Every dictionary in the list should have the same keys because this data is used to create a excel file, if you give me different keys, then error will be occured while creating the excel file. This is very strict.
    - return as list of dictionaries. Follow this strictly.
    - If the data is incomplete or the list is truncated, ensure to return the list fully closed with no missing brackets.
    - Return the result strictly as a list of dictionaries. Avoid including explanations.
    - i want only the response which is a list of dictionaries (dont return as json). 
    - Please provide the response as a plain list of dictionaries. Do not include any code formatting like json or python. i need the ouput to be ready for direct use in json.loads. This is very strict. Always ensure this while returning the response.
    Data:
    {data}
    """

def main_prompt(user_input, n_models):
    return f"""
    Translate the following instruction into web automation actions:
    Instruction: {user_input}.
    - You are an AI assistant designed to help users find and compare specific products. When given a query about products to compare, provide a list of accurate and original URLs from reputable websites where users can find detailed information on those products. Ensure the URLs lead to pages that show prices, specifications, and comparisons for each specific products.
    - For example, if a user asks to compare shirts, laptops, or any products, include URLs from well-known e-commerce or review sites which is available in india like Amazon, flipkart etc., along with relevant product names and additional useful information. The urls should only be in the url not in outside.
    - If user asks to compare foods, or any item related to it, include URLs from well known food ordering sites which is available in india along with relevant food names and additional useful information. The urls should only be in the url not in outside
    - Provide atleaset {n_models} original urls that a human might go.
    - When a user requests a comparison, identify and extract the original URLs based on the specified product type.
    - For comparing any item (shirts, electronics, etc.), use the command "compare" and extract key details for comparison and no of urls inside details should be {n_models}. I dont want "url" key.
    - If user query specifies ai models or anything related to that, use the command "compare" i dont want a webiste url. strictly make the details list as the top famous {n_models} language model companies and add 'pricing site' with each element, eg: "details": [company1 pricing site, company 2 pricing site] and dont want "url" in this case.
    - If the user specifies about websites to look for a product, identify and add only the correct url of that websites in the details. i dont want other website urls. This is strict.
    - Ensure that the Excel fields for each comparison are created dynamically based on the item type.
    Response should include:
    [
        {{
            "command": "navigate",
            "details": ["url": "https://www.example1.com", "url": "https://www.example2.com"]  # This should not be a placeholder
        }}
    ]
    - I only want the response. (dont return as json)
    """