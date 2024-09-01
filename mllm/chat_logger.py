from __future__ import annotations

import html
import json

from mllm.display.show_html import show_json_table
from mllm.utils.logger import Logger


def get_chat_in_html(message_to_api: list[dict], additional_res: dict):
    res = []
    for entry in message_to_api:
        if isinstance(entry["content"], str):
            entry["content"] = [{"type": "text", "text": entry["content"]}]
        content = []
        for item in entry["content"]:
            if item["type"] == "text":
                text = item["text"]
                text = html.escape(text)
                text = text.replace("\n", "<br/>")
                text = text.replace(" ", "&nbsp;")
                content.append(text)
            elif item["type"] == "image_url":
                content.append("<image src='{}' style='max-height: 200px;'/>".format(
                    item["image_url"]["url"]))
        content = "<br/>".join(content)
        res.append(f"------{entry['role']}------<br/> {content}")
        res.append("""
<style>
details {
  user-select: none;
}

details>summary span.icon {
  width: 24px;
  height: 24px;
  transition: all 0.3s;
  margin-left: auto;
}

details[open] summary span.icon {
  transform: rotate(180deg);
}

summary {
  display: flex;
  cursor: pointer;
  background-color: #f1f1f1;
}

summary::-webkit-details-marker {
  display: none;
}
</style>    
""")
    additional_res_str = json.dumps(additional_res, indent=4)
    additional_res_str = html.escape(additional_res_str)
    res.append(f"""
<details>
  <summary>Additional info</summary>
  <pre>{additional_res_str}</pre>
</details>
""")

    return "<br/>".join(res)


class ChatLogger(Logger):
    active_loggers = []
    def __init__(self, disable=False, save_path=None, show_table=True):
        super().__init__(disable)
        self.save_path = save_path
        self.show_table = show_table


    def display_log(self):
        contents = [get_chat_in_html(message_to_api, additional_res) for message_to_api, additional_res in self.log_list]
        filenames = [caller_name.split("/")[-1] for caller_name in self.caller_list]
        info_list = []
        for i in range(len(contents)):
            content = contents[i]
            info_list.append({
                "filename": filenames[i],
                "content": content
            })
        if self.show_table:
            show_json_table(info_list)
        if self.save_path is not None:
            info_list_for_save = []
            for i in range(len(self.log_list)):
                message_to_api, additional_res = self.log_list[i]
                info_list_for_save.append({
                    "filename": filenames[i],
                    "content": message_to_api,
                    "additional_res": additional_res
                })
            with open(self.save_path, "w") as f:
                f.write(json.dumps(info_list_for_save, indent=4))
