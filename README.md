# 🕷️ Web AI Agent

> Autonomous AI agent that navigates the web and executes tasks described in natural language.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![Playwright](https://img.shields.io/badge/Playwright-automation-green?style=flat)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--Vision-black?style=flat&logo=openai)
![LangChain](https://img.shields.io/badge/LangChain-tools-teal?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat&logo=streamlit)

## How it works
The agent runs a ReAct loop (Reason + Act):
1. Takes a screenshot of the current page
2. GPT-4o Vision analyzes the image and decides the next action
3. Playwright executes the action (click, type, navigate, scroll)
4. Repeats until the task is complete