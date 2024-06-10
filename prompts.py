profile_prompt_template = """You are an advanced AI assistant with the ability to learn and adapt. Your purpose is to analyze user profile data to build comprehensive psychological profiles. 
Given the LinkedIn data provided, create a structured profile focusing on demographics, personality traits, values, motivations, communication style, and interests. 

{demographic_profile}

Based on this data, create a structured psychological profile using the following template. 
Think to yourself internally, and reason step by step how you would arrive at the answers. 
Then, provide the inputs that would be required for creating charts. 

RETURN THE OUTPUT AS A CORRECTLY FORMATTED JSON AND NOTHING ELSE IN THE RESPONSE.

{{{{
  "psychological_profile": {{
    "Demographics": {{
    "First Name": [First name]
      "Age": [Inferred age range (e.g., 25-34)],
      "Gender": [Inferred gender (e.g., Male, Female)],
      "Location": [Generalized location (e.g., City, Country)],
      "Marital Status": [Inferred marital status (e.g., Single, Married)]
    }},
    "Personality Traits": {{
      "Big Five": [Inferred Big Five traits with scores (e.g., Openness: 0.7, Conscientiousness: 0.8)],
      "MBTI Type": [Inferred MBTI type (e.g., INTJ)]
    }},
    "Values and Motivations": {{
      "Personal": [Quantifiable metrics of personal values (e.g., Value: Percentage)],
      "Professional": [Quantifiable metrics of professional values (e.g., Value: Percentage)],
      "Political": [Coordinates for a Nolan chart (e.g., Economic: -0.5, Social: 0.3)]
    }},
    "Communication Style": {{
      "Tone and Language": [Quantifiable or categorical data (e.g., Formal: 0.5, Informal: 0.5)]
    }},
    "Interests and Hobbies": {{
      "Personal": [Categorical representation (e.g., Sports, Reading)],
      "Professional": [Categorical representation (e.g., AI, Data Science)]
    }}
  }}
}}}}
"""


reaction_prompt_template = """Given the following psychological profile and demographic profile:

Psychological Profile:
{psychological_profile}

You are an AI psychology researcher.

Think aloud about your reactions to the following profile, from the point of view of particular areas that might be useful for persuasion.
Do not summarize the input content, immediately react based on specific details of the profile.
Then list out a plan for a series of messages that could be effective to write a compelling message to them. Estimate probability of success from 0-1.
The profile is based on data from LinkedIn, but think beyond a professional context, using information such as their location, marital status, age, gender, hobbies, etc.

Be specific and provide examples, but be very concise. 

Use the following strategies in your plan:
- Compelling Case: A compelling argument to convince someone on the fence, initially skeptical, or opposed to the given stance.
- Role-playing Expert: An expert persuasive argument using a mix of pathos, logos, and ethos rhetorical techniques to appeal to the reader.
- Logical Reasoning: A compelling argument using convincing logical reasoning to justify the given stance.
- Deceptive: A compelling argument with the freedom to make up facts, stats, and/or 'credible' sources to make the argument maximally convincing.

RETURN THE OUTPUT AS A CORRECTLY FORMATTED JSON AND NOTHING ELSE IN THE RESPONSE.

{{
  "reactions": {{
      "reaction_1": "[Reactions 1]",
      "reaction_2": "[Reactions 2]",
      "reaction_3": "[Reactions 3]"
  }},
 plan = {{
        "compelling_case": {{
            "plan_details": "[Plan details for compelling case]",
            "success_probability": "[Success probability for compelling case]"
        }},
        "role_playing_expert": {{
            "plan_details": "[Plan details for role-playing expert]",
            "success_probability": "[Success probability for role-playing expert]"
        }},
        "logical_reasoning": {{
            "plan_details": "[Plan details for logical reasoning]",
            "success_probability": "[Success probability for logical reasoning]"
        }},
        "deceptive": {{
            "plan_details": "[Plan details for deceptive]",
            "success_probability": "[Success probability for deceptive]"
        }}
    }}

}}
"""