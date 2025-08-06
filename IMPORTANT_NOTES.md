# IMPORTANT IMPLEMENTATION NOTES

## Image Generation Requirements

**🚨 CRITICAL:** NEVER USE DALL-E 3 for image generation

**MUST USE:** OpenAI Responses API with image_generation tool as documented in:
`/Users/jeffreyhacker/AI social media content agent/docs/api-references/openai-image-generation.md`

**Correct API Pattern:**
```python
response = client.responses.create(
    model="gpt-4o-mini",
    input="Generate image prompt",
    tools=[{"type": "image_generation"}]
)
```

**Current Status:** The `client.responses` API is not available in OpenAI library v1.58.1
**Action Required:** Wait for API availability or implement alternative approach

---
*Created: 2025-08-05*