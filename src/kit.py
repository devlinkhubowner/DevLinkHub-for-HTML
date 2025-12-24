# from . import database#supabase操作用のファイル
import database
import webbrowser#サイトを開く
import httpx
import requests
import inspect#元の関数を取得したりする
import logging#エラー判別用
import datetime
import json
from github import Github,GithubIntegration,GithubException#GNU LESSER GENERAL PUBLIC LICENSE Version 3 github操作用

class supabase():
    def newdata(table,data,column):
        try:
            if column != None:
                response = database.supabase.newdata(table=table,data=data,column=column)
            else:
                response = database.supabase.newdata(table=table,data=data,column=table)
        except database.supabaseError as e:
            logging.warning(e)
            webbrowser.open("https://forms.gle/v9Vvt7rFQtoxE6gh7")
            #TODO 問題報告用サイトを作る

    def allread(table):
        try:
            response = database.supabase.allread(table)
        except database.supabaseError as e:
            logging.warning(e)
            caller = inspect.stack()[1]  
            logging.warning(caller.function)
            webbrowser.open("https://forms.gle/v9Vvt7rFQtoxE6gh7")
        else:
            return response
        
    def searchread(table,search,key):
        try:
            response = database.supabase.searchread(table,search,key)
        except database.supabaseError as e:
            logging.warning(e)
            caller = inspect.stack()[1]  
            logging.warning(caller.function)
            webbrowser.open("https://forms.gle/v9Vvt7rFQtoxE6gh7")
        else:
            return response
        
    def delete(table, number):
        try:
            database.supabase.delete(table=table,id="id",number=number)

        except Exception as e:
            logging.warning(e)
            caller = inspect.stack()[1]
            logging.warning(caller.function)
            webbrowser.open("https://forms.gle/v9Vvt7rFQtoxE6gh7")


    def update(table,data,former,overwrite,column,columneq):
        try:
            if overwrite == True:
                database.supabase.json(table=table,data=data,former=former,overwrite=table,column=column)
            else:
                database.supabase.text(table=table,data=data,former=former,column=column,columneq=columneq)
        except database.supabaseError as e:
            logging.warning(e)
            caller = inspect.stack()[1]  
            logging.warning(caller.function)
            webbrowser.open("https://forms.gle/v9Vvt7rFQtoxE6gh7")

    class ogp():
        def ogp(url):
            response = httpx.get(f"https://ogp-scanner.kunon.jp/v1/ogp_info?url={url}")
            if response.status_code == 200:
                return response

class github():
    def filepass(token,title,searchpass):
        try:
            g = Github(token)
            repo = g.get_repo(title)
            data = repo.get_contents(searchpass)
            return data.decoded_content.decode('utf-8')
        except GithubException as e:
            if e.status == 404:
                print("ファイルは存在しません、またはリポジトリが空です")
                return False
    def repository(appid, key, installation_id):
        # GitHub App として初期化
        integration = GithubIntegration(appid, key)
        # Installation Access Token を発行
        access_token = integration.get_access_token(installation_id).token
        # GitHub API でインストール可能リポジトリを直接取得
        headers = {"Authorization": f"token {access_token}"}
        url = "https://api.github.com/installation/repositories"
        resp = requests.get(url, headers=headers)
        data = resp.json()
        # repositories を順に表示
        repos = []
        for repo in data.get("repositories", []):
            repos.append(repo["full_name"])
        return repos
    def createfile(token, repo_name, update_data,filepass):
        g = Github(token)
        repo = g.get_repo(repo_name)

        new_branch_name = "main"  # 新規作成時のブランチ名

        # 現在のブランチ一覧を取得
        branches = list(repo.get_branches())

        # -------------------------
        # リポジトリが空の場合
        # -------------------------
        if len(branches) == 0:

            repo.create_file(
                path=filepass,
                message="Initial commit",
                content=update_data,
                branch=new_branch_name,
            )

        # -------------------------
        # 既にブランチがある場合
        # -------------------------
        default_branch = repo.default_branch  # main または master を自動取得
        source_branch = repo.get_branch(default_branch)

        # 新しい作業用ブランチがない場合は作る
        try:
            repo.get_branch(new_branch_name)
        except GithubException:
            repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=source_branch.commit.sha)

        # ファイル作成
        try:
            repo.create_file(
                path=filepass,
                message=f"{filepass} を追加",
                content=update_data,
                branch=new_branch_name
            )
        except GithubException as e:
            print(f"ファイル作成に失敗しました: {e}")
    def update(token, repo_name, update_data, filename="message.txt"):
        g = Github(token)
        repo = g.get_repo(repo_name)

        path = filename  # 常に main に置く

        try:
            # 既存ファイル取得
            contents = repo.get_contents(path, ref="main")
            repo.update_file(
                path,
                "update file",
                update_data,
                contents.sha,
                branch="main"
            )
        except Exception:
            # ないなら作成
            repo.create_file(
                path,
                f"create {datetime.datetime.now()}",
                update_data,
                branch="main"
            )
    def read(token, filepass, repo_name):
        from github import Github
        g = Github(token)
        try:
            repo = g.get_repo(repo_name)
            file_content = repo.get_contents(filepass)

            decoded_text = file_content.decoded_content.decode("utf-8")
            sha = file_content.sha  # ← これが update に必須

            return {
                "content": decoded_text,
                "sha": sha
            }

        except Exception as e:
            print(f"エラー: {e}")
            return False
