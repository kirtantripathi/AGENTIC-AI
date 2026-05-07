import asyncio
from browser_use import Agent, ChatOllama
# from langchain_ollama import ChatOllama  # or from browser_use if they re-export
from pydantic import Field

base_url = ""


async def main():
    llm = ChatOllama(
        model="qwen3-vl:8b",  # Use a vision-capable model like Qwen2-VL
        host=base_url,
        timeout=600
    )

    agent = Agent(
        task="Calculate 8 + 1 using the https://www.calculator.net/scientific-calculator.html website",  # Your goal
        llm=llm,
        use_vision=True,             # This is key — sends screenshots to VLM
        # Additional useful options:
        # max_steps=30,
        # browser_context=...,       # reuse browser across runs
    )

    result = await agent.run()
    print(result)

asyncio.run(main())


# =====================================================================================================================================

# import asyncio
# import base64
# import json
# from playwright.async_api import async_playwright
# from langchain_ollama import ChatOllama
# from langchain_core.messages import HumanMessage

# # --- CONFIG ---
# OLLAMA_MODEL = "qwen3-vl:8b"
# OLLAMA_BASE_URL = "http://122.170.112.23:11434"
# TARGET_SITE = "https://www.calculator.net/scientific-calculator.html"

# llm = ChatOllama(
#     model=OLLAMA_MODEL,
#     base_url=OLLAMA_BASE_URL,
# )

# # --- VLM placeholder ---
# # NOTE: Ollama models are NOT vision-capable (unless using special models like llava)
# # For now, we simulate perception using DOM only

# async def extract_elements(page):
#     elements = await page.evaluate("""
#     () => Array.from(document.querySelectorAll('button, a, input'))
#     .map(el => {
#         const rect = el.getBoundingClientRect();
#         return {
#             label: el.innerText || el.placeholder || "unknown",
#             x: rect.x + rect.width/2,
#             y: rect.y + rect.height/2
#         }
#     })
#     """)
#     return elements


# # --- LLM: decide next action ---
# async def decide_action(goal, elements):
#     prompt = f"""
#     Goal: {goal}

#     Elements:
#     {elements}

#     Return ONLY valid JSON:
#     {{
#         "action": "click" or "type",
#         "label": "...",
#         "text": "..." 
#     }}
#     """

#     response = llm.invoke([HumanMessage(content=prompt)])
#     content = response.content

#     try:
#         return json.loads(content)
#     except:
#         print("Failed to parse:", content)
#         return {"action": "click", "label": elements[0]["label"]}


# # --- Match label ---
# def find_element(label, elements):
#     for el in elements:
#         if label.lower() in el["label"].lower():
#             return el
#     return elements[0] if elements else None


# # --- Main agent loop ---
# async def run_agent(goal):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()

#         await page.goto(TARGET_SITE)

#         for step in range(10):
#             # Stay on site
#             if TARGET_SITE not in page.url:
#                 await page.goto(TARGET_SITE)

#             # 1. Perception (DOM-based)
#             elements = await extract_elements(page)

#             # 2. Decide
#             action = await decide_action(goal, elements)
#             print(f"Step {step}: {action}")

#             # 3. Act
#             target = find_element(action.get("label", ""), elements)
#             if not target:
#                 print("No element found")
#                 continue

#             x, y = target["x"], target["y"]

#             if action["action"] == "click":
#                 await page.mouse.click(x, y)

#             elif action["action"] == "type":
#                 await page.mouse.click(x, y)
#                 await page.keyboard.type(action.get("text", ""))

#             await page.wait_for_timeout(1500)

#         await browser.close()


# # --- Run ---
# asyncio.run(run_agent("Calulate 38 + 10"))