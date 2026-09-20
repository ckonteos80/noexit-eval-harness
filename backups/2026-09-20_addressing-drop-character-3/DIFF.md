## prompts.py

**`adressingSystemPromptActions`** -- before:
```
- If the user message addresses both characters, reply with "0".
- If the user message addresses character 1, reply with "1".
- If the user message addresses character 2, reply with "2".
- If the user message addresses character 3, reply with "3".

Do not include any additional text, commentary, or explanations.
```
after:
```
- If the user message addresses both characters, reply with "0".
- If the user message addresses character 1, reply with "1".
- If the user message addresses character 2, reply with "2".

Reply with exactly one of those digits and nothing else. Do not include any additional text, commentary, or explanations.
```
