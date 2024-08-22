import gradio as gr
import os
from config import Config
from github_client import GitHubClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG

config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)


def export_progress_by_date_range(repo, days):
    raw_file_path = github_client.export_progress_by_date_range(repo, days)
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)

    return report, report_file_path

def add_option(new_option):
    options = subscription_manager.list_subscriptions()
    options.append(new_option)
    dropdown = gr.Dropdown(
        options, label="订阅列表", info="已订阅GitHub项目"
    )
    return dropdown

def remove_option(option_to_remove):
    options = subscription_manager.list_subscriptions()
    if option_to_remove in options:
        options.remove(option_to_remove)
    dropdown = gr.Dropdown(
        options, label="订阅列表", info="已订阅GitHub项目"
    )
    return dropdown

with gr.Blocks() as demo:
    dropdown = gr.Dropdown(
        subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
    )
    gr.Interface(
        fn=export_progress_by_date_range,
        title="GitHubSentinel",
        inputs=[
            dropdown,
            gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
        ],
        outputs=[gr.Markdown(), gr.File(label="下载报告")],
    )
    new_option_input = gr.Textbox(label="添加新选项")
    add_button = gr.Button("添加选项")
    add_button.click(add_option, inputs=new_option_input, outputs=dropdown)
    remove_option_input = gr.Textbox(label="删除选项")
    remove_button = gr.Button("删除选项")
    remove_button.click(remove_option, inputs=remove_option_input, outputs=dropdown)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))