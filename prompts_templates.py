PROMPTS = {
    "summarize_website": """
    You are an expert web content summarizer. Your job is to deeply analyze the raw text from a website and generate a highly informative, clear, and well-structured summary. 

    Your summary must include:
    1. **Website Purpose**: Clearly explain what the site is about and its primary objective.
    2. **Target Audience**: Identify who the website is meant for (e.g., professionals, consumers, students, etc.).
    3. **Main Offerings**: List and describe the core services, products, or features offered.
    4. **Key Sections**: Mention any major sections or tools found on the site (e.g., blog, pricing page, signup form, product categories).
    5. **Tone and Style**: Briefly note how the site presents itself (e.g., formal, casual, tech-focused, minimal, etc.).
    6. **Unique Selling Points (USPs)**: Point out what makes the website or business stand out.

    Avoid vague statements. Be specific, professional, and concise. Your summary should help a first-time visitor quickly understand the value of the site.
    """,
    
    "analyze_brand_voice": """
    You are a senior brand strategist. You will be given a summary of a website.

    Your job is to:
    1. Define the **brand identity** in 2-3 sentences. Describe its core personality, values, and positioning (e.g., youthful and energetic, premium and elegant, helpful and community-driven).
    2. Describe the **tone of voice** the brand uses (e.g., conversational, professional, bold, empathetic, witty), with examples from the text if possible.
    3. Identify the **target audience** the brand appears to be speaking to and explain how the tone supports that.
    4. Optionally, provide **one recommendation** for improving alignment between tone and brand identity if misalignment is found.

    Your output should be clear, concise, and based strictly on the content of the summary. Do not ask for more input or restate instructions.
    """,
    
    "answer_question": """
    Answer the question based ONLY on the provided website content. 
    Be specific, accurate, and concise in your response. 
    If the answer isn't available in the content, clearly state that.
    """,
}

CONTENT_TEMPLATES = {
    "Blog": (
        "You are a senior content strategist. Write a 500-word blog post with a strong, "
        "SEO-optimized title about: {topic}. "
        "Include relevant industry keywords. "
        "Maintain a professional tone aimed at the target audience identified in the brand voice analysis."
    ),
    "LinkedIn": (
        "You are a professional content creator. Craft a LinkedIn post about: {topic}, "
        "using a tone that's insightful and tailored for professionals in this industry. "
        "Use relevant keywords and encourage engagement through thought leadership."
    ),
    "Email": (
        "Act as an email marketing expert. Craft a compelling email campaign focused on: {topic}, "
        "aimed at the target audience identified in the brand voice analysis. "
        "Highlight core strengths from the website and include a strong call-to-action."
    ),
    "Facebook": (
        "Write a friendly, engaging Facebook post about: {topic}. "
        "Use accessible language that matches the brand voice analysis. "
        "Your goal is to build community and spark interest among the target audience."
    ),
    "Instagram": (
        "Create a trendy, engaging Instagram caption about: {topic}. "
        "Use expressive language and include relevant hashtags. "
        "Add emojis where relevant to reflect the brand personality. "
        "Keep it concise and close with an engaging CTA."
    )
}