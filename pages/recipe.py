import streamlit as st
import json
import openai
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    ingredient: str = Field(description="材料", examples=["鶏もも肉"])
    quantity: str = Field(description="分量", examples=["300g"])

class Recipe(BaseModel):
    ingredients: list[Ingredient]
    instrunctions: list[str] = Field(description="手順", examples=[["材料を切ります。", "材料を炒めます。"]])

OUTPUT_RECIPE_TOOLS = {
    "type": "function",
    "function": {
        "name": "output_recipe",
        "description": "レシピを出力する",
        "parameters": Recipe.schema(),   
    }
}

# SAMPLE_JSON = """
# {
#   "ingredients": [
#     {
#       "ingredient": "材料A",
#       "quantity": "1個"
#     },
#     {
#       "ingredient": "材料B",
#       "quantity": "100g"
#     }
#   ],
#   "instrunctions": ["材料を切ります", "材料を炒めます"]
# }
# """

PROMPT_TEMPLATE = """以下の料理のレシピを考えてください。

料理名:{dish}
"""

st.title("レシピ生成AI")

dish = st.text_input(label="料理名")

if dish:
    with st.spinner(text="生成中"):
        messages = [
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(dish=dish),
            }
        ]
        # st.write(messages)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            tools=[OUTPUT_RECIPE_TOOLS],
            tool_choice="auto",
        )
        st.write(response)
        response_message = response.choices[0].message
        tool_call = response_message.tool_calls[0]
        function_args = tool_call.function.arguments

        recipe = json.loads(function_args)

        st.write("## 材料")
        st.table(recipe["ingredients"])

        # 以下の形式のマークダウンの文字列を作成して表示
        # ##手順
        # 1. 材料を切ります。
        # 2. 材料を炒めます。
        instruction_markdown = "## 手順\n"
        for index, instruction in enumerate(recipe["instrunctions"]):
            instruction_markdown += f"{index+1}. {instruction}\n"
        st.write(instruction_markdown)
