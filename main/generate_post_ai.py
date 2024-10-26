import json
import os

import openai
import requests
from django.core.files.base import ContentFile
from google.ai.generativelanguage_v1beta.types import content
import google.generativeai as genai

from content_chronicle.settings import OPENAI_KEY
from main.models import Workspace, User, PostGenerationSession, Post

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["response"],
        properties={
            "response": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.OBJECT,
                    enum=[],
                    required=[
                        "descr",
                        "cap",
                        "post_time",
                        "img_prompt",
                        "vid_prompt",
                        "assignee_id",
                    ],
                    properties={
                        "descr": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "cap": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "post_time": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "img_prompt": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "vid_prompt": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "assignee_id": content.Schema(
                            type=content.Type.STRING,
                        ),
                    },
                ),
            ),
        },
    ),
    "response_mime_type": "application/json",
}


def generate_posts_ai(
    workspace: Workspace,
    user: User,
    session: PostGenerationSession | None = None,
    custom_instructions: str | None = None,
    range_start: str | None = None,
    range_end: str | None = None,
):
    user_roles = workspace.members.all().values("id", "email", "role")

    system_instruction = (
        "generate the content for professional social media marketing\n"
        f"users: {list(user_roles)}\n"
        f"select assignee for each post based on their roles.\n"
        f"generate multiple posts if there are multiple events, generate at least 3 posts."
    )
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    history = []
    if session is not None:
        session_history = session.history.all().values("prompt", "response")
        history = [
            [
                {"role": "user", "parts": [x["prompt"]]},
                {"role": "model", "parts": [x["response"]]},
            ]
            for x in session_history
        ]
        history = [item for sublist in history for item in sublist]
    chat_session = model.start_chat(history=history)

    prompt = ""
    if custom_instructions:
        prompt += custom_instructions + "\n"
    prompt += (
        f"Generate social media content for date between {range_start} and {range_end}"
    )
    response = chat_session.send_message(prompt)
    return json.loads(response.text), prompt


def regenerate_posts_ai(
    workspace: Workspace,
    prompt: str,
    post: Post,
    session: PostGenerationSession | None = None,
):
    user_roles = workspace.members.all().values("id", "email", "role")
    post_data = {
        "descr": post.description,
        "cap": post.post_text,
        "post_time": post.schedule_time.isoformat(),
        "img_prompt": post.img_prompt,
        "vid_prompt": post.vid_prompt,
        "assignee_id": post.assignee_id,
    }
    system_instruction = (
        f"generate the content for professional social media marketing\n"
        f"users: {list(user_roles)}\n"
        f"select assignee for each post based on their roles.\n"
        f"generate a single post in replacement of the post {post_data}"
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    history = []
    if session is not None:
        session_history = session.history.all().values("prompt", "response")
        history = [
            [
                {"role": "user", "parts": [x["prompt"]]},
                {"role": "model", "parts": [x["response"]]},
            ]
            for x in session_history
        ]
        history = [item for sublist in history for item in sublist]
    chat_session = model.start_chat(history=history)

    response = chat_session.send_message(prompt)
    return json.loads(response.text), prompt


def generate_post_image(post: Post, prompt: str):
    client = openai.Client(api_key=OPENAI_KEY)
    response = client.images.generate(
        model="dall-e-2", prompt=prompt, size="1024x1024", response_format="url", n=1
    )
    img_data = requests.get(response.data[0].url).content
    post.post_image.save(f"{post.id}.png", ContentFile(img_data))
    post.save()
