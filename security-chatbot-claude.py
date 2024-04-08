import os
import json
import requests
import streamlit as st
import boto3
import requests
import re


#Initialize bedroc
bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")

def format_markdown(text, topic):
    # Split the text into sections based on the pattern "Section:"
    sections = re.split(r'\nSection:', text)

    # Format the title
    markdown_text = f"# {topic}\n\n"

    # Format the introduction'
    for section in sections[0:]:
        lines = section.strip().split('\n')
        section_title = lines[0]
        section_content = '\n'.join(lines[1:])
        markdown_text += f"{section_content}\n\n"

    # Format the remaining sections
    for section in sections[1:]:
        lines = section.strip().split('\n')
        section_title = lines[0]
        section_content = '\n'.join(lines[1:])
        markdown_text += f"## {section_title}\n\n{section_content}\n\n"

    return markdown_text

def get_cloud_security_insights(topic):
    try:
        prompt_config = {
                                        "anthropic_version": "bedrock-2023-05-31",
                                        "max_tokens": 4096,
                                        "messages": [
                                                        {
                                                            "role": "user",
                                                            "content": [
                                                            {
                                                                "type": "text",
                                                                "text": f"You are an AWS Cloud Security expert with a focus on Cloud Networking and Cloud Infrastructure Security.  You love AWS Network Firewalls and VPC Security among other areas of security.  You code in python.\n\n Teach me about {topic} with code examples and a detalied explanation of all the security terms mentioned. Explain this in a way that a beginner can understand. The output should be similar to a blog post with a summary at the end.  This hould also be presented in a logical order that ties the concepts together. The explaination should include an introduction, an overview of why it's important, a definitaion of key components in the AWS ecosystem, Securiity Terms Explained, a Use case, code examples, and a summary of best practices. You should never include sattements that involve or invoke fear, uncertainty, or doubt (FUD).  We always want to present facts in a manner that empowers and educates.  We never spur one to action using FUD. It should end with a conclusion and the last sentence should say Happy Labbing!."
                                                            }
                                                            ]
                                                        }
                                                    ]
                                }
        body = json.dumps(prompt_config)
        modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
        contentType = "application/json"
        accept = "application/json"
        response = bedrock.invoke_model(
                modelId=modelId,
                contentType=contentType,
                accept=accept,
                body=body
            )
        response_body = json.loads(response.get("body").read())    
        summary = response_body.get("content")[0]["text"]
        return summary
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


def main():
    # Streamlit UI setup
    st.title('AWS AI Cloud Security Instructor')

    topic = st.text_input('Enter a cloud security topic you would like to learn:')
    topic_folder = "topic"
    os.makedirs(topic_folder, exist_ok=True)
    markdown_file = os.path.join(topic_folder, f"{topic}.md")

    # Check if the edition already exists
    if os.path.exists(markdown_file):
        overwrite = st.checkbox("Overwrite existing topic?")
        if overwrite:
            for file_name in os.listdir(topic_folder):
                file_path = os.path.join(topic_folder, file_name)
                os.remove(file_path)
        else:
            st.warning(f"Edition {topic} already exists. Please enter a new topic.")

    if st.button('Teach Me'):
        if topic:
            with st.spinner('Fetching insights...'):
                insights = get_cloud_security_insights(topic)
                st.markdown(insights)
                markdown_formatted = format_markdown(insights, topic)
                with open(markdown_file, "w", encoding="utf-8") as file:
                    file.write(markdown_formatted)
        else:
            st.error('Please enter a topic to continue.')

if __name__ == "__main__":
    main()