import os
import subprocess

import g4f
from tenacity import retry, stop_after_attempt

PROVIDER_MAPPING = {
    'g4f.Provider.AItianhu': g4f.Provider.AItianhu,
    'g4f.Provider.Acytoo': g4f.Provider.Acytoo,
    'g4f.Provider.AiService': g4f.Provider.AiService,
    'g4f.Provider.Aichat': g4f.Provider.Aichat,
    'g4f.Provider.Ails': g4f.Provider.Ails,
    'g4f.Provider.Bard': g4f.Provider.Bard,
    'g4f.Provider.Bing': g4f.Provider.Bing,
    'g4f.Provider.ChatgptAi': g4f.Provider.ChatgptAi,
    'g4f.Provider.ChatgptLogin': g4f.Provider.ChatgptLogin,
    'g4f.Provider.DeepAi': g4f.Provider.DeepAi,
    'g4f.Provider.DfeHub': g4f.Provider.DfeHub,
    'g4f.Provider.EasyChat': g4f.Provider.EasyChat,
    'g4f.Provider.Forefront': g4f.Provider.Forefront,
    'g4f.Provider.GetGpt': g4f.Provider.GetGpt,
    'g4f.Provider.H2o': g4f.Provider.H2o,
    'g4f.Provider.Liaobots': g4f.Provider.Liaobots,
    'g4f.Provider.Lockchat': g4f.Provider.Lockchat,
    'g4f.Provider.Opchatgpts': g4f.Provider.Opchatgpts,
    'g4f.Provider.Raycast': g4f.Provider.Raycast,
    'g4f.Provider.Theb': g4f.Provider.Theb,
    'g4f.Provider.Vercel': g4f.Provider.Vercel,
    'g4f.Provider.Wewordle': g4f.Provider.Wewordle,
    'g4f.Provider.You': g4f.Provider.You,
    'g4f.Provider.Yqcloud': g4f.Provider.Yqcloud,
}
PROVIDER = PROVIDER_MAPPING[os.environ.get('PROVIDER')]


def run_shell_command(command):
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


@retry(stop=stop_after_attempt(12))
def chat_completion(query) -> str:
    return g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
        provider=PROVIDER # select provide which is active
    )


def translate_content(content, output_lang):
    """Use GPT for translation"""
    translate_query = (
        f'翻譯以下 markdown 文本為{output_lang}語言，並且遵循以下規則:\n'
        '1. 保持文本原有格式、符號\n'
        '2. 只需要給我文本翻譯結果，不要有任何描述\n'
        '3. 確切翻譯文本所有內容，留下換行符號\n'
        '4. 以 markdown 程式碼輸出結果:\n'
        '--------------------------------\n'
        f'{content}'
    )
    response = chat_completion(translate_query)

    check_query = (
        '原始問題:\n'
        f'{translate_content}\n'
        '原始回答:\n'
        f'{response}\n'
        '請繼續完成未回答的部分，如果已經完成請回答: ""'
    )
    check_response = chat_completion(check_query)

    if check_response != 'None':
        response = '\n' + check_response

    print(response, '\n', check_response)
    return response


def main():
    git_diff_command = "git diff --name-only HEAD~1 HEAD"
    return_code, stdout, stderr = run_shell_command(git_diff_command)

    if return_code == 0:
        modified_files = stdout.split("\n")
        for file in modified_files:
            if "README" in file:
                output_lang = "en" if "zh-TW" in file else "zh-TW"
                
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()

                translated_content = translate_content(content, output_lang)
                output_file = file.replace(".md", ".zh-TW.md") if output_lang == "zh-TW" else file.replace(".zh-TW", "")

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(translated_content)
                    
                print(f"Translated content written to {output_file}")


if __name__ == "__main__":
    main()